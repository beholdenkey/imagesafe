# OpenTofu

Run [OpenTofu](https://github.com/opentofu/opentofu) from a minimal image built from a
verified upstream release commit. The adjacent melange recipe builds signed APKs;
apko composes the CLI and certificates into a nonroot image.

```bash
docker run --rm ghcr.io/beholdenkey/imagesafe/opentofu:latest version
docker run --rm --user "$(id -u):$(id -g)" -v "$PWD:/work" \
  ghcr.io/beholdenkey/imagesafe/opentofu:latest init
```

Matching the host user's UID/GID gives the CLI access to a bind-mounted workspace.
The default image user is 65532. Provider installation requires network access; CI
uses a provider-free fixture for its isolated initialization/validation checks.

See [source packaging](../../docs/packaging.md) for local builds and recipe updates.
