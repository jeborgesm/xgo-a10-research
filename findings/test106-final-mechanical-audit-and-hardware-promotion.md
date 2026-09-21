# Test106 final mechanical audit and hardware promotion

Status: HARDWARE CANDIDATE.

## Audit caught and fixed one pre-hardware defect

The first OFFLINE Test106 build placed the literal CLEAN! at Stage1 offset 0x4AA. The is_clean comparator loaded the first four reference bytes with an LW from that address.

0x870004AA is not word-aligned. On MIPS this can raise an address exception once a CLEAN marker exists. The first recovery invocation could have succeeded because the marker was initially absent, while the second invocation would have reached the unaligned comparison.

This was caught before hardware promotion.

Correction:
- relocated CLEAN! to aligned Stage1 offset 0x4B8 / runtime 0x870004B8;
- updated both reference constructors:
  - Stage1 offset 0x210
  - Stage1 offset 0x34C
- zeroed the old 0x4AA literal location.
- no file-size changes.

## Final hashes

MD/catalog.xgc
- size 2642
- SHA-256 e4c21a94055a6aec817494d2f69450f12fbba3244a91c1b74e73de2a4e91b338

MD/catalog-safe.xgc
- size 7000
- SHA-256 45b3e2638b27e0d4a3ffa518e359413de619184ea9c93c4a5c83bbbc2e0ac65c

bios/bisrv.asd
- size 12768452
- SHA-256 b66dbcd86ad785875a6804bb7d07c6eb1195ceedb01c0bce8107f65eee2ab66e
- exact known-booting Test97/Test105 firmware.

Hardware candidate ZIP
- SHA-256 07703312d5a331f2a35f6cc42d44d85d608f33f0cc07335679b9d03ccd46e4d7

## Package delta vs HW-proven Test105

Changed:
- MD/catalog.xgc
- MD/catalog-safe.xgc

Added: none
Removed: none

Everything else byte-identical.

## Mechanical audit

Stage1 inserted helper entry points:
- 0x87000180 is_clean
- 0x87000260 write_state
- 0x87000310 write_active
- 0x87000340 write_clean
- 0x87000370 recovery_gate
- 0x870003C0 backup_and_activate

Conditional branch targets in inserted executable region are aligned and remain inside the 2642-byte Stage1 image.

Function stack frames have matching save/restore shapes:
- is_clean: -0x28 / +0x28
- write_state: -0x20 / +0x20
- write_active: -0x08 / +0x08
- write_clean: -0x08 / +0x08
- recovery_gate: -0x08 / +0x08
- backup_and_activate: -0x10 / +0x10

Stage2 differs from Test105 by only two direct call-target rewrites:
- recovery call -> 0x87000370 recovery_gate
- backup call -> 0x870003C0 backup_and_activate

No Stage2 size/address change.

## Intended first hardware sequence on current card

Current card is ideal:
- healthy LIVE 839 generation;
- stale complete 788 backup triplet;
- no .xgo-cat-state marker.

Expected:
1. install Test106 candidate;
2. boot;
3. run Refresh ONCE.
   Missing marker forces compatibility recovery, then current ROM set rebuilds; expected UI is likely Games Updated.
4. confirm responsive and MD frontend/game launch.
5. shut down and capture MD/art + Resources if practical.
   Expected marker: CLEAN!
   Stale 788 backup files may remain physically present but are logically inactive.
6. only after CLEAN marker is confirmed should a second Refresh be used to prove stale backups are ignored and the no-change path returns normally.

Do not intentionally power-cut during writes.
