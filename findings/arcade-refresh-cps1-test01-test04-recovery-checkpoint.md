# Arcade Refresh CPS1 Test01-Test04 recovery checkpoint

Date: 2026-09-26

Branch: `research-arcade-refresh-four-family`

Status: **recovered project-state record from the immediately preceding XGO project investigation.** This note restores work that had remained in chat rather than GitHub. It intentionally distinguishes what was hardware-observed from later interpretation.

## Process correction

The active Arcade investigation must follow:

- `docs/MODIFICATION-CONTINUITY-PROTOCOL.md`
- `docs/REUSE-FIRST-ENGINEERING-INDEX.md`
- the evidence classes HW / BIN / SRC / UP / INF / OPEN.

Conversation memory is not authoritative project state. Important observations must be committed before further experimental work.

No new hardware candidate is authorized by this recovery note.

## Scope

The dedicated Arcade command must eventually classify/orchestrate the four stock Arcade families:

- CPS1
- CPS2
- NeoGeo
- IGS

The present checkpoint concerns the first CPS1 proof path only.

Do not generalize CPS1 behavior to the other three families without their own evidence gates.

## Recovered Test04 HW checkpoint

**Test04 is the last positive hardware checkpoint for CPS1 Refresh/import/catalog persistence. Freeze it as evidence; do not mutate it into Test05 while the launch/runtime divergence remains open.**

Recovered HW observations:

- Refresh discovers the CPS1 import.
- The generated `1941.zfb` is materialized.
- The CPS1 catalog is updated sufficiently for the new entry to appear.
- The generated `1941.zfb` size observed was **59,918 bytes**.
- Its launcher trailer resolves to **`1941.zip`**.
- The first **59,904-byte** preview region is zero-filled.
- Re-entry/live-list behavior can freeze after Refresh.
- Launch of the generated/imported 1941 entry does not reach successful gameplay.

The zero-filled preview must **not** be called corruption. Existing Refresh reconstruction uses a GBA-style blank-preview fallback when artwork is absent. Whether Arcade should later use richer fallback artwork is separate from launch correctness.

## What Test04 proves and does not prove

HW proves enough of the import/catalog path to show that the CPS1 item can be discovered, materialized and exposed by the frontend.

HW does **not** yet prove:

- that the generated wrapper is byte-for-byte equivalent to a known-good stock CPS1 wrapper in every launch-relevant field;
- that the live frontend cache/list lifecycle is correctly invalidated after mutation;
- that the selected-list/category/index state entering native CPS1 launch is equivalent to a stock CPS1 title;
- that the user's `1941.zip` matches the ROM contract expected by the stock XGO FBA driver;
- the causal location of the launch failure.

All of those remain **OPEN** until separately closed.

## Correct runtime oracle

Do **not** use Pac-Man/Test11 as the launch oracle.

The current SD-card Pac-Man path returns to the menu and is part of the historical reason CLASSIC/MAME2000 exists. It is therefore not a valid positive comparator for current native CPS1 launch.

Use a **currently working stock CPS1 title**, with **Cadillacs & Dinosaurs** as the preferred comparator.

Known stock mapping already preserved in repository archaeology:

```text
Cadillacs and Dinosaurs.zfb
    -> dino.zip
    -> stock native CPS1/FBA path
    -> working gameplay on current hardware
```

The current comparison target is:

```text
known-good stock CPS1
Cadillacs and Dinosaurs.zfb
    -> dino.zip
    -> selected CPS1 list/context
    -> stock preprocessing
    -> stock FBA
    -> PLAY

generated CPS1
1941.zfb
    -> 1941.zip
    -> selected CPS1 list/context
    -> stock preprocessing
    -> stock FBA
    -> FAIL
```

Find the **first demonstrated divergence**.

## BIN evidence recovered after Test04

Inspection of the exact XGO `bios/bisrv.asd` found CPS1/FBA material for 1941, including:

- descriptions `1941 - Counter Attack (Japan)` and `1941 - Counter Attack (World)`;
- internal identifiers including `1941j` and `1941`.

Classification: **BIN**.

This demonstrates that the stock XGO FBA binary contains 1941 driver identity/material. It does **not** by itself prove that an arbitrary 1941 ROM set is compatible, nor that ROM compatibility is the cause of Test04's launch failure.

The earlier chat statement that ROM-set compatibility was the "leading suspect" is retracted. ROM compatibility is one hypothesis among the remaining launch-boundary questions.

## Existing wrapper/launch contract that must be reused

Repository archaeology already closed these mechanisms and they must not be rediscovered by speculative patching:

- Arcade/CLASSIC wrapper preview: 144 x 208 x 16-bit RGB565 = 59,904 bytes.
- Lightweight Arcade launcher metadata follows that preview.
- Historical stock example:
  - `Street Fighter II- The World Warrior.zfb`
  - trailer archive basename `sf2.zip`.
- Stock preprocessing constructs the real archive path with `%s/bin/%s`.
- Current selected system/list directory state and persistent archive-name state are stock-produced values.
- Do not parse untouched wrapper bytes from `ROM_BUFFER` at a late runtime hook; prior archaeology disproved that assumption.
- Browser launch sites enter stock `run_game()` with the selected wrapper path and stock preprocessing establishes the runtime state before final FBA dispatch.

Relevant existing findings include:

- `findings/game-metadata-enrichment-title-art-contract-closed.md`
- `findings/game-metadata-enrichment-stock-contract.md`
- `findings/hardware-test-05-cps1-zfb-load-failure-test06-fix.md`
- `findings/test07-zfb-format-correct-rom-buffer-assumption-wrong.md`
- `findings/xgo-arcade-stock-path-globals-closed.md`
- `findings/classic-deep-test12-contract-audit-test33.md`
- `findings/arcade-expansion-scope-and-priority-targets.md`

## Offline gate before another hardware test

No Test05 is authorized yet.

Offline comparison must first exhaust, at minimum:

1. generated `1941.zfb` versus a known-good stock CPS1 wrapper such as Cadillacs;
2. CPS1 catalog record/index placement and synchronized triplet behavior;
3. selected-list/category/subsystem state entering stock `run_game()`;
4. stock preprocessing/archive-name state;
5. any index-dependent or driver-identity metadata used before FBA dispatch;
6. the exact 1941 ROM filename/size/CRC contract compiled into the XGO stock FBA, if recoverable from BIN;
7. comparison of that contract to the actual imported `1941.zip` when the exact ZIP is available;
8. live-list/cache invalidation as a separate issue from launch correctness.

Do not combine cache freeze and launch failure into one causal story without evidence.

## Hardware-cycle rule

The next hardware candidate must answer one narrow question that cannot reasonably be closed offline. Before packaging it:

- identify exact protected parent;
- preserve source/reconstruction;
- use deterministic fail-closed builder logic;
- verify original patch words/ranges;
- reseal and independently verify LCFG;
- generate complete byte-diff manifest;
- archive exact hashes/provenance;
- state expected observations and interpretation branches.

Test ZIPs are evidence artifacts, not source.

## Immediate next task

Continue **offline only** from Test04.

Recover the exact stock XGO 1941 ROM contract from `bisrv.asd` as far as BIN evidence permits, while simultaneously comparing the known-good Cadillacs launch path against the generated 1941 path.

Do not patch firmware and do not request another hardware test until the first divergence is demonstrated or the offline evidence is genuinely exhausted.
