# Test130 pre-helper failure closure — path is not a new filesystem contract

Date: 2026-09-23
Status: BIN + historical HW correction

A deeper repository review retracts the idea that /GB/refresh.xgc is suspicious merely
because it is a new helper directory.

Test73 established the external-helper loader with /SFC/refresh.xgc and Test75
propagated the same contract to /FC/refresh.xgc. Both are ordinary system-local
paths under /mnt/sda1/<SYSTEM>/ and were hardware-proven. Test97/Test106 likewise
use /MD/refresh.xgc. Therefore /mnt/sda1/GB/refresh.xgc is the direct architectural
continuation of an already-proven per-system pathname contract. There is no
repository evidence for a special executable-helper whitelist by system directory.

Test130 package audit also proves:
- firmware path is exactly /mnt/sda1/GB/refresh.xgc;
- ZIP member is GB/refresh.xgc;
- requested size is 0x101F08;
- actual member size is exactly 0x101F08;
- helper entry is li v0,1; jr ra; nop.

Thus the exact-size fread condition is structurally satisfied if fopen sees the
installed file. A missing/incorrectly installed file remains possible at runtime,
but is no longer the leading architectural hypothesis.

The strongest remaining pre-helper discriminator is the generic runner heap guard:
*(0x80C237B0) must be <= 0x86FFFFFF before fopen.

Next offline task: recover all firmware writes/calls affecting 0x80C237B0 and compare
the old Test85/Test106 selector-confirm path with the Test119/Test123 eight-row
selector-confirm path before native Refresh entry. Do not modify the GB materializer
or protected helper paths.
