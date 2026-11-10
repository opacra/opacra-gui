# Opacra Wallet (desktop)

The desktop wallet for [Opacra (OPCA)](https://opacra.org), a private-by-default
proof-of-work cryptocurrency with its own blockchain.

Send, receive and mine OPCA, and prove payments, with the wallet running its own full
Opacra node: the blockchain is downloaded to your computer, so your wallet checks
everything itself and doesn't depend on anyone else's server.

**Download:** [opacra.org](https://opacra.org) (Windows; on Linux, build it from source as
below). Check every download against the signed `SHA256SUMS` on the release page before
running it.

Copyright (c) 2026 The Opacra Project. Portions Copyright (c) 2014-2024 The Monero Project.
BSD-3-Clause, see [LICENSE](LICENSE). This wallet is a fork of the
[Monero GUI](https://github.com/monero-project/monero-gui) v0.18.5.4; its history is kept
below Opacra's own commits.

---

## What is different from the Monero GUI

- Opacra's name, look and units (OPCA; addresses `Pa…`, `Ps…`, `Pi…`), 30-second blocks.
- Runs the Opacra node (`opacrad`, from [opacra/opacra](https://github.com/opacra/opacra),
  included here as the `monero` submodule) with Opacra's own ports and data folder.
- Runs your own full node (no "simple mode" using public remote nodes until such nodes
  exist; you can still point it at a node you run elsewhere). New nodes keep the whole
  blockchain (no pruning) by default while the chain is small.
- No price feeds, no update checks, no P2Pool. Solo mining is built in; pools are listed at
  [opacra.org/start.html](https://opacra.org/start.html).
- Hardware wallets are hidden (not yet tested with Opacra).
- Windows wallets are kept in `C:\Users\<you>\Opacra\wallets` (not in Documents, which
  OneDrive may copy to the cloud). The default wallet name is "My Opacra wallet", never
  the computer's login name.

## Status

Version 1.0.0. Tested privately on Opacra mainnet (Windows and Linux): create and restore
wallets, receive, send, close and reopen, solo mining. Interface translations are Monero's,
updated to Opacra's name; text that changed for Opacra shows in English. Opacra is
experimental software: it has been reviewed by an experienced cryptocurrency developer
but has not had a professional security audit. Use it at your own risk.

## Building

Get the source with its submodules:

```bash
git clone --recursive https://github.com/opacra/opacra-gui
cd opacra-gui
```

### Windows (from Linux or WSL, with Docker)

```bash
bash contrib/opacra/build-windows-gui.sh
```

Builds the Windows libraries and a static Qt inside Docker (about 1.5–2 hours the first
time, minutes afterwards) and writes `dist/opacra-wallet-gui-v<version>-win-x64.zip` with
its SHA-256. Set `JOBS=<n>` to limit the threads used.

### Linux (Ubuntu 24.04)

```bash
sudo apt install build-essential cmake ninja-build git pkg-config libunbound-dev libssl-dev \
  libzmq3-dev libsodium-dev libhidapi-dev libnorm-dev libusb-1.0-0-dev libpgm-dev \
  libgcrypt20-dev libboost-chrono-dev libboost-date-time-dev libboost-filesystem-dev \
  libboost-locale-dev libboost-program-options-dev libboost-regex-dev \
  libboost-serialization-dev libboost-system-dev libboost-thread-dev qtbase5-dev \
  qtdeclarative5-dev qttools5-dev-tools libqt5svg5-dev qml-module-qtquick2 \
  qml-module-qtquick-controls qml-module-qtquick-controls2 qml-module-qtquick-dialogs \
  qml-module-qtquick-layouts qml-module-qtquick-window2 qml-module-qtquick-xmllistmodel \
  qml-module-qtquick-templates2 qml-module-qtgraphicaleffects qml-module-qtqml-models2 \
  qml-module-qt-labs-settings qml-module-qt-labs-platform qml-module-qt-labs-folderlistmodel
make release
build/release/bin/opacra-wallet-gui
```

In Ubuntu on Windows (WSL), start it with
`QMLSCENE_DEVICE=softwarecontext LIBGL_ALWAYS_SOFTWARE=1 build/release/bin/opacra-wallet-gui`.

The wallet's logo images are drawn by `contrib/opacra/make-branding.py`.

## Reporting a problem

Security issues: email support@opacra.org and don't post them publicly. Everything else:
the Opacra Discord or GitHub issues.
