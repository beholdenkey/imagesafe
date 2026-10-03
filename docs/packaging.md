# Source package guidance

ImageSafe packages OpenTofu with [melange](https://github.com/chainguard-dev/melange)
from a verified upstream release commit. The available Wolfi package lagged upstream
and failed the HIGH/CRITICAL vulnerability gate, so this image owns its source package.
Other images use packages maintained by Wolfi.

The recipe lives at `images/opentofu/melange.yaml`. Mise pins the tools, and its tasks
invoke melange and apko directly:

```bash
mise run packages:build images/opentofu/melange.yaml --arch x86_64
mise run packages:test images/opentofu/melange.yaml --arch x86_64
mise run packages:build images/opentofu/melange.yaml --arch aarch64
mise run packages:test images/opentofu/melange.yaml --arch aarch64
mise run images:lock opentofu
mise run images:build opentofu --arch amd64
mise run images:test opentofu --arch amd64
mise run images:scan opentofu --arch amd64
```

Docker is required. The tasks create local signing keys under `build/keys/`, build APKs
and signed indexes under `build/packages/`, and test the result in its runtime
environment. Build both architectures before resolving a multi-architecture image lock.
Local cross-architecture builds require a Docker engine configured for that architecture;
CI uses native runners.

Local development keys and build output are ignored by Git. CI generates ephemeral
keys for each native package job. Only APKs, signed indexes, provenance, and public keys
are transferred to lock/build/publication jobs. The publication job uses those exact
packages and locks. OpenTofu's image lock is a build artifact because each run has
fresh signing keys and package signatures.

The Docker melange runner may require elevated container privileges. Recipes run on
disposable hosted runners with read-only repository permissions. Package testing uses
`melange test`; it checks the installed application rather than just its source tree.

Update the recipe's `version` and `expected-commit` together after verifying the upstream
release. Keep the Go package compatible with upstream `go.mod`. A stale commit pin
fails the checkout.

## Recipe practices

- Fetch archives with `expected-sha256`/`expected-sha512`, or use `git-checkout` with
  both a release tag and `expected-commit`.
- Declare the upstream version, APK epoch, description, and SPDX license. Increment the
  epoch when packaging changes without a new upstream version.
- Keep build dependencies in `environment.contents.packages` and runtime dependencies
  in package metadata. Use subpackages for optional components.
- Prefer melange's maintained build pipelines. Preserve default linting and define
  package runtime tests.
- Sign packages/indexes and pass their public keys to apko.
- Set `SOURCE_DATE_EPOCH` consistently. Compare independent builds before claiming
  reproducibility.

`mise run check` compiles the OpenTofu recipe for both architectures. Compilation checks
pipeline structure; native CI package builds and tests validate the actual result.

## Compose the signed local repository

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
    - imagesafe-opentofu@local
```

## References

- [Chainguard Images layout](https://github.com/chainguard-images/images)
- [apko file format](https://github.com/chainguard-dev/apko/blob/main/docs/apko_file.md)
- [melange build file](https://github.com/chainguard-dev/melange/blob/main/docs/BUILD-FILE.md)
- [Verified Git checkout](https://github.com/chainguard-dev/melange/blob/main/docs/PIPELINES-GIT.md)
- [Package tests](https://github.com/chainguard-dev/melange/blob/main/docs/TESTING.md)
