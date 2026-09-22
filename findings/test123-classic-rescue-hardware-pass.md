# Test123 — CLASSIC Refresh rescue hardware PASS

Date: 2026-09-21
Branch: `research-classic-refresh-resurface`

## Hardware result

**PASS.** User confirmed Test123 successful on real XGO A10 hardware.

## Candidate identity

Firmware SHA-256:
`7becafa3372e7b511bd8f05d0f378ca6397d72c6cc5c075f2e0d650cba2a86b5`

LCFG CRC-32/MPEG-2:
`0x91CA4950`

Firmware-only ZIP SHA-256:
`528347bd7e7005074ff9fc1b459d0f9ec7499f519fcecd02b0d9aa96c7a39dd2`

Runtime CLASSIC helper present on the tested SD:
`/CLASSIC/refresh.xgc`
SHA-256:
`9f932f35b1627bb8a4a7427831454e3c5dd854972231c1062316a814ada8723f`

This is the canonical recovered Test72 hardware-proven helper.

## What this proves

HW:
- Test122 selector/UI lifecycle survives the Test123 dispatcher change.
- command 7 / Classic can be routed independently instead of falling through to MD.
- the native Refresh frame/workspace -> CLASSIC continuation contract is valid in the current selector lineage.
- `s5=0; j 0x80A38000` is a valid post-workspace CLASSIC route.
- the preserved Test72 external CLASSIC helper remains compatible with the current firmware lineage.
- the operation returns without the prior standalone-call hard lock.

BIN/SRC:
- FC/SFC/MD bodies are byte-identical to Test122.
- CLASSIC bootstrap `0x80A38000..0x80A3823F` is byte-identical to the protected implementation.
- commands 3..6 no longer fall through to MD in Test123; they intentionally use a non-mutating native no-change return pending implementation.

## Current protected checkpoint

Test123 supersedes Test122 as the protected functional Refresh checkpoint for CLASSIC routing.

Preserve:
- Test122 eight-row UI/navigation;
- Test118 B-close behavior;
- Test119 caller-selection normalization/re-entry;
- Test122 stock-selector compositor suppression;
- Test123 independent CLASSIC command routing;
- canonical Test72 `/CLASSIC/refresh.xgc`.

## Next priority

Wire GB, GBC and GBA individually using preserved six-console scanner/materializer evidence.

Arcade remains separate: one UI command must orchestrate/classify the shared `/ARCADE` content across stock CPS1/CPS2/NeoGeo/IGS catalogs rather than pretending Arcade is one stock list ID.

After all eight individual commands are stable, add the explicit ninth `Refresh All` command.
