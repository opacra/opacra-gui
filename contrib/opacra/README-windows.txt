Opacra Wallet (desktop) for Windows
===================================

Start: double-click opacra-wallet-gui.exe.
If the window stays blank or flickers, use start-low-graphics-mode.bat instead.

The first time:
- Choose "Create a new wallet", pick a name and a password.
- Write down the 25 words on paper and keep them offline. Anyone with them can spend your
  coins; without them a lost wallet can't be restored. Opacra never asks for them.
- The wallet runs its own Opacra node (opacrad.exe, in this folder) and downloads the
  blockchain the first time. Wait until it shows as synchronised before sending.

Good to know:
- Mainnet addresses start with Pa. Testnet addresses start with Te, and testnet coins
  have no value.
- Received coins can be spent after 10 blocks (about 5 minutes); mined coins after 60
  blocks (about 30 minutes).
- Don't run the wallet and the "Start Opacra mainnet" launcher at the same time: both use
  the same node and blockchain folder, and the wallet may stop a node it didn't start.
- Windows may say "Windows protected your PC" (the programs aren't code-signed yet):
  choose More info, then Run anyway. Some antivirus programs flag opacrad.exe because the
  node can mine; check the download against the signed SHA-256 on the release page first.

Opacra is experimental software. It has been reviewed by an experienced cryptocurrency
developer but has not had a professional security audit.

Website: https://opacra.org   Source: https://github.com/opacra
