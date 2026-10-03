# Security policy

ImageSafe is a personal showcase project. Published images are built from signed Wolfi
packages and a source-built OpenTofu package, run as nonroot by default, and receive daily rebuild attempts. Trivy HIGH and
CRITICAL findings block new publication; this does not remove vulnerabilities from older
images or establish that an image is free of all vulnerabilities.

Use digest references and verify Cosign signatures for deployments that require an
immutable, authenticated artifact. Review the package lock, SPDX SBOM, and scan evidence
in the corresponding successful Build run. If the latest rebuild failed, `latest` may
still reference an older image.

Please use GitHub's private vulnerability reporting for sensitive issues when available.
Otherwise contact the maintainer at `justthered63@gmail.com` before disclosing sensitive
details publicly. Ordinary build failures and package-update requests can be filed as issues.

No support SLA is provided. Contributions that reproduce a failure and include a tested
fix are welcome.
