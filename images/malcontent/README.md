# malcontent

Inspect files for malware with [malcontent](https://github.com/chainguard-dev/malcontent).
This image packages the Wolfi CLI and its runtime dependencies with a nonroot default
user and `/work` workspace.

```bash
docker run --rm ghcr.io/beholdenkey/imagesafe/malcontent:latest --help
```

Mount input files under `/work` and select the command shown by the CLI. Use image
digests when you need fixed package inputs. See [image authoring](../README.md).
