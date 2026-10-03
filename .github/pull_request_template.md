# Change

Describe the resulting behavior and affected images.

## Validation

Include the exact local commands and results. For recipe changes, include lock refresh,
build, smoke test, and vulnerability scan results for the affected architectures.

```bash
mise run check
mise run images:build <image> --arch amd64
mise run images:test <image> --arch amd64
mise run images:scan <image> --arch amd64
```
