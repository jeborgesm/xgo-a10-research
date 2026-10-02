# Physical SD firmware bit audit — b5f1651b is the correct Test A parent

Date: 2026-10-02
Branch: research-audio-fidelity-latency
Status: USER-SUPPLIED PHYSICAL SD IMAGE + BIN AUDIT

The user supplied bios/bisrv.asd directly from the currently running SD card.

Identity:
- size 12,768,452
- SHA256 b5f1651b146b52070f2e89d51cc2694852af565150568f78d06404e9f9f461ab
- LCFG CRC32/MPEG-2 0x4AB4C686

This exactly matches the HW-confirmed xgo-gb-gba-refresh-path-repair-v2 firmware.

## Chronology correction

ea442b74... was the earlier 2026-09-24 GBC/GBA propagation candidate. Physical testing on 2026-09-29 exposed the GB pathname-terminator collision. Repair-v2 b5f1651b... superseded that firmware.

The older physical-baseline/handoff language presenting ea442b74... as current is stale.

## Exact repair-v2 bytes in uploaded image

At 0x80A381D8 the relocated string is:
/mnt/sda1/GB/catalog.xgc followed by NUL.

At 0x80A39088 the instruction word is 0x248481D8, the final reference to that relocated path.

At 0x80A390F8 the GBC body begins exactly as documented.

At 0x80A398C8 the GBA catalog pathname is intact and its required terminator at 0x80A398E1 is zero. This distinguishes repair-v2 from the rejected first repair.

## CPS1 scheduler exact preservation

The complete helper at 0x8035EEE8..0x8035EF67 is byte-for-byte equal to the versioned MAIN_WORDS in tools/cps1/patch_mapper_v19_stock_scheduler.py.

The early island at 0x8035F070..0x8035F07F also matches exactly.

All nine scheduler setup/re-entry patch sites contain their final patched words.

Therefore repaired CPS1 pacing is directly proven in the physical SD firmware, not merely inferred from lineage.

## Arcade chronology

Final NeoGeo Test28 explicitly records no firmware change. It modifies the external ARCADE/NEOGEO/refresh.xgc helper.

Therefore the current SD can correctly contain b5f1651b... bisrv.asd plus later Test28 external Arcade helpers.

## Test A patch-site verification

All three native-22050 sites contain their expected parent words:
- 0x80306E00 = 0x3402AC44
- 0x802FDFC8 = 0x24025622
- 0x802FE068 = 0x24025622

Applying only Test A and resealing gives:
- output SHA256 060093e8fd2a3fa559c9b43e207c4bb495de82e87519b672a799d19b304b20b7
- LCFG CRC32/MPEG-2 0x17CBBF35
- 10 changed bytes total: four CRC bytes, four selected-rate instruction bytes, and one byte in each comparison immediate
- zero unexpected changes.

## Corrected baseline

Gameplay-audio Test A protected firmware parent is b5f1651b146b52070f2e89d51cc2694852af565150568f78d06404e9f9f461ab.

The fail-closed builder has been corrected accordingly.
