#!/usr/bin/env bash
set -euo pipefail

operation=${1:?Usage: package.sh build|test recipe.yaml [x86_64|aarch64]}
recipe=${2:?Provide a melange recipe}
arch=${3:-$(uname -m)}
case "$arch" in
x86_64 | aarch64) ;;
arm64) arch=aarch64 ;;
*)
	echo "Unsupported architecture: $arch" >&2
	exit 1
	;;
esac

mkdir -p build/keys build/packages
key="$PWD/build/keys/melange-$arch.rsa"
export SOURCE_DATE_EPOCH
SOURCE_DATE_EPOCH=$(git show -s --format=%ct HEAD)
case "$operation" in
build)
	if [[ ! -f $key ]]; then
		melange keygen "$key"
	fi
	melange build "$recipe" --arch "$arch" --runner docker \
		--signing-key "$key" --out-dir "$PWD/build/packages" \
		--source-dir "$(dirname "$recipe")" --generate-provenance
	cp "$key.pub" "$PWD/build/packages/$arch/"
	;;
test)
	melange test "$recipe" --arch "$arch" --runner docker \
		--repository-append "$PWD/build/packages" \
		--keyring-append "$key.pub" --source-dir "$(dirname "$recipe")"
	;;
*)
	echo "Unknown operation: $operation" >&2
	exit 1
	;;
esac
