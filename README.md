# ImageSafe

[![Build](https://github.com/beholdenkey/imagesafe/actions/workflows/build.yaml/badge.svg)](https://github.com/beholdenkey/imagesafe/actions/workflows/build.yaml)

ImageSafe is my container supply chain showcase: declarative images, package locks,
nonroot execution, native architecture tests, vulnerability reports, and signed releases.
The images are tools I use in my own infrastructure and development projects.

## Images

| Image                                      | Entrypoint      | Purpose                |
| ------------------------------------------ | --------------- | ---------------------- |
| `ghcr.io/beholdenkey/imagesafe/hurl`       | `/usr/bin/hurl` | HTTP request testing   |
| `ghcr.io/beholdenkey/imagesafe/malcontent` | `/usr/bin/mal`  | Malware discovery      |
| `ghcr.io/beholdenkey/imagesafe/opentofu`   | `/usr/bin/tofu` | Infrastructure as code |
| `ghcr.io/beholdenkey/imagesafe/wolfi-base` | `/bin/sh`       | Interactive Wolfi base |

Every image supports `linux/amd64` and `linux/arm64` and selects UID/GID 65532 by default.
The application images contain their application, certificate bundle, and resolved
runtime dependencies. OpenTofu is built from verified source with melange; the other
images use packages maintained by Wolfi. Only `wolfi-base` deliberately includes a shell and package manager.

Use `latest` for a rolling release, an application version for that release's latest
rebuild, or a digest for an immutable deployment. A `build-<GitHub run ID>` tag identifies
each publication; the source commit tag can move when nightly rebuilds refresh packages.
Application-version tags are derived from the APK lock rather than handwritten metadata.

```bash
docker run --rm ghcr.io/beholdenkey/imagesafe/hurl:latest --version

docker run --rm --mount type=bind,src="$PWD",dst=/work \
  ghcr.io/beholdenkey/imagesafe/opentofu:latest version
```

Bind-mounted workspaces must be accessible to UID 65532. Image-level nonroot execution
is separate from running a rootless container engine.

## How the pipeline works

[apko](https://github.com/chainguard-dev/apko) composes OCI images from signed Wolfi APKs.
The committed `apko.lock.json` files record exact package versions and checksums for both
architectures of Wolfi-only images. OpenTofu first builds signed APKs from the pinned
release commit on native runners, tests the packages, and generates a per-run image lock.
Each package job uses an ephemeral signing key; only the public keys leave that job. Pull requests and main-branch changes use these locks. Nightly and manual
main-branch rebuilds resolve fresh locks so application and operating-system fixes are
picked up even when no image recipe changes. The source-built OpenTofu version remains
pinned in its melange recipe and needs an explicit release update. These refreshed locks are retained as build
artifacts; the workflow does not commit them back to the repository.

1. Validate recipes, tooling, GitHub Actions, and build selection. Build and test local
   source packages when the selected image needs them.
2. Build changed images on native AMD64 and ARM64 runners using the same resolved locks.
3. Test each image with a read-only filesystem, no network, no capabilities, and no new privileges.
4. Scan each image with Trivy; HIGH or CRITICAL findings block publication.
5. Publish on `main`, sign architecture and index digests with keyless Cosign, and attest the index SBOM.

Build artifacts retain package locks, SPDX SBOMs, scan results, and published digest
references for 30 days. Documentation edits do not rebuild images. Shared recipe,
build-script, and toolchain changes rebuild every image. An existing registry tag never
causes a changed image to be skipped.

The pipeline uses hosted runners for pull requests and grants registry-write and OIDC
permissions only to the publication job. Publication waits for all selected image tests
and project validation to pass.

## Development

Install [mise](https://mise.jdx.dev/) and Docker, then:

```bash
mise trust .mise/config.toml
mise install --locked
mise run setup
mise run check
mise run images:list
mise run images:build hurl --arch amd64
mise run images:test hurl --arch amd64
mise run images:scan hurl --arch amd64
```

For OpenTofu, build the local packages for both architectures and generate its lock
before building the image; see [source package guidance](docs/packaging.md).

Mise owns tool versions and tasks. Lefthook loads the Common, GitHub, Container, and
Renovate profiles from a pinned commit of
[Apeiros Common](https://github.com/apeiros-innovations/common). Their matching Mise
fragments live in `.mise/conf.d/`; project overrides live in `.mise/config.toml`.
Docker is an external prerequisite, not installed by mise.

To refresh and review the checked-in APK inputs:

```bash
mise run images:lock hurl
mise run images:build hurl --arch amd64
mise run images:test hurl --arch amd64
mise run images:scan hurl --arch amd64
git diff -- images/hurl/apko.lock.json
```

After updating tool definitions, run `mise lock` and commit `.mise/mise.lock`.
Common has no release tags at the selected revision; update its pinned SHA and copied
Mise fragments together. The setup task seeds Lefthook’s remote cache at that SHA because
Lefthook’s initial `git clone --branch` supports branch/tag names rather than commit hashes. The local hook covers the `.mise` paths while Common's current
Mise hook matches `.config/mise`.

See [image authoring](images/README.md) and [source package guidance](docs/packaging.md).

## Verify a published image

Substitute a digest from a successful Build run:

```bash
cosign verify \
  --certificate-identity 'https://github.com/beholdenkey/imagesafe/.github/workflows/build.yaml@refs/heads/main' \
  --certificate-oidc-issuer 'https://token.actions.githubusercontent.com' \
  ghcr.io/beholdenkey/imagesafe/hurl@sha256:<digest>

cosign verify-attestation --type spdxjson \
  --certificate-identity 'https://github.com/beholdenkey/imagesafe/.github/workflows/build.yaml@refs/heads/main' \
  --certificate-oidc-issuer 'https://token.actions.githubusercontent.com' \
  ghcr.io/beholdenkey/imagesafe/hurl@sha256:<digest>
```

A vulnerability scan is evidence at a point in time. It cannot guarantee that an image
has no vulnerabilities or that future advisories will not affect it. See the
[security policy](.github/SECURITY.md) for reporting and rebuild behavior.

Licensed under [Apache-2.0](LICENSE).
