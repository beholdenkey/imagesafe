# Wolfi base

A [Wolfi](https://github.com/wolfi-dev/os) base image with a shell, certificates, a
nonroot default user, and a writable `/work` workspace.

```bash
docker run --rm -it ghcr.io/beholdenkey/imagesafe/wolfi-base:latest
```

Application-specific images use their required runtime packages directly. This base
is useful when an interactive shell is part of the workload. Use its digest for
fixed inputs. See [image authoring](../README.md).
