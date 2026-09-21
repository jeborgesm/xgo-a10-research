# Test81 — MD native .md enrichment rebuilt from Test75 dispatcher architecture

## Status

**OFFLINE AUDITED / AWAITING HARDWARE**

## Rationale

After Test80 demonstrated that the Test76-derived expanded dispatcher can freeze even when the MD helper is bypassed, Test81 discards that dispatcher construction entirely.

Test81 starts again from the exact hardware-passed Test75 firmware and extends the **proven Test75 dispatcher pattern itself**, rather than modifying the Test76/Test77 dispatcher.

This also follows the hardware input actually in use: the MD materializer accepts native **.md** ROMs rather than the artificial .bin-only proof gate from Test76.

## Dispatcher

The Test75 generic external-helper runner at 0x80A382E0 remains unchanged.

The dispatcher at 0x80A38490 retains the Test75 stack frame, saved-register contract, helper-runner calls, failure branches, change accumulation in s0, and final s4/s5 initialization. Two calls are appended using the same instruction grammar as the proven FC/SFC pairs:

FC refresh -> FC catalog -> SFC refresh -> SFC catalog -> MD refresh -> MD catalog -> existing scanner -> CLASSIC.

The rebuilt dispatcher/string blob occupies 0x80A38490..0x80A38657, within the previously unused cave area used for these additive dispatchers.

## MD helper contract

- /MD/import/<stem>.md
- /MD/art/<stem>.jpg or .jpeg
- /MD/meta/<stem>.txt
- generated top-level /MD/<friendly-or-basename>.zmd

MD refresh helper SHA-256:
03b6402c19288de17700eb92cd209030cfc6eddb077de90db9f54b4ff7292651

MD catalog helper SHA-256:
2604672d00ec25f49a96e05214b1a3421b35717d04098800309bd08b26077645

The existing staged .md files can remain in place. ignore_file.xyz is expected to be ignored.

## Candidate identity

- ZIP: xgo-stock-test81-md-native-md-test75-dispatcher.zip
- ZIP SHA-256: cf7f41246d8d397a1155aad05a052ee37813bb65d9656f4c3f8610c5f8b3e688
- firmware SHA-256: 0127537fb24b4bb7759c9f370045169f3befbd6bed54d92d0a15071f00617d18
- LCFG CRC-32/MPEG-2: 0x788545D4
- ZIP integrity test passed.

## Hardware gate

With the current controlled SD-card fixture, invoke Refresh once.

Expected if the Test75-style extension is sound:
- valid .md inputs are materialized/imported;
- ignore_file.xyz is ignored;
- Games Updated is shown if wrappers/catalog entries are added;
- frontend remains responsive.

If it freezes, do not attribute the result merely to .md processing; compare the exact Test75 dispatcher extension and MD helper pair separately. Do not promote before hardware pass.
