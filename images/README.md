# Images

> [!NOTE]
> This directory contains the configuration files consumed by the build pipeline.

The [Common](../images/base/common.yaml) configuration file is the base configuration file for all images. So all you need to do is include the common configuration file in your image configuration file.

```yaml
include: ../base/common.yaml
contents:
  keyring:
    - https://packages.wolfi.dev/os/wolfi-signing.rsa.pub
  repositories:
    - https://packages.wolfi.dev/os
  packages:

annotations:
  org.opencontainers.image.title: ""
  org.opencontainers.image.description: ""
  org.opencontainers.image.version: ""
  org.opencontainers.image.documentation: ""

entrypoint:
  command:
cmd:
```
