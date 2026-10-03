# Image authoring

Each `images/<name>/` directory contains an `apko.yaml`, `metadata.yaml`, `README.md`,
and declarative `tests/main.yaml`. Wolfi images also have a committed `apko.lock.json`.
Source packages use an adjacent `melange.yaml`.

Run apko from the repository root. Every recipe includes `images/base/common.yaml`,
which owns accounts, architectures, environment, workspace permissions, and project
annotations. Application images use only their runtime packages and certificates.

Keep Wolfi/glibc packages together. Avoid combining them with Alpine/musl packages.
If an Alpine image is needed, give it separate repositories/keyrings and a supported
stable release.

```yaml
include: images/base/common.yaml
contents:
  keyring:
    - https://packages.wolfi.dev/os/wolfi-signing.rsa.pub
  repositories:
    - https://packages.wolfi.dev/os
  packages:
    - ca-certificates-bundle
    - application
entrypoint:
  command: /usr/bin/application
cmd: --help
annotations:
  org.opencontainers.image.title: Application
  org.opencontainers.image.description: A short description.
  org.opencontainers.image.documentation: https://github.com/owner/application
```

Put the exact APK package name in `metadata.yaml`. The workflow reads the resolved
application version from the lock using yq and jq, checks agreement between architectures,
and passes it to apko's OCI annotations and Docker's metadata action.

Add the image to [.github/image-filters.yaml](../.github/image-filters.yaml) and the
nightly/manual image list in the workflow. The paths-filter action produces the build
matrix. Use `some-with-excludes` so README edits stay outside the image build selection.

## Tests and locks

Add Container Structure Tests for the application command and image entrypoint/CMD.
Shared tests in `images/base/tests.yaml` verify the nonroot user, home, workspace,
and certificates. Test files use Container Structure Tests' version 2 schema.

```bash
mise run images:lock hurl
mise run images:build hurl --arch amd64
mise run images:test hurl --arch amd64
mise run images:scan hurl --arch amd64
```

Repeat runtime tests on an ARM host or rely on the native ARM CI job. Add functional
checks when a version command cannot catch the expected integration failures.
OpenTofu's fixture in `tests/workspace/` exercises initialization and validation.

APK revisions differ from upstream releases. Keep exact dependency versions in the
lock rather than duplicating them in annotations. Nightly/manual builds refresh the
package set; PRs use committed Wolfi locks. Failed resolution, tests, or vulnerability
scans prevent publication.

For signed source packages and per-build locks, see [melange packaging](../docs/packaging.md).
