# Test105 final mechanical audit and hardware promotion

Status: OFFLINE AUDIT PASS. Exact bytes promoted to HARDWARE CANDIDATE; no hardware result yet.

## Exact artifact

ZIP SHA-256:
38b502be0d6b837bfeededcf8a6ca67c80b9f217ac6d2774fb885448343b050f

The promoted HARDWARE-CANDIDATE ZIP is byte-identical to the previously audited OFFLINE ZIP.

## Exact Test97 delta

A complete file-by-file SHA-256 comparison against xgo-stock-test97-md-dot-gate-isolation.zip found:

ADDED:
- MD/catalog-safe.xgc

CHANGED:
- MD/catalog.xgc

REMOVED:
- none

No other file differs.

Therefore bios/bisrv.asd, MD/refresh.xgc, Resources, CLASSIC, UI/status assets, and all unrelated baseline behavior are byte-identical to Test97.

## Firmware proof

bios/bisrv.asd:
- size 12,768,452
- SHA-256 b66dbcd86ad785875a6804bb7d07c6eb1195ceedb01c0bce8107f65eee2ab66e

This is the exact known-booting Test97/user-recovery firmware. Test105 makes zero firmware changes.

## Stage1 mechanical audit

MD/catalog.xgc:
- size 2642 exactly
- SHA-256 135dae8bf00962db365afe1cffd6c2f36b0780033d11e89f4694925f05276a80

Confirmed constants:
- pathname pointer -> /mnt/sda1/MD/catalog-safe.xgc
- mode -> rb
- Stage2 requested bytes -> 0x1B58 / 7000
- destination -> 0x87180000
- fopen -> 0x802B3524
- fread -> 0x802B3698
- fclose -> 0x802B2F40
- exact read-count branch required before execution
- Stage2 call target constructed as 0x87180000

The 0x54-byte Stage1 cache-maintenance sequence at offset 0x80 has the exact same SHA-256 as Test97 firmware bytes 0xA383A4..0xA383F7:
879de11fffb73d931010f8a709913dd4f845d6df84fb74256ee675b596c17ba3

Thus cache synchronization is not inferred; it is byte-for-byte lifted from the stock runner.

## Stage2 hook audit

MD/catalog-safe.xgc:
- size 7000
- SHA-256 c36a77d2d1291584306c651c204b489a83a9eb77736506638b71d6e45dc941e2
- base 0x87180000
- end 0x87181B58

All 42 direct J/JAL instructions in the relocated image target addresses inside the relocated Stage2 image. None targets the old 0x87000000..0x87001B58 image.

Key relocated targets:
- entry wrapper: 0x871818E8
- recovery preflight: 0x87180A60
- backup_old: 0x87181030
- rollback: 0x87181208
- verify_new: 0x87181680
- backup hook: 0x871819A0
- rollback hook: 0x871819EC
- verify hook: 0x87181A18

Hook branches mechanically resolve:
- 0x87180644 -> 0x871819EC
- 0x87180678 -> 0x871819EC
- 0x8718069C -> 0x871819EC
- 0x871806D0 -> 0x871819EC
- 0x871806F4 -> 0x871819EC
- 0x87180728 -> 0x871819EC

The post-commit hook at 0x87180730 resolves to verify hook 0x87181A18.

## Promotion decision

All current offline rejection gates pass.

Test105 is therefore promoted to a narrowly scoped hardware candidate WITHOUT rebuilding:
- same audited ZIP bytes;
- same SHA-256;
- unchanged firmware.

The first hardware observation should be boot only. Because Test104 failed before helper execution, establishing that this exact unchanged-firmware package boots is the cleanest first boundary. Do not invoke Refresh until boot is confirmed.
