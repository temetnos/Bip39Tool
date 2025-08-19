# BIP39 Offline Tool (Interactive)

**Purpose:** Safely perform common BIP39 tasks *offline* on a trusted machine:

- Validate a **24-word mnemonic** (checksum)
- Compute the **correct 24th word** from the first 23 words
- **Rebuild** a valid 24-word mnemonic (given 23 or 24 words)
- **Encode** a 24-word mnemonic into a **compact hex** string (72 hex chars)
- **Decode** a compact hex string back into the **24-word mnemonic**
- **Generate** a fresh random mnemonic (12/15/18/21/24 words) using strong entropy

> **Security:** Always run offline on a trusted machine. Never paste real seeds into an online computer or web page.

---

## Requirements

- Python 3.8+
- The official BIP39 English wordlist (`english.txt`, exactly 2048 lines) placed next to the script.
  - Get it from the [BIP39 repository](https://github.com/bitcoin/bips/blob/master/bip-0039/english.txt).

your-folder/
bip39_tool.py
english.txt

---
Run:
python3 bip39_tool.py

You will see:
=== BIP39 Offline Tool ===
1) Validate a 24-word mnemonic
2) Compute the 24th word from the first 23
3) Rebuild a valid 24-word mnemonic
4) Encode 24 words to compact hex
5) Decode hex back to 24 words
6) Generate a random mnemonic (12/15/18/21/24)
Q) Quit

Pick a number, input the requested data, and the tool prints the result and returns to the menu.

⸻

Usage Examples

1) Validate a 24-word mnemonic

Choose 1, paste your 24 words (space-separated). The tool prints whether the checksum is valid.

2) Compute the 24th word from the first 23

Choose 2, paste the first 23 words, and it prints the correct 24th word per BIP39 checksum rules.

3) Rebuild a valid 24-word mnemonic

Choose 3, paste either 23 or 24 words. The tool recomputes and prints a valid 24-word mnemonic (fixing the last word if needed).

4) Encode 24 words to compact hex

Choose 4, paste your 24 words. The tool returns a 72-character hex string (each word index encoded as 3 hex chars).
Useful for compact offline storage (QR codes, NFC tags, paper backups, metal plates, etc.).

5) Decode hex back to 24 words

Choose 5, paste the 72-character hex string. The tool returns the corresponding 24-word mnemonic.

6) Generate Random Mnemonic (Offline)

Use Option 6 to create a fresh mnemonic completely offline. The tool supports 12/15/18/21/24 words (BIP39).

Entropy sources:
	•	OS random (recommended): Uses the system CSPRNG via Python secrets. Suitable for cryptographic keys on modern OSes.
	•	Dice (1..6): For air-gap purists. Needs ~100 rolls for a 24-word mnemonic (256-bit entropy). The tool uses rejection sampling to avoid modulo bias; if your value lands in the rejection range, add a few rolls and retry.
	•	Hex (manual): Provide exact entropy bytes in hex (e.g., 32 bytes = 64 hex chars for 24 words).

Quick steps (24-word example):
	1.	Select 6.
	2.	Press Enter to accept 24 words.
	3.	Choose entropy source: [R] for OS random (default).
	4.	The tool prints a 24-word mnemonic.
	5.	(Optional) Validate with option 1.
	6.	(Optional) Encode to hex with option 4, then decode back with option 5 to verify reversibility.

Security: Always run offline on a trusted machine. Hex encoding is not encryption; encrypt or secret-share it if confidentiality is required.

⸻

Why hex encoding helps for backup & storage

A 24-word BIP39 mnemonic represents 24 indices into the 2048-word list (each index fits in 11 bits).
This tool encodes each index as 3 hex characters (0x000–0x7FF), producing a fixed-length 72-character string.

Advantages:
	•	Compact & deterministic: always 72 hex chars; easy to fit in constrained storage.
	•	Media-agnostic: plain text works in QR codes, NFC tags, paper backups, metal plates, etc.
	•	Reversible: the tool decodes hex back to the exact 24 words using the standard BIP39 English wordlist.

Integrity tip: After generating a mnemonic, encode to hex (option 4) and immediately decode it back (option 5) to confirm a perfect round-trip before storing the backup.

Note: Hex encoding here is not encryption. Anyone with the hex and the wordlist can reconstruct the mnemonic.
If you need secrecy, encrypt the hex or split it into shares (e.g., Shamir’s Secret Sharing) and store them separately.

⸻

Example Workflow (Deterministic Variant Mnemonics)

A testing/backup workflow to create deterministic variants while keeping validity:
	1.	Start with a known 24-word mnemonic.
	2.	Modify the first 23 words deterministically (e.g., swap positions 7 and 12).
	3.	Use Option 3 – Rebuild a valid 24-word mnemonic to recompute the correct last word for the modified first 23 words.
	4.	The result is a valid but independent mnemonic (new wallet). There is no cryptographic link to the original mnemonic.
	5.	Optionally, encode this 24-word mnemonic as hex and store it compactly.
	6.	Before storing, run a quick round-trip: encode (4) → decode (5) and re-validate (1). This catches any transcription/storage errors early.

Why this helps backups:
	•	You can generate multiple independent wallets deterministically from a rule you control.
	•	You avoid invalid mnemonics by letting the tool recompute the correct checksum word.
	•	Compact hex backups can be split across media or locations. Combine them later to fully reconstruct the mnemonic.

Important: If you forget your personal transformation rule, the funds are irrecoverable.
Write your rule down securely (separately from the backup) or use standard secret-sharing/encryption.

⸻

Operational Security Checklist
	•	Run offline on a trusted machine (no network).
	•	Keep OS/Python up to date.
	•	Prefer OS random for entropy; if using dice, ensure sufficient rolls and avoid modulo bias (the tool enforces this).
	•	Store hex backups separately from any transformation rules or passphrases.
	•	Remember: hex ≠ encryption. Use encryption or secret sharing if confidentiality is needed.
	•	Test recovery regularly: decode your backup and validate before you need it.

⸻

Derivation Paths (FYI)

This tool focuses on mnemonics, not on deriving addresses. Wallets derive addresses using paths like:
	•	Ethereum: m/44'/60'/0'/0/x

If you need an address previewer for certain paths, build a separate offline tool (e.g., Node.js + ethers) and never expose secrets online.

⸻

License

MIT (suggested).

⸻

Disclaimer

This tool is provided as is for educational/backup purposes.
You are responsible for your operational security. Use at your own risk.

