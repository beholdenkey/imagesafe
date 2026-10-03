"""Build and test the catalog with the same commands locally and in CI."""

import argparse
import datetime
import fnmatch
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
ARCHITECTURES = {"amd64": "x86_64", "arm64": "aarch64"}


def run(*args, capture=False, env=None):
    result = subprocess.run(
        args, cwd=ROOT, check=True, text=True, capture_output=capture, env=env
    )
    return result.stdout.strip() if capture else None


def catalog():
    data = json.loads((ROOT / "images/catalog.json").read_text())
    for name, entry in data.items():
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", name):
            raise ValueError(f"Invalid image name: {name}")
        if not isinstance(entry["smoke"], list) or not all(
            isinstance(arg, str) for arg in entry["smoke"]
        ):
            raise ValueError(f"Invalid smoke command: {name}")
        if not (ROOT / f"images/{name}/apko.yaml").is_file():
            raise ValueError(f"Missing recipe for {name}")
    recipes = {p.parent.name for p in (ROOT / "images").glob("*/apko.yaml")}
    if set(data) != recipes:
        raise ValueError("Every image recipe must have a catalog entry")
    return data


def select_images(names, paths, force=False):
    """Shared build inputs fan out; image inputs affect only that image."""
    if force:
        return sorted(names)
    shared = (
        "images/base/", ".mise/", "scripts/", "tests/",
        ".github/workflows/build.yaml",
    )
    if any(p == "images/catalog.json" or p.startswith(shared) for p in paths):
        return sorted(names)
    # Source recipe changes rebuild their image and package.
    source_images = set(names) & {"opentofu"} if any(p.startswith("packages/") for p in paths) else set()
    return sorted(source_images | {
        name for name in names
        if any(p.startswith(f"images/{name}/") and not p.endswith(".md") for p in paths)
    })


def matrix(base, force):
    data = catalog()
    if base and not force and base != "0" * 40:
        # NUL separators preserve filenames containing spaces or newlines.
        paths = run("git", "diff", "--name-only", "-z", base, "HEAD", capture=True).split("\0")
    else:
        paths, force = [], True
    names = select_images(data, paths, force)
    images = {"include": [{"name": name} for name in names]}
    builds = {"include": [
        {"name": name, "arch": arch, "runner": runner}
        for name in names
        for arch, runner in (("amd64", "ubuntu-24.04"), ("arm64", "ubuntu-24.04-arm"))
    ]}
    packages = {"include": [
        {"name": name, "recipe": data[name]["recipe"], "arch": apk_arch, "runner": runner}
        for name in names if "recipe" in data[name]
        for apk_arch, runner in (("x86_64", "ubuntu-24.04"), ("aarch64", "ubuntu-24.04-arm"))
    ]}
    outputs = {"images": json.dumps(images), "builds": json.dumps(builds),
               "packages": json.dumps(packages), "package_count": str(len(packages["include"])),
               "count": str(len(names))}
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as out:
            for key, value in outputs.items():
                out.write(f"{key}={value}\n")
    print(json.dumps(outputs))


def recipe(name):
    if name not in catalog():
        raise ValueError(f"Unknown image: {name}")
    return f"images/{name}/apko.yaml", f"images/{name}/apko.lock.json"


def lock(name):
    names = catalog() if name == "all" else [name]
    for item in names:
        config, locked = recipe(item)
        run("apko", "lock", config, "--output", locked)
        (ROOT / locked).chmod(0o644)


def version(name):
    _, locked = recipe(name)
    if not (ROOT / locked).exists() and "recipe" in catalog()[name]:
        package_version = run("melange", "package-version", catalog()[name]["recipe"], capture=True)
        return package_version.removeprefix(catalog()[name]["package"] + "-").rsplit("-r", 1)[0]
    data = json.loads((ROOT / locked).read_text())
    package = catalog()[name]["package"]
    packages = [p for p in data["contents"]["packages"] if fnmatch.fnmatchcase(p["name"], package)]
    if {p["architecture"] for p in packages} != set(ARCHITECTURES.values()):
        raise ValueError(f"{name}: application package missing on one architecture")
    versions = {p["version"].rsplit("-r", 1)[0] for p in packages}
    if len(versions) != 1:
        raise ValueError(f"{name}: application versions differ between architectures")
    return versions.pop()


def annotations(name):
    revision = run("git", "rev-parse", "HEAD", capture=True)
    return ["--annotations", f"org.opencontainers.image.version:{version(name)},"
            f"org.opencontainers.image.revision:{revision}"]


def build_env():
    env = os.environ.copy()
    env["SOURCE_DATE_EPOCH"] = run("git", "show", "-s", "--format=%ct", "HEAD", capture=True)
    return env


def output_dir(name, arch):
    return ROOT / f"build/{name}/{arch}"


def image_tag(name, arch):
    return f"imagesafe/{name}:test-{arch}"


def build(name, arch):
    config, locked = recipe(name)
    out = output_dir(name, arch)
    out.mkdir(parents=True, exist_ok=True)
    # apko appends -<architecture> to Docker archive tags.
    run("apko", "build", config, f"imagesafe/{name}:test", str(out / "image.tar"),
        "--arch", arch, "--lockfile", locked, "--sbom-path", str(out),
        "--cache-dir", str(ROOT / ".cache/apko"), *annotations(name), env=build_env())


def test(name, arch):
    recipe(name)
    run("docker", "load", "--input", str(output_dir(name, arch) / "image.tar"))
    tag = image_tag(name, arch)
    info = json.loads(run("docker", "image", "inspect", tag, capture=True))[0]
    if info["Architecture"] != arch:
        raise ValueError("Loaded image has the wrong architecture")
    if info["Config"]["User"] not in ("nonroot", "65532", "65532:65532"):
        raise ValueError("Image must run as nonroot by default")
    common = ["docker", "run", "--rm", "--read-only", "--network=none",
              "--cap-drop=ALL", "--security-opt=no-new-privileges", "--tmpfs", "/tmp"]
    run(*common, tag, *catalog()[name]["smoke"])
    if name == "opentofu":
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            work.chmod(0o777)
            (work / "main.tf").write_text('output "message" { value = "imagesafe" }\n')
            mount = ["--mount", f"type=bind,src={directory},dst=/work"]
            run(*common, *mount, tag, "init", "-backend=false", "-input=false")
            run(*common, *mount, tag, "validate")


def scan(name, arch):
    recipe(name)
    run("trivy", "image", "--input", str(output_dir(name, arch) / "image.tar"),
        "--scanners", "vuln", "--severity", "HIGH,CRITICAL", "--exit-code", "1",
        "--format", "json", "--output", str(output_dir(name, arch) / "trivy.json"))


def publish(name, registry):
    config, locked = recipe(name)
    if not registry or not re.fullmatch(r"[a-z0-9][a-z0-9./_-]*", registry):
        raise ValueError("Set IMAGE_REGISTRY, e.g. ghcr.io/beholdenkey/imagesafe")
    out = ROOT / f"build/{name}/publish"
    out.mkdir(parents=True, exist_ok=True)
    repository = f"{registry}/{name}"
    revision = run("git", "rev-parse", "HEAD", capture=True)
    # A run-specific tag also distinguishes daily rebuilds of the same source commit.
    build_id = os.environ.get("GITHUB_RUN_ID", datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d%H%M%S"))
    tags = [f"{repository}:latest", f"{repository}:{revision}",
            f"{repository}:build-{build_id}", f"{repository}:{version(name)}"]
    run("apko", "publish", config, *tags, "--lockfile", locked,
        "--sbom-path", str(out), "--image-refs", str(out / "image-refs.txt"),
        "--cache-dir", str(ROOT / ".cache/apko"), *annotations(name), env=build_env())


def validate():
    for name in catalog():
        config, locked = recipe(name)
        # Source-image keyrings are generated by the package jobs. Their apko
        # configuration is checked by the subsequent lock/build commands.
        if "recipe" not in catalog()[name]:
            run("apko", "show-config", config, capture=True)
        version(name)
        if (ROOT / locked).exists():
            data = json.loads((ROOT / locked).read_text())
            if data["config"]["name"] != config:
                raise ValueError(f"{locked}: wrong config path")
    for config in (ROOT / "packages").glob("*.yaml"):
        for arch in ARCHITECTURES.values():
            run("melange", "compile", str(config), "--arch", arch, capture=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["list", "matrix", "lock", "build", "test", "scan", "publish", "validate"])
    parser.add_argument("name", nargs="?", default="all")
    parser.add_argument("--arch", choices=ARCHITECTURES, default="amd64")
    parser.add_argument("--base", default=os.environ.get("BASE_SHA", ""))
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--registry", default=os.environ.get("IMAGE_REGISTRY", ""))
    args = parser.parse_args()
    if args.command == "list":
        print("\n".join(catalog()))
    elif args.command == "matrix":
        matrix(args.base, args.all or os.environ.get("FORCE_ALL") == "true")
    elif args.command == "lock":
        lock(args.name)
    elif args.command == "validate":
        validate()
    elif args.command == "publish":
        publish(args.name, args.registry)
    else:
        {"build": build, "test": test, "scan": scan}[args.command](args.name, args.arch)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        if isinstance(error, subprocess.CalledProcessError) and error.stderr:
            print(error.stderr, file=sys.stderr)
        print(error, file=sys.stderr)
        sys.exit(1)
