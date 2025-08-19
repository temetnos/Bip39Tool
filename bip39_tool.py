#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BIP39 Offline Tool (interactive, English)
Features:
  1) Validate a 24-word mnemonic (checksum)
  2) Compute the correct 24th word from the first 23
  3) Rebuild a valid 24-word mnemonic (given 23 or 24 words)
  4) Encode a 24-word mnemonic to compact hex (72 hex chars)
  5) Decode hex back to a 24-word mnemonic

REQUIREMENT:
  - Place the official BIP39 English wordlist as 'english.txt' (2048 lines)
    in the same folder as this script (get it from the BIP repository).

SECURITY:
  - Run offline on a trusted machine. Never paste real seeds on an online computer.
"""

import sys
from hashlib import sha256

# ---------- Core helpers ----------
def load_wordlist(path="english.txt"):
    with open(path, "r", encoding="utf-8") as f:
        words = [w.strip() for w in f if w.strip()]
    if len(words) != 2048:
        raise RuntimeError("english.txt invalid: expected 2048 words.")
    return words

def idx_map(wordlist):
    return {w: i for i, w in enumerate(wordlist)}

def bits_from_indices(indices):
    return ''.join(f"{i:011b}" for i in indices)

def bytes_from_bitstring(bitstr):
    if len(bitstr) % 8 != 0:
        bitstr += '0' * (8 - (len(bitstr) % 8))
    return int(bitstr, 2).to_bytes(len(bitstr)//8, 'big')

def normalize_words(s: str):
    # Lowercase, strip commas/extra spaces, split.
    s = s.replace(",", " ").strip().lower()
    return [w for w in s.split() if w]

def validate_mnemonic(words, wl, w2i):
    if len(words) != 24:
        return False
    try:
        idx = [w2i[w] for w in words]
    except KeyError as e:
        print(f"[!] Unknown BIP39 word: {e.args[0]}", file=sys.stderr)
        return False
    bits = bits_from_indices(idx)          # 264 bits
    ent_bits, cs_bits = bits[:256], bits[256:]
    ent_bytes = bytes_from_bitstring(ent_bits)
    digest_bits = f"{int.from_bytes(sha256(ent_bytes).digest(),'big'):0256b}"
    return cs_bits == digest_bits[:8]

def guess_last_word(first23, wl, w2i):
    if len(first23) != 23:
        raise ValueError("Provide exactly 23 words.")
    try:
        idx23 = [w2i[w] for w in first23]
    except KeyError as e:
        raise ValueError(f"Unknown BIP39 word: {e.args[0]}")
    first253 = bits_from_indices(idx23)    # 253 bits
    for tail in range(8):                  # last 3 entropy bits
        ent_bits = first253 + f"{tail:03b}"
        ent_bytes = bytes_from_bitstring(ent_bits)
        cs8 = int.from_bytes(sha256(ent_bytes).digest(), 'big') >> (256-8)
        last_index = (tail << 8) | cs8     # 11 bits
        if 0 <= last_index < 2048:
            candidate = first23 + [wl[last_index]]
            if validate_mnemonic(candidate, wl, w2i):
                return wl[last_index]
    raise RuntimeError("Could not determine a valid 24th word (check input).")

def seed_to_hex(words, wl, w2i):
    if len(words) != 24:
        raise ValueError("Provide exactly 24 words.")
    try:
        idx = [w2i[w] for w in words]
    except KeyError as e:
        raise ValueError(f"Unknown BIP39 word: {e.args[0]}")
    return ''.join(f"{i:03x}" for i in idx)   # 72 hex chars (24 * 3)

def hex_to_seed(h, wl):
    h = h.strip().lower()
    # Allow optional 0x prefix removal per segment (not common, but sanitize)
    h = h.replace("0x", "")
    if len(h) % 3 != 0:
        raise ValueError("Hex length must be a multiple of 3 (each word index is 3 hex chars).")
    try:
        idx = [int(h[i:i+3], 16) for i in range(0, len(h), 3)]
    except ValueError:
        raise ValueError("Invalid hex string.")
    if any(not (0 <= x < 2048) for x in idx):
        raise ValueError("Index out of range 0..2047.")
    return [wl[i] for i in idx]

# ---------- UI helpers ----------
MENU = [
    ("Validate a 24-word mnemonic", "validate"),
    ("Compute the 24th word from the first 23", "guess-last"),
    ("Rebuild a valid 24-word mnemonic", "rebuild-last"),
    ("Encode 24 words to compact hex", "encode-hex"),
    ("Decode hex back to 24 words", "decode-hex"),
]

def print_menu():
    print("\n=== BIP39 Offline Tool ===")
    for i, (title, _) in enumerate(MENU, start=1):
        print(f"{i}) {title}")
    print("Q) Quit")

def ask(prompt):
    try:
        return input(prompt).strip()
    except EOFError:
        return "Q"

def main():
    try:
        wl = load_wordlist("english.txt")
    except Exception as e:
        print(f"[!] Failed to load wordlist: {e}")
        sys.exit(1)
    w2i = idx_map(wl)

    while True:
        print_menu()
        choice = ask("> Select (1-5 or Q): ").lower()

        if choice in ("q", "quit", "exit"):
            print("Bye.")
            break

        if not choice.isdigit() or not (1 <= int(choice) <= len(MENU)):
            print("[!] Invalid selection.")
            continue

        _, cmd = MENU[int(choice)-1]

        try:
            if cmd == "validate":
                s = ask("Enter 24 words (space-separated):\n> ")
                words = normalize_words(s)
                ok = validate_mnemonic(words, wl, w2i)
                print("✔ Valid." if ok else "✖ Invalid!")

            elif cmd == "guess-last":
                s = ask("Enter the first 23 words (space-separated):\n> ")
                words = normalize_words(s)
                last = guess_last_word(words, wl, w2i)
                print(f"24th word: {last}")

            elif cmd == "rebuild-last":
                s = ask("Enter 23 or 24 words (space-separated):\n> ")
                words = normalize_words(s)
                if len(words) not in (23, 24):
                    print("[!] Provide 23 or 24 words.")
                    continue
                first23 = words[:23]
                last = guess_last_word(first23, wl, w2i)
                out = first23 + [last]
                print("Valid 24-word mnemonic:\n" + " ".join(out))

            elif cmd == "encode-hex":
                s = ask("Enter 24 words (space-separated):\n> ")
                words = normalize_words(s)
                hx = seed_to_hex(words, wl, w2i)
                print("Hex (72 chars):\n" + hx)

            elif cmd == "decode-hex":
                hx = ask("Enter hex (72 chars, each word = 3 hex chars):\n> ")
                words = hex_to_seed(hx, wl)
                print("24 words:\n" + " ".join(words))

        except Exception as e:
            print(f"[!] Error: {e}")

if __name__ == "__main__":
    main()