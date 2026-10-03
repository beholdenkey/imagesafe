# ImageSafe

A small container-image showcase built with [apko](https://github.com/chainguard-dev/apko),
[melange](https://github.com/chainguard-dev/melange), and Wolfi packages. The project follows
[Chainguard Images](https://github.com/chainguard-images/images)' per-image configuration
and test layout, using standard tools and GitHub Actions for GHCR delivery.

## Images

| Image                                     | Purpose                     | Package source                                  |
| ----------------------------------------- | --------------------------- | ----------------------------------------------- |
| [hurl](images/hurl/README.md)             | Run and test HTTP requests  | Wolfi                                           |
| [malcontent](images/malcontent/README.md) | Inspect files for malware   | Wolfi                                           |
| [opentofu](images/opentofu/README.md)     | Infrastructure as code      | Verified upstream source, packaged with melange |
| [wolfi-base](images/wolfi-base/README.md) | A nonroot base with a shell | Wolfi                                           |

Images are published to `ghcr.io/beholdenkey/imagesafe/<name>` for `linux/amd64`
and `linux/arm64`. Every image runs as UID/GID 65532 by default, with a writable
`/work` and `/home/nonroot` owned by that account. Nonroot describes the process inside
the image; rootless operation of the container engine is a separate host setting.

## Build and release

Each image owns its `apko.yaml`, `metadata.yaml`, and `tests/`. Wolfi package inputs
are committed in `apko.lock.json`. OpenTofu also owns a `melange.yaml`; its signed
APK package, public keys, provenance, and image lock are generated together for each
build. See [image authoring](images/README.md) and [source packaging](docs/packaging.md).

| Responsibility                                       | Tool                                                                              |
| ---------------------------------------------------- | --------------------------------------------------------------------------------- |
| Select affected images                               | `dorny/paths-filter` and [.github/image-filters.yaml](.github/image-filters.yaml) |
| Install locked tools and run local commands          | mise                                                                              |
| Build signed source packages                         | melange                                                                           |
| Resolve package inputs and build OCI images/SBOMs    | apko                                                                              |
| Check metadata, filesystem, and application commands | Container Structure Tests                                                         |
| Gate HIGH/CRITICAL vulnerabilities                   | Trivy                                                                             |
| Generate publication tags                            | `docker/metadata-action`                                                          |
| Sign image digests and attest the index SBOM         | cosign                                                                            |

PRs build and test both architectures on native GitHub runners. OpenTofu additionally
initializes and validates a provider-free fixture as nonroot with a read-only root
filesystem, disabled network, and dropped capabilities. Publication follows successful
checks on `main`, using the same signed APKs and package locks. SBOMs, test reports,
scan reports, package provenance, and published references are retained for 30 days.

Documentation edits do not rebuild images. Shared build inputs rebuild all images.
Daily and manual runs refresh package locks and rebuild the catalog. OpenTofu's upstream
release version and verified commit are explicit recipe inputs.

Published tags include `latest`, the application version, the full source commit, and
`build-<run-id>`. These tags can move as dependencies are rebuilt; use the image digest
when you need fixed inputs. Workflow version tags and OCI annotations come from the APK
lock rather than a duplicated upstream version.

## Work locally

Install [mise](https://mise.jdx.dev/), clone the repository, then run:

```bash
mise trust .mise/config.toml
mise trust .mise/conf.d/common.toml
mise trust .mise/conf.d/container.toml
mise trust .mise/conf.d/github.toml
mise trust .mise/conf.d/renovate.toml
mise install --locked
mise run setup
mise run check

mise run images:build hurl --arch amd64
mise run images:test hurl --arch amd64
mise run images:scan hurl --arch amd64
```

Mise tasks invoke the tools directly. Build/test tasks expose native mise argument
validation and help; use `mise run images:build --help`. Select `--arch arm64` on an
ARM host. Docker is required for runtime tests and melange package builds. Build both
OpenTofu package architectures before resolving its image lock.

To refresh a Wolfi lock deliberately:

```bash
mise run images:lock hurl
```

[Lefthook](https://lefthook.dev/) loads the Common, GitHub, container, and Renovate
profiles from [Apeiros Common](https://github.com/apeiros-innovations/common).
It uses Common's `main` branch and refreshes every 24 hours through Lefthook's native
remote support. Common currently has no release tags. Mise fragment versions and
tool dependencies are pinned in the project's lockfiles.

## Verify a published image

```bash
cosign verify ghcr.io/beholdenkey/imagesafe/hurl@sha256:<digest> \
  --certificate-identity=https://github.com/beholdenkey/imagesafe/.github/workflows/build.yaml@refs/heads/main \
  --certificate-oidc-issuer=https://token.actions.githubusercontent.com

cosign verify-attestation ghcr.io/beholdenkey/imagesafe/hurl@sha256:<digest> \
  --type spdxjson \
  --certificate-identity=https://github.com/beholdenkey/imagesafe/.github/workflows/build.yaml@refs/heads/main \
  --certificate-oidc-issuer=https://token.actions.githubusercontent.com
```

Use the published multi-architecture index digest for the index SBOM attestation.
A clean vulnerability scan reflects the database and package inputs available at that
time. Minimal images and regular rebuilds reduce exposure; they cannot guarantee an
absence of vulnerabilities. Review [SECURITY.md](.github/SECURITY.md) for reporting.
