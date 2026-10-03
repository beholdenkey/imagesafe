# Hurl

Run and test HTTP requests described in plain text with
[Hurl](https://github.com/Orange-OpenSource/hurl). This image contains the Wolfi Hurl
package and its runtime dependencies, runs as nonroot, and uses `/work` for inputs.

```bash
docker run --rm ghcr.io/beholdenkey/imagesafe/hurl:latest --version
docker run --rm -v "$PWD:/work:ro" ghcr.io/beholdenkey/imagesafe/hurl:latest --test requests.hurl
```

Use the image digest for fixed inputs. See [image authoring](../README.md) for local
build/test commands.
