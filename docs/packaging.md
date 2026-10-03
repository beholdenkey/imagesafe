# Source package guidance

ImageSafe uses [melange](https://github.com/chainguard-dev/melange) to build OpenTofu from
its verified release commit. The currently available Wolfi package lagged upstream and
failed the HIGH/CRITICAL vulnerability gate, so this image owns its source package.
Other images use packages maintained by Wolfi.

Mise pins apko and melange. These tasks provide the local signed-package workflow:

```bash
mise run packages:build packages/opentofu.yaml x86_64
mise run packages:test packages/opentofu.yaml x86_64
mise run packages:build packages/opentofu.yaml aarch64
mise run packages:test packages/opentofu.yaml aarch64
mise run images:lock opentofu
mise run images:build opentofu --arch amd64
mise run images:test opentofu --arch amd64
mise run images:scan opentofu --arch amd64
```

A Docker daemon is required. The tasks create a local signing key under `build/keys/`,
write packages and their signed APK indexes under `build/packages/`, and use the public
key when testing the local package. Keys and build output are ignored by Git. Local keys
are development trust anchors; CI keys are ephemeral and scoped to that build run.

The Docker runner may require elevated container privileges. CI runs recipes on
disposable hosted runners with read-only repository permissions. It builds and tests
both architectures, transfers only packages, provenance, and public keys, then resolves
the image lock from those exact signed APKs. The publication job uses that same package
set and lock. Source-image locks are build artifacts rather than committed files because
each run has fresh ephemeral keys and package signatures.

Local cross-architecture builds require a Docker engine configured to run the target
architecture. CI uses native runners.

Update the OpenTofu recipe's `version` and `expected-commit` together after verifying
the upstream release. Keep its Go minor version compatible with upstream `go.mod`.
A stale commit pin fails the checkout rather than silently building different source.

## Recipe practices

- Fetch release archives with `expected-sha256`/`expected-sha512`, or use `git-checkout`
  with a release tag and `expected-commit`. A tag alone is a mutable input.
- Declare the upstream version, APK epoch, description, and SPDX license. Increment the
  epoch when changing packaging without changing the upstream version.
- Keep build dependencies in `environment.contents.packages`. Put runtime dependencies
  in package metadata; use subpackages for headers, docs, or optional features.
- Prefer melange's maintained language/build pipelines over custom download/install scripts.
- Preserve default package linting. Define a `test` pipeline that runs against the packaged
  result in its fresh runtime environment; testing only the source tree misses dependencies.
- Sign packages and indexes. Pass the public key and local repository to apko rather than
  disabling signature verification.
- Set `SOURCE_DATE_EPOCH` when exercising reproducibility. Pinning source and tool versions
  alone does not prove that the build is reproducible; compare independently rebuilt output.

Compile new recipes before building; `mise run check` compiles recipes under `packages/`
for both target architectures. Compilation validates pipeline structure; it does not
replace package builds or runtime tests.

## Compose a local package

Once built and tested, reference the signed local APK repository in an image recipe:

```yaml
contents:
  keyring:
    - https://packages.wolfi.dev/os/wolfi-signing.rsa.pub
    - build/packages/x86_64/melange-x86_64.rsa.pub
    - build/packages/aarch64/melange-aarch64.rsa.pub
  repositories:
    - https://packages.wolfi.dev/os
    - "@local build/packages"
  packages:
    - application@local
```

Build both architectures before generating a multi-architecture apko lock. Local package
artifacts and keys are prerequisites for that lock and cannot be replaced by the
public Wolfi packages. The existing OpenTofu package stage provides this ordering.

## References

- [apko file format](https://github.com/chainguard-dev/apko/blob/main/docs/apko_file.md)
- [melange build file](https://github.com/chainguard-dev/melange/blob/main/docs/BUILD-FILE.md)
- [Verified Git checkout](https://github.com/chainguard-dev/melange/blob/main/docs/PIPELINES-GIT.md)
- [Package test pipelines](https://github.com/chainguard-dev/melange/blob/main/docs/TESTING.md)
- [Package linting](https://github.com/chainguard-dev/melange/blob/main/docs/LINTER.md)
