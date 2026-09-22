# XGO modification continuity and source-preservation protocol

Status: mandatory process for all firmware modification work.

## Why this exists

The project has accumulated enough binary archaeology, family-source comparison, hardware proof, and reconstructed source that new work must not regress into trial-and-error byte patching after a chat/session handoff.

A hardware candidate is the *last* step of a research cycle, not the mechanism used to discover ordinary control flow.

## Evidence hierarchy

Use and preserve the existing evidence classes:

- **HW** — observed on XGO hardware.
- **BIN** — directly established from XGO binary/data.
- **SRC** — source/reconstruction evidence preserved in this repository.
- **UP** — behavior/source from an upstream or family device.
- **INF** — inference.
- **OPEN** — unresolved.

UP/INF must never silently become XGO fact.

## Mandatory source-first workflow

Before emitting a firmware candidate:

0. Read `docs/REUSE-FIRST-ENGINEERING-INDEX.md` and identify the nearest already-solved XGO mechanism. Document why it can or cannot be reused. This precedes new disassembly or patch design.

1. Read `HANDOFF-CURRENT.md` completely.
2. Identify the protected HW baseline and its exact hashes.
3. Read the relevant reconstruction/source under `tools/`.
4. Search this repository's findings and preserved family-source notes before redisassembling known territory.
5. Consult available SF2000/GB300/DY-family/HC-RTOS source where the mechanism is inherited or analogous.
6. Close each OPEN control-flow/ABI assumption with BIN, SRC, or explicitly bounded UP evidence.
7. Update the source/reconstruction so it describes the intended emitted machine code.
8. Use a deterministic fail-closed builder. It must verify baseline SHA, original patch-site words, cave/range ownership, output bounds, and final LCFG seal.
9. Generate a byte-diff manifest from baseline to candidate and explain every changed region.
10. Only then authorize a hardware test.

If a candidate requires a hook whose ownership or continuation is still OPEN, **do not emit it**.

## Source preservation requirement

Every executable helper or firmware patch must be reproducible from repository content.

For each modification preserve:

- source or annotated assembly;
- runtime addresses and ABI/register assumptions;
- exact displaced instructions and continuation targets;
- builder/patch script;
- input baseline SHA-256;
- output SHA-256;
- LCFG payload size and CRC;
- byte-diff manifest;
- family/upstream source provenance used;
- HW result after testing;
- negative results and why they were rejected.

Binary-only ZIP evolution is prohibited as the development model.

## Family-source policy

When compatible family source exists, use it aggressively but classify it as UP until XGO correspondence is established.

For every family source used, record:

- repository/project;
- commit SHA/tag;
- exact file path;
- relevant function/symbol;
- what behavior it demonstrates;
- corresponding XGO BIN address/symbol, if known;
- differences or unresolved assumptions.

When practical, preserve the relevant source file or a reconstruction derived from it in the repository with provenance. Do not rely only on a URL that may disappear.

## Hardware-cycle gate

Hardware should answer a narrow question that cannot reasonably be closed offline.

Do not use hardware cycles to discover:
- whether a branch target was guessed correctly;
- whether a shared frontend path is actually selector-specific;
- whether displaced instructions were preserved;
- whether a candidate was resealed;
- whether a source reconstruction and emitted bytes disagree.

Those are offline failures.

## Handoff durability

Every active branch must keep `HANDOFF-CURRENT.md` current enough that a fresh chat can continue without relying on conversational memory.

Before a chat/session transition, record:

- active branch;
- exact protected baseline;
- last HW-positive checkpoint;
- rejected tests and causal lesson;
- current OPEN items;
- exact next research task;
- files that are authoritative source;
- files that are pseudocode only;
- forbidden/rejected hooks;
- whether a hardware candidate is currently authorized.

The handoff must point to source, not merely test ZIP names.

## Refresh-selector incident / Test113–117

Test113 is the last positive UI checkpoint:
- Setup opens;
- Refresh Games renders cleanly;
- all eight rows navigate;
- frontend remains responsive;
- selecting a Refresh option closes the transient selector;
- B exits Setup but leaves selector state resident, so reopening Setup resurfaces Refresh Games.

Rejected:
- Test114: patched an assumed B exit seam; HW showed no effect.
- Test115: routed an assumed selector-exit helper; HW showed no effect.
- Test116: cleared state inside a stock/global B path and then continued stock B; Setup closed and selector state behavior remained wrong.
- Test117: globally intercepted `0x80356C68`; Setup hard-locked. This violated the selector architecture's explicit no-global/custom-B-hook constraint.

These tests are evidence, not development bases.

**Current rule:** return to Test113/Test106 source reconstruction. No Test118 until the selector's B-cancel seam is source/BIN-pinned and the deterministic builder emits the complete selector from the protected baseline.

## Current Refresh source gap

`tools/refresh_selector/selector_module_v0.S` already defines the intended cancel semantics:

`selector_active=0; refresh_command=-1; MENU_REDRAW`.

However, the exact stock state-14 path that should invoke this selector-specific cancel is still OPEN. The assembly labels this continuation OPEN, and the current builder is audit-only.

Therefore the immediate engineering work is:

1. recover/pin the stock state-14 B dispatch path from Test106;
2. compare it with preserved family/upstream menu/input source where applicable;
3. determine a selector-local interception/dispatch point that does not modify shared frontend B handling;
4. update `selector_module_v0.S` from pseudocode to instruction-pinned source;
5. convert `build_selector_candidate.py` into the deterministic emitter;
6. produce and review the complete diff manifest offline;
7. only then create the next hardware candidate.


## Reuse-first amendment — 2026-09-21

The Test120/Test121 Refresh presentation regressions exposed a process gap: preserving source is insufficient if later work does not consult it before designing a patch.

Therefore the reuse preflight in `docs/REUSE-FIRST-ENGINEERING-INDEX.md` is mandatory. In particular, UI work must compare Mapper v19, Mapper v16 stock-layer suppression, Test05b/Test06 Setup repaint source, Audio OSD framebuffer work, and the current protected selector before new renderer code is authorized.

Test119 remains the protected Refresh checkpoint. Test120 and Test121 are rejected HW evidence, not development bases.
