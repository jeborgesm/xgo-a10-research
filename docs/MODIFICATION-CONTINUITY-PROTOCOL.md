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


## Mandatory historical-solution recovery gate

Before designing, patching, or hardware-testing a mechanism that resembles a problem previously investigated in XGO Archeology, **search this repository first for a hardware-proven implementation**.

This is a hard engineering rule, not a suggestion:

1. Search findings, builders/source, manifests, golden-artifact records, handoffs, and branch history for the same mechanism or the closest solved analogue.
2. Prefer an existing **HW-proven** mechanism over a newly inferred or merely BIN-compatible implementation.
3. If a new design differs from an earlier HW-proven solution, document why the proven mechanism cannot be reused before producing a candidate.
4. A known ABI or plausible native function is not sufficient reason to replace a preserved HW-proven implementation.
5. Hardware tests should validate a bounded new unknown; they must not rediscover behavior already established and preserved in GitHub.
6. When a test contradicts current assumptions, immediately search historical hardware records before proposing another patch.

### Test124 lesson

Test124 (2026-09-22) demonstrated why this gate is mandatory. A selective call to native scanner `0x807DAE4C` was statically coherent but returned `No New Games` for new GB/GBC/GBA raw ROMs. Repository recovery then found the earlier **Test08 HW PASS**, whose custom table-driven filesystem scanner had already discovered forgotten raw `.gb` files on hardware, appended them to the stock Game Boy catalog, and launched them successfully.

Therefore the correct next engineering action is to reuse/selectively adapt the Test08 HW-proven discovery worker, not continue experimenting with alternative scanner paths.

**Repository-first maxim:** if XGO Archeology solved it before, recover and reuse that solution before inventing another one.


## Mandatory architectural-ancestor selection gate

Before implementing a new system-family variant of an existing feature, do not choose an ancestor by chronology or by the first historical test that touched that system. Build a component-level comparison of the HW-proven implementations and select the closest proven ancestor for each mechanism.

Required comparison dimensions include at minimum: input filename/extension geometry, source/art/meta namespace, generated wrapper contract, materializer behavior, catalog/list identity, live frontend/catalog lifecycle, helper loader/ABI, status/return behavior, and persistence/recovery behavior.

A new candidate must identify which proven ancestor supplies each component and enumerate the exact substitutions. If a mechanism was already solved in a closer HW-proven implementation, reuse that solution rather than reopening an older archaeology path.

Example established by GB propagation: Test74/Test75 supply the enrichment/wrapper architecture, while the HW-positive MD lineage supplies the two-character native-extension geometry and later catalog/frontend lifecycle lessons. Test08 raw discovery is supporting evidence, not the architectural parent for enriched GB import.


## Chat-disruption recovery contract — 2026-09-29

This section is mandatory after any forced/new chat, context compaction, model handoff, or other conversational disruption. Conversation continuity is never allowed to become the project continuity mechanism.

### Bootstrap order

Before technical work resumes:

1. identify the active branch;
2. read `HANDOFF-CURRENT.md` completely, including later superseding checkpoints;
3. read this protocol and `docs/REUSE-FIRST-ENGINEERING-INDEX.md`;
4. inspect the applicable branch findings, deterministic builders/source, `artifacts/golden-artifacts.json`, private artifact repository, and latest HW-result commits;
5. recover any immediately preceding chat-only HW observation or correction and commit it before building on it;
6. establish the exact protected baseline and last HW-positive checkpoint;
7. only then resume the current OPEN boundary.

Old handoff text is historical evidence. A later explicit correction or HW checkpoint supersedes it where they conflict. Never resurrect an obsolete priority merely because it appears earlier in a long handoff.

### Interaction contract

When the user says **go** or **continue**, that is authorization to continue the offline investigation autonomously through ordinary searches, disassembly, comparisons, source repair, deterministic reconstruction, audits, and repository commits. It is **not** a request for incremental narration.

Do not return to the user merely to report:
- that a search or commit was performed;
- that one hypothesis was rejected;
- that a file was repaired;
- what could be investigated next;
- a short progress/status update after a few seconds;
- a request to say `go` again.

Continue until a meaningful gate is reached:
- a fully audited hardware candidate is genuinely required and ready, with exact artifact/hash/instructions; or
- a substantive offline closure materially changes the investigation and no immediate offline continuation remains; or
- an indispensable user-owned artifact/input is required and cannot be recovered from repository/artifacts.

### Hardware gate

A new hardware request is forbidden unless all of the following are explicit in the repository:
- the exact unresolved question;
- the HW-proven ancestor;
- exact recovered source/binaries and provenance;
- relevant prior positive and negative experiments;
- why offline evidence cannot answer the question;
- deterministic candidate construction;
- complete mechanical byte/file delta audit;
- hashes/manifests and expected observations.

Do not use a hardware test merely to separate hypotheses that can still be separated offline. Do not create speculative numbered-test ladders.

### Evidence and archival invariants

- HW outranks BIN/SRC/UP/INF.
- BIN/SRC/UP/INF never silently become HW.
- Failed tests and disproved interpretations remain preserved as evidence.
- Corrections are appended/pinned; history is not silently rewritten.
- Every important finding/status must reach GitHub; chat-only state is a workflow defect.
- Every meaningful HW-test ZIP is archived; only HW-confirmed milestones may become golden.
- Verify artifact identity/hashes and internals; filenames are not provenance.
- Recover proven implementations instead of reconstructing them from memory.
- Preserve cumulative HW-proven behavior and keep experiments subsystem-local.
- Mechanically audit resulting binaries/packages, not merely intended source changes.

### Durable maxim

`Recover -> establish provenance -> compare offline -> smallest evidence-driven delta -> mechanically audit -> hardware-test one unresolved boundary -> record exact HW result -> archive -> commit -> promote only after HW proof.`

Absolute prohibitions:
1. Never reconstruct a proven implementation from memory when it can be recovered.
2. Never ask hardware a question offline archaeology can answer.
3. Never let an inference outrank an observation.
4. Never allow important project state to exist only in a chat.
