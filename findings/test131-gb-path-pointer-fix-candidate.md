# Test131 — GB signed-path-pointer fix hardware candidate

Date: 2026-09-23
Status: OFFLINE AUDITED — hardware candidate

Test131 starts from exact Test127 and changes only the two malformed GB pathname
HI16 instructions identified in the Test127/Test130 root-cause closure.

Firmware changes:
- 0x80A39050: 3C0480A3 -> 3C0480A4 (refresh pathname)
- 0x80A3907C: 3C0480A3 -> 3C0480A4 (catalog pathname)
- LCFG CRC reseal only.

Effective pointers after correction:
- 0x80A390C0 /mnt/sda1/GB/refresh.xgc
- 0x80A390E0 /mnt/sda1/GB/catalog.xgc

Protected FC/SFC/MD/CLASSIC bodies and helper files are unchanged from Test127.
GB refresh/catalog helpers are unchanged from Test127.

Identity:
- firmware SHA-256: 4e9b7832fc955df6d7f582e9d7c383a0d5c3832accee9f800ef14677f1fc88e5
- LCFG CRC-32/MPEG-2: 0x1B3BD6E6
- GB refresh SHA-256: 00addd59c2b3305e936021bb6cb7c66e03cac334816cd2a61e5c216315e19810
- GB catalog SHA-256: 66030c93bfde3e790140265b1123b0ca6cb684efc251a9f602bad480ac7cbbfb
- ZIP SHA-256: 15c501fc1fb6321d5b1d9739bea32a44271eafe3cf9fab6976d85722758213f0

Hardware gate:
1. Preserve the existing GB import fixture from Test127 if still present.
2. Install Test131.
3. Refresh Games -> Game Boy once.
4. Expected first result: Games Updated and generated .zgb visible.
5. Verify generated entry artwork/title if fixture supplies them and launch the game.
6. Run Game Boy Refresh once more. Expected: No New Games, device responsive.

This test is no longer exploratory parser work: it validates the exact two-word
root-cause correction.
