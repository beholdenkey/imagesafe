<div align="center">

## ImageSafe

_An opinionated collection of secure container images that eliminate CVEs from the start_

</div>

<div align="center">

![GitHub Repo stars](https://img.shields.io/github/stars/beholdenkey/image-safe?style=for-the-badge)
![GitHub forks](https://img.shields.io/github/forks/beholdenkey/image-safe?style=for-the-badge)

</div>

Welcome to ImageSafe, if looking for a container start by [browsing the GitHub Packages page for this repo's packages](https://github.com/beholdenkey?tab=packages&repo_name=image-safe).

## Goals

The goal of this project is to provide [semantically versioned](https://semver.org/), [rootless](https://rootlesscontaine.rs/), [multiple architecture](https://www.docker.com/blog/multi-arch-build-and-images-the-simple-way/) and [Common Vulnerabilities and Exposures (CVE)-free](https://cve.mitre.org/) container images.

It also uses tools such as [apko](https://github.com/chainguard-dev/apko) to build Open Container Initiative (OCI) images from Alpine Package Keeper (APK) packages directly without a Dockerfile. In addition to using [Melange](https://github.com/chainguard-dev/melange) to build APK packages from source. All images are built on either a [Wolfi](https://github.com/wolfi-dev) or [Alpine Linux](https://www.alpinelinux.org/) base image.

> [!NOTE]
> This project is intended to be used as a way to share the container images I use in my other projects.
