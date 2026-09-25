# Arcade catalog helper — first exact emission and delta audit

Date: 2026-09-25
Branch: research-arcade-refresh-four-family
Status: OFFLINE EMISSION PASS; not yet a firmware/hardware candidate

The exact parent was extracted directly from the local golden package:
xgo-gbc-gba-golden-propagation-candidate.zip -> GBA/catalog.xgc

Parent verification:
- size 2642
- SHA db7c1173f5b98adb3506b2676a035ba6e54b35a4391709cbbcd7ad92b983cbc6

The guarded emitter was executed against that exact binary. An independent
pre-parent delta audit allowed only:
- +0x0444 suffix middle immediate;
- the seven proven LUI/ADDIU reference pairs;
- +0x0730..+0x0738 GBA cache invalidation.

Result for every family:
- 20 changed bytes inside the original 2642-byte parent;
- 0 changed bytes outside the allow-list;
- all remaining bytes in the original image are byte-identical.

Final emitted identities after removing an unnecessary duplicate appended rb/wb
pair (the original mode literals remain valid and referenced):

CPS1:
- size 2767
- SHA dd7f6c21428bd482ddbc7da298bd9e2e9fb4b6b449065831b26d0fadc9374528

CPS2:
- size 2767
- SHA 7a636c1a801de7c63bfe4d7e9bbed9acd9ac0bdb4b8756f966ee04a37e3edb88

IGS:
- size 2766
- SHA 97cde79e59626dcfc1997f1678d61a87d81dd0b5e686ec5ba629fb4b55683b7b

NEOGEO:
- size 2769
- SHA 6f91ff89aeecea7f3128bdbdbd66e2a0eca2df46257ca93edcd02aa790f3ac7c

All appended tables begin:
- slot0 +0x0A52
- slot1 +0x0A70
- slot2 +0x0A8E
- root  +0x0AAC

The family-dependent final size difference is solely the family name length in
the staging root.

This closes the first actual Arcade catalog-helper emission. Before command-6
wiring, independently resolve every patched reference in each emitted helper
back to its expected appended ASCII string and verify the cache store sequence
is absent and the .zfb predicate disassembles as intended.
