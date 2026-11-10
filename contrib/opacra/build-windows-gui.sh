#!/usr/bin/env bash
# Opacra Wallet (GUI): build the Windows zip with Docker, on the PC's Ubuntu (WSL).
#
#   cd /build/opacra-gui && bash contrib/opacra/build-windows-gui.sh
#
# First run: about 1.5-2 hours on a 24-thread PC (it builds the Windows libraries and a static
# Qt once, inside a Docker image that is kept). Later runs: minutes.
# Output: dist/opacra-wallet-gui-v<version>-win-x64.zip and its SHA-256.
set -euo pipefail
export TZ=UTC
cd "$(dirname "$0")/../.."
ROOT=$PWD
IMAGE=opacra-gui:build-env-windows
JOBS=${JOBS:-$(nproc)}

die() { echo "STOP: $*" >&2; exit 1; }

echo "== checks"
command -v docker >/dev/null || die "Docker isn't installed (sudo apt install docker.io)."
docker info >/dev/null 2>&1 || die "Docker isn't running: sudo service docker start"
[ -f monero/src/cryptonote_config.h ] || die "the Opacra core isn't in ./monero"
grep -q 'Opacra' monero/src/cryptonote_config.h || die "./monero is not the Opacra core"
want=$(git rev-parse HEAD:monero)
have=$(git -C monero rev-parse HEAD)
[ "$want" = "$have" ] || die "./monero is at $have, the wallet expects $want (git submodule update)"
[ -z "$(git -C monero status --porcelain --untracked-files=no)" ] || die "./monero has local changes"
VERSION=$(sed -n 's/^set(VERSION_\(MAJOR\|MINOR\|REVISION\) "\([0-9]*\)")$/\2/p' CMakeLists.txt | paste -sd.)
case "$VERSION" in [0-9]*.[0-9]*.[0-9]*) ;; *) die "can't read the version from CMakeLists.txt ('$VERSION')" ;; esac
echo "  Opacra Wallet $VERSION, core $(git -C monero log -1 --format='%h %s')"

echo "== build environment ($IMAGE; cached after the first run)"
CTX=$(mktemp -d)
trap 'rm -rf "$CTX"' EXIT
git -C monero archive HEAD contrib/depends | tar -x -C "$CTX"
mv "$CTX/contrib/depends" "$CTX/depends"; rmdir "$CTX/contrib"
cp docker.gitconfig "$CTX/"
docker build --tag "$IMAGE" --build-arg THREADS="$JOBS" --file contrib/opacra/Dockerfile.windows "$CTX"

echo "== wallet build"
docker run --rm -v "$ROOT":/monero-gui -w /monero-gui -e TZ=UTC -e CMAKE_BUILD_PARALLEL_LEVEL="$JOBS" "$IMAGE" \
  sh -c "make depends root=/depends target=x86_64-w64-mingw32 tag=win-x64; rc=\$?; chown -R $(id -u):$(id -g) build; exit \$rc"

BIN=build/x86_64-w64-mingw32/release/bin
for f in opacra-wallet-gui.exe opacrad.exe; do [ -f "$BIN/$f" ] || die "$BIN/$f was not built"; done
for f in opacra-wallet-gui.exe opacrad.exe; do
  n=$(grep -c -a '/home/' "$BIN/$f" || true)
  [ "$n" = 0 ] || die "$f contains $n /home/ paths"
done

echo "== package"
NAME=opacra-wallet-gui-v$VERSION-win-x64
OUT=dist/$NAME
rm -rf "$OUT" "dist/$NAME.zip"; mkdir -p "$OUT"
cp "$BIN/opacra-wallet-gui.exe" "$BIN/opacrad.exe" start-low-graphics-mode.bat LICENSE "$OUT/"
cp contrib/opacra/README-windows.txt "$OUT/README.txt"
python3 - "$OUT" "dist/$NAME.zip" <<'PY'
import os, sys, zipfile
src, dst = sys.argv[1], sys.argv[2]
base = os.path.basename(src)
with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
    for name in sorted(os.listdir(src)):
        info = zipfile.ZipInfo(base + "/" + name, date_time=(2026, 1, 1, 0, 0, 0))
        info.external_attr = 0o644 << 16
        info.compress_type = zipfile.ZIP_DEFLATED
        with open(os.path.join(src, name), "rb") as f:
            z.writestr(info, f.read())
PY
( cd dist && sha256sum "$NAME.zip" | tee "$NAME.zip.sha256" )
echo "Done: dist/$NAME.zip"
