# Image authoring

Each `images/<name>/apko.yaml` includes `images/base/common.yaml`. Run apko from the
repository root: include paths are relative to that working directory.
The shared configuration owns nonroot accounts, architectures, environment,
workspace permissions, and project metadata.

Use Wolfi packages for the current image catalog. Keep application images minimal;
do not add `wolfi-base` just to obtain a shell. Avoid combining Wolfi/glibc and
Alpine/musl packages in one image. If an Alpine image is needed later, give it its own
repository/keyring configuration and choose a supported stable release rather than edge.

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

Add a matching `images/catalog.json` entry with the APK package name and smoke-test
arguments. A package glob handles Wolfi's versioned package names, such as `opentofu-*`.
The helper rejects application-version differences between architectures.

Do not duplicate an upstream version in an OCI annotation or pin an upstream GitHub
release as though it were an APK version. APK releases include packaging revisions;
package availability can lag upstream releases. The APK lock is the version source.
Refresh it with `mise run images:lock <name>` and test both target architectures.

Nightly runs intentionally refresh all packages, including application updates. Consumers
that need change control should use image digests rather than mutable version tags.
A failed lock refresh, smoke test, or vulnerability gate leaves the previously published
images in place. Unsupported architectures must fail instead of silently disappearing.

Every new image needs a useful smoke test. OpenTofu also runs provider-free initialization
and validation in a writable nonroot workspace. Add application-specific functional tests
when a version check is insufficient to catch the integration failures you expect.

For packages that are not available upstream, see [melange packaging](../docs/packaging.md).
