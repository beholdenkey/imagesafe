"""Bootstrap the pinned Common revision before Lefthook installs its remotes.

Lefthook 2.1 uses git clone --branch for fresh remotes, which cannot clone a SHA.
Seeding its remote cache first allows an immutable pin without a Common release tag.
"""

import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
URL = "https://github.com/apeiros-innovations/common.git"


def run(*args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def main(operation):
    config = (ROOT / ".lefthook.yaml").read_text()
    match = re.search(r"^    ref: ([0-9a-f]{40})$", config, re.MULTILINE)
    if not match or URL not in config:
        raise ValueError("Expected one Common remote pinned to a full commit SHA")
    revision = match.group(1)
    info = Path(run("git", "rev-parse", "--path-format=absolute", "--git-path", "info"))
    remote = info / "lefthook-remotes" / f"common-{revision}"
    if operation == "setup":
        if not (remote / ".git").exists():
            remote.mkdir(parents=True, exist_ok=True)
            run("git", "init", "--quiet", str(remote))
            run("git", "-C", str(remote), "remote", "add", "origin", URL)
            run("git", "-C", str(remote), "fetch", "--depth=1", "origin", revision)
            run("git", "-C", str(remote), "checkout", "--quiet", "--detach", revision)
        run("lefthook", "install")
    if run("git", "-C", str(remote), "rev-parse", "HEAD") != revision:
        raise ValueError("Common remote differs from the pinned revision; rerun setup")
    run("lefthook", "validate")
    merged = json.loads(run("lefthook", "dump", "--format", "json"))
    if not merged.get("commit-msg") or not merged.get("pre-push"):
        raise ValueError("Common hooks were not loaded; run mise run setup")
    print(f"Common {revision}: hooks loaded and validated")


if __name__ == "__main__":
    try:
        if len(sys.argv) != 2 or sys.argv[1] not in {"setup", "check"}:
            raise ValueError("Usage: hooks.py setup|check")
        main(sys.argv[1])
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(error, file=sys.stderr)
        sys.exit(1)
