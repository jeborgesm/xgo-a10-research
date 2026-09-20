# Generic helper runner load-bound closure for expanded MD catalog helper

Status: BIN, with existing HW lineage supporting the same runner/load mechanism. No Test104 candidate yet.

## Runner exact behavior

Test97 firmware generic helper runner is at runtime 0x80A382E0.

Arguments:
- a0 = helper pathname
- a1 = exact helper byte size

The runner:
1. opens the supplied helper pathname;
2. sets destination a0 = 0x87000000;
3. sets fread size = 1;
4. sets fread count = requested helper size;
5. calls firmware fread 0x802B3698;
6. requires returned byte count == requested helper size;
7. closes the file;
8. performs cache maintenance;
9. calls 0x87000000 as code;
10. restores the global at 0x80C2CE6C and returns helper v0.

Relevant sequence:

    80A38364  lui   a0,0x8700
    80A38368  li    a1,1
    80A3836C  move  a2,s1        # requested byte size
    80A38370  move  a3,s2        # FILE*
    80A38374  ... fread 0x802B3698
    ...
    80A3839C  bne   v0,s1,fail
    ...
    80A383F8  lui   t9,0x8700
    80A383FC  jalr  t9            # execute helper

Thus there is no 2642-byte intrinsic runner limit. 2642 is a caller-supplied catalog helper size.

## Strong existing size evidence

The SAME generic runner is already called in Test97 with two established helper sizes:

Catalog helper:

    0x00000A52 = 2,642 bytes

Refresh/materializer helper:

    0x00101F08 = 1,056,520 bytes

Examples in Test97 firmware:
- 0x80A38258/5C -> size 0x00101F08
- 0x80A3827C -> size 0x00000A52
- selective FC/SFC/MD dispatcher repeats the same pair
- MD refresh at 0x80A387B4/B8 uses 0x00101F08
- MD catalog at 0x80A387E0 uses 0x00000A52

The 1,056,520-byte helpers have already been part of the hardware-proven Refresh lineage.

Therefore expanding MD/catalog.xgc moderately does NOT require a new loader mechanism. It only requires changing the MD catalog call site's explicit size constant to the exact new payload length.

## Address-space envelope

Runner destination:

    0x87000000

Existing refresh helper extent:

    0x87000000 + 0x00101F08
      = 0x87101F08

Known catalog OLD buffers begin:

    0x87200000 TAX
    0x87210000 NEC
    0x87220000 BVS

Known NEW buffers begin:

    0x87240000 TAX
    0x87260000 NEC
    0x87280000 BVS

Therefore the existing proven 1,056,520-byte helper remains below the first catalog scratch buffer by:

    0x87200000 - 0x87101F08
      = 0x000FE0F8
      = 1,040,632 bytes

A hardened catalog helper in the low-kilobyte/tens-of-kilobyte range is far inside the already exercised runner envelope and nowhere near the catalog buffers.

This is much stronger evidence than merely assuming the 2642-byte helper can grow.

## Heap guard clarification

The runner's pre-open check around 0x80A38308 compares 0x86FFFFFF against the value stored at 0x80C237B0.

This is a guard protecting the 0x87000000 helper execution region from the current heap boundary/state. It is not a 2642-byte size check.

The runner later temporarily writes 0x87000000 to 0x80C2CE6C while the helper executes and restores the previous value afterward.

Exact allocator semantics remain OPEN, but existing 1,056,520-byte helper execution demonstrates that modest catalog-helper growth is compatible with this runner architecture.

## Safe design budget

Do NOT use the full 1,056,520-byte theoretical precedent.

For hardening, impose a conservative engineering budget:

    target expanded catalog.xgc <= 16 KiB

This is DESIGN, not a firmware requirement.

At 16 KiB:

    helper end = 0x87004000

which leaves almost the entire established gap before 0x87200000 untouched.

The recovery state machine should comfortably fit in this budget.

## Patch scope

For the first hardened MD proof:
- MD/catalog.xgc changes.
- MD catalog helper size immediate at 0x80A387E0 changes from 0x0A52 to exact new size.
- Do not change MD/refresh.xgc.
- Do not change FC/SFC catalog helper sizes.
- Do not alter common generic runner.
- Do not alter status paths.
- Do not alter Volume OSD.
- Do not alter CLASSIC.

This sharply limits firmware risk compared with Test103.

## Gate closed

Expanded-helper load safety is now sufficiently supported for offline construction.

Remaining pre-Test104 work:
1. implement the recovery state machine in an expanded MD/catalog.xgc;
2. retain the helper's existing indirect firmware-service ABI;
3. byte-verify backup and committed live members;
4. implement complete/partial backup startup rules;
5. statically audit every branch, path, service address, buffer extent, and return value;
6. simulate interruption at helper-level write/delete boundaries against the actual implemented state machine.

Only after those checks should Test104 be packaged for hardware.
