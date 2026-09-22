# Post-Test100 bisrv NO BOOT root cause — LCFG reseal omission

Date: 2026-09-21
Status: **root cause closed at container-integrity level; hardware already supplies the failure/recovery correlation**

## User observation

The user correctly identified the pattern: post-Test100 experiments that alter `bios/bisrv.asd` repeatedly fail to boot, while restoring the protected Test97/Test106 `bisrv.asd` immediately restores boot.

## Existing project evidence we failed to carry forward

The repository already contains a closed LCFG integrity contract:
- header size 0x200;
- payload size at file offset 0x184;
- CRC-32/MPEG-2 at file offset 0x18c;
- CRC covers every payload byte from 0x200 through EOF;
- stock XGO image recomputes exactly;
- tool: `tools/reseal_lcfg.py`.

The SF2000-family reconstructed boot path validates this CRC before entering the application. Exact XGO bootloader code remains undumped, but the XGO image uses the identical container fields/algorithm.

## Why Test104 was the warning

Test104 changed exactly two payload bytes at file offsets 0x00A387E0..E1 and did not boot. Restoring the otherwise-identical protected firmware restored boot.

The previous Test104 finding described a "boot-sensitive firmware immediate" or possible unknown integrity condition. With the already-established LCFG reseal evidence, the simpler explanation is that those two payload bytes changed the CRC-covered region without updating the header CRC.

## Why Test107/Test108 repeat it

Both candidates changed many payload bytes in `bisrv.asd`. Their construction records focused on code placement/deltas but did not reseal the LCFG CRC after patching.

Therefore they were invalid LCFG images before any injected selector code could execute.

The NO BOOT results do **not** prove:
- the Test107 BSS-code hypothesis;
- the Test108 proven-executable-region code itself is bad;
- the selector hooks are reached at boot.

Those conclusions are demoted. The candidates failed the firmware-container gate first.

## Mandatory rule from now on

Every modified `bisrv.asd` candidate must pass, in this order:

1. exact expected baseline hash;
2. apply only manifest-approved payload patches;
3. recompute payload size = file_size - 0x200 and write LE32 at 0x184;
4. recompute CRC-32/MPEG-2 over `data[0x200:]` and write LE32 at 0x18c;
5. independently recompute and assert stored size/CRC;
6. diff against baseline and require that every changed payload byte belongs to the manifest; header changes are limited to 0x184..187 if size changes and 0x18c..18f for CRC;
7. only then package.

For same-size patches, 0x184 must remain identical and only the CRC field should change in the header.

## Candidate-builder policy

A builder that modifies bisrv and does not reseal must fail closed and refuse to emit a hardware candidate.

Do not create another hardware test until Test107/Test108 are independently resealed offline and the manifest audit passes. A resealed Test108 may become the next candidate, but it must receive a new test number because the previous Test108 hash is hardware-proven NO BOOT and must remain immutable evidence.

## Evidence grades

- XGO LCFG field offsets/CRC reproduction: **BIN**
- Test104 two-byte payload change -> NO BOOT; restore protected bisrv -> BOOT: **HW**
- Test107/108 modified unresealed bisrv -> NO BOOT; restore protected bisrv -> BOOT: **HW**
- exact XGO internal bootloader CRC enforcement: **INF/OPEN** pending bootloader dump
- failure mechanism being LCFG integrity rejection: **strong INF from BIN+HW+UP**, sufficient to make reseal mandatory
