# Polish 02 — clock-only 48us wait tolerance, retain user-validated Polish 01 OLED

**Date:** 2026-10-28. **Branch:** `research-gp2040ce-xgo-integration`. **State:** offline candidate [SRC], source-extracted virtual XGO IRQ tests [MODEL], fast CI [CI PASS], full RP2040 linked firmware [CI PASS], user hardware [UNTESTED]. No GOLD BIOS/cable edits.

## Scope: actual controller reliability improvements, not more diagnostics

The owner has hardware-validated Polish 01 paged OLED for extended Street Fighter II play (no missed inputs noticed) and continues to report three faults in NES Contra: idle ghost jumps, unexpected repeated jumps on held A, and unwanted repeated shots on held B **with the starting single-shot rifle**. The original rifle does not explain these repeats as normal Machine Gun autofire. Preserve exact physical hold semantics; do not invent a one-shot pulse, change any ROM mapping, or suppress input bits.

**Polish 02 is a real controller source change:** enable tolerance of an unusually long **host CLOCK LOW/HIGH phase**, hypothesized to happen when the original XGO's scanner briefly enables MIPS IRQs between GPIO operations, without modifying DATA signal or XGO firmware. It is an incremental attempt to reduce unwanted release/reassert transitions in *held* buttons. The actual on-device link fault/IRQ pause duration remains **unmeasured**, and this change is **NOT** an idle ghost fix.

## Single mechanical change, exact source guarded

Original protected transparent driver:
`integrations/gp2040ce-xgo-test01/candidates/offline-test44-transparent-controller/XGODriver.cpp`
Git blob `cccb985a05baa8bb9078b6e336eb5f991c1a7a8f`.

New isolated Polish 02:
`integrations/gp2040ce-xgo-test01/candidates/offline-polish02-clock-tolerance/XGODriver.cpp`
Git blob `eff10e585ee46805801c3d218d5d8412630dd650`.

Executable source difference **only**:
- Keep `EDGE_TIMEOUT_US = 18` for initial `wait_data(true)` (do not lengthen initial host DATA release/first-bit acquisition).
- Add `CLOCK_TIMEOUT_US = 48`.
- Use it at the four `wait_clock(false|true)` sites during slots 1–11 and terminal CLK.
- Preserve all 12 physical button slots, `published_mask` direct mapping, true held state, early R slot0 sink timing, `data_sink/data_release()`, USB-PHY pull overrides, ISR masking, host DATA frame re-arm, OLED layout and paged I2C update.
- No XGO `bisrv.asd`, Frankie soldering, resistors, or per-ROM adjustments.

The new [Polish02 exact extracted C++ test](../tests/test_polish02_clock_tolerance_cpp.py) token-compares the original and candidate after reversing only the declared CLOCK wait changes and verifies `wait_data(true,EDGE_TIMEOUT_US)` remains unchanged. Fail closed if any other executable source behavior differs.

## Verified MODEL + CI, not observed on hardware

[GitHub Actions #40695772983](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40695772983) SUCCESS. All earlier protected tests plus the new [direct extracted C++](../tests/test_polish02_clock_tolerance_cpp.py) model passed:
- 1 normal and **23 synthetic XGO 25us stretched CLOCK phase** scenarios: Polish02 first and following held-A frames succeed, no responder CLOCK timeout or active failure. The protected 18us responder failed all **23** injected stretched cases.
- The synthetic host explicitly lengthens 12 LOW and 11 intervening HIGH windows. **Real XGO IRQ length is unknown**; simulated host word for the *stretched first* scan is not reconstructed with its true delayed sample timestamp, only next clean frame is compared.
- Also passes the existing transparency contract (all 12 buttons stay physical, no artificial pulse/edge queues).

Initial fast-CI attempts failed due to two test harness mistakes (overescaped Python regex and omitted global CLOCK constant when extracting `emit_frame()`); corrected before the successful test. Those were harness failures, not RP2040 compile/hardware failures.

## Completed real ARM firmware build and verified distribution (Oct 28)

[Full RP2040 build and ELF audit #40696044674](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40696044674) is **SUCCESS**. The workflow pinned GP2040-CE `3d1f32f7d02d418826b725b60208278d3be878c3`, Pico SDK 2.3.1, original input UI blob, unchanged paged OLED source blob, and Polish02 driver Git blob `eff10e585ee46805801c3d218d5d8412630dd650`. It compiled a full Cortex-M0+ UF2, verified `emit_frame()` remains in SRAM, and ran the masked IRQ/no-XIP linked ELF audit successfully. GitHub artifact ID **12819837151** is the full candidate, artifact ID **12820245338** the separate linked disassembly/symbols.

The downloaded candidate ZIP, UF2 magic and manifest/SHASUM were checked locally. The new UF2 is **2,515,968 bytes**, SHA256 **`699e46f1e157510e6fda03534700ba80824966bf74663c87c6457396986bce72`**. It is NOT user-tested. To avoid regressions, produced a checksum-verified local distribution `XGO-Controller-Polish-02-Clock-Tolerance-With-Rollback.zip` (SHA256 `f70e2c5733a80445e209a21c8a23bd1cd423a2c841ab53ddc578039f92239f4e`), containing:

- `01-TEST-POLISH02-CLOCK48-PAGED-OLED.uf2` (new compiled controller).
- `02-ROLLBACK-POLISH01-PAGED-OLED-HW-PASS.uf2` (current owner's tested working build).
- `03-ROLLBACK-ORIGINAL-TRANSPARENT-A-HW-PASS.uf2` (earlier accepted baseline).

The package is generated in this conversation's container; it is not committed to Git. **No XGO BIOS changes, no pad-bridge or cable work, no added electronics, no one-shot/pulse logic.** Current owner must choose whether to flash; no device action has happened in this research turn.

## Promotion criteria and honest limits

This is a plausible fix for **clock-induced interruptions of held button transmission**, not proof that the actual controller experienced XGO IRQ stretches of 25us. If successful on hardware, it could reduce repeated actions arising from dropped/reasserted held state. It has **no direct mechanism to correct** passive DATA-line false LOW at an idle first-bit sample; genuine unsolicited P2 jumps remain an independent OPEN issue. Do not say the fault is fully fixed until the device demonstrates both stable held A/B and absence of ghost inputs.

Do not replace the known-working Polish01 UF2 until independent full Cortex-M0+ cross-link + SRAM/no-XIP audit passes. The build workflow [`gp2040ce-xgo-polish02-build.yml`](../../../.github/workflows/gp2040ce-xgo-polish02-build.yml) clones pinned GP2040-CE `3d1f32f7d02d418826b725b60208278d3be878c3` and Pico SDK 2.3.1 and combines the candidate XGODriver.cpp with the previously tested paged OLED `tiny_ssd1306.cpp` blob `e441ecc441a1d495413fbd56171a9a72e7321883`. Verify actual linked ELF critical instructions and SHA before hardware use.

**Rollback:** user-installed Polish01 paged OLED UF2 SHA256 `5dcc28132ca54293a3d27dc2a452269bc47a1e7f141bd49c2c7e296918071b5b`; original transparent A UF2 SHA256 `94ea7228c774a67e8252e7e09d94938530e5d74572d985332e6840ae09fe8b84`; XGO GOLD BIOS SHA256 `75f858b6d9a1eb81235ae9e9c9b449a6a3052ad4365e5411b8ce041075e99d6b`. No physical or firmware rollback was necessary during this offline work.
