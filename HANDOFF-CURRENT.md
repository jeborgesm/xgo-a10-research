# XGO Archeology — authoritative new-chat handoff: CPS1 family stock-FBA pivot

Date: 2026-09-05
Active branch: `research-post-mapper-runtime`

## NEW-CHAT BOOTSTRAP RULE

When continuing XGO Archeology in a new/rolled-over chat:

1. Read this handoff from GitHub FIRST.
2. Treat GitHub branch history/findings as authoritative project state.
3. Conversation memory is supplementary only.
4. Do NOT reconstruct the CPS1 story from chat summaries.
5. Do NOT resume A68K per-ROM bisection unless family research produces a concrete mechanism requiring it.
6. Commit research/code/hardware results before advancing to the next experiment.

## Current project direction

We have deliberately pivoted from “replace stock CPS1 with an external core” to:

> **Family-wide stock-FBA comparative archaeology and optimization.**

Research target:
- XGO stock arcade/FBA
- SF2000 stock arcade/FBA
- GB300 v2 stock arcade/FBA
- other HC15xx-family firmware where useful

Goal:
identify proven vendor/family optimizations and determine whether XGO’s stock CPS1 implementation can be improved by understanding/transplanting:
- CPU backend choices
- CPS1 speed hacks
- frameskip/frame pacing
- audio timing/sample rate/synchronization
- scheduler/runtime integration
- later-family fixes
- driver/config differences

Do not assume an external emulator is superior. Family evidence indicates stock arcade is unusually optimized and difficult to beat.

## Why we pivoted

Hardware and family evidence now agree.

### XGO hardware

Stock XGO CPS1:
- functional
- generally best-performing baseline
- can become laggy

External FBA2012 / Musashi:
- corrected content handoff works
- SFII reaches CPS1 self-test
- stalls inside/under first `BurnDrvFrame()`

External MAME2000:
- boots and reaches gameplay
- controls repaired
- adaptive frameskip tested
- still slower than stock
- abandoned as primary replacement

External FBA2012 / native-MIPS A68K:
- intended as faster 68000 backend
- legacy register-context ABI defect found and repaired
- nevertheless stalls during second ROM-load pass before A68K CPU execution
- zero-I/O probes localized stall into first half of SFII 68000 program-ROM loading
- further ROM-by-ROM bisection is paused because it no longer serves the highest-value project goal

### Family research

SF2000 Multicore / sibling-family evidence indicates Arcade is the notable stock emulator without a clearly better multicore replacement. MAME2000 performance on related hardware is reported worse than stock FBA, matching our XGO hardware result.

Conclusion:
**study the stock family FBA implementation instead of blindly replacing it.**

Primary decision record:
`findings/family-wide-arcade-emulator-research-and-decision.md`

Commit:
`27146930334267e57e0baf5ad532239e33f1208a`

## External CPS1 progression preserved for reference

- Test08 — FBA2012 content path fixed; SFII reaches self-test.
- Test09 — input polling ruled out; FBA stalls in first frame.
- Test10 — MAME2000 boots/plays.
- Tests11-13 — MAME input/state/performance work; ultimately slower than stock.
- Test14 — FBA2012 native-MIPS A68K; Loading hang.
- Test15 — A68K legacy ABI repaired; Loading hang remains.
- Test16 — trace localized failure after `CpsInit()`, before `CpsRunInit()`; A68K had not executed.
- Test17 — deep `Cps1LoadRoms(1)` instrumentation; filesystem tracing itself proved invasive.
- Test18 — direct stock-FS trace also perturbed startup; filesystem tracing abandoned.
- Test19 — zero-I/O forced return after `Cps1LoadRoms(1)`; device remained on Loading.
- Test20 — immediate forced failure inside load pass produced Loading -> black -> freeze, calibrating visual reachability.
- Test21 — forced return after full 68000 program-ROM phase not reached.
- Test22 — forced return after first two SFII program-ROM pairs not reached; A68K path stall localized to first half of program-ROM phase.

Test22/decision-gate record:
`findings/hardware-test-22-first-half-program-rom-stall-and-decision-gate.md`

Commit:
`8027df53162320cc28a1a65d61fe6116e40017a7`

## Important earlier authoritative handoff

`findings/cps1-test17-authoritative-handoff.md`

This preserves the exact FBA -> MAME -> FBA+A68K progression and prevents accidental reinterpretation as stock fallback.

## Protected baseline / guardrails

Preserve unless an explicit experiment says otherwise:
- Mapper v19
- external NES work
- Snes9x2005 integration
- external-core runtime infrastructure
- stock CPS2 / IGS / Neo Geo fallthrough
- corrected CPS1 runtime/content-path discoveries

Do not casually replace the full SD package or shared firmware while testing one CPS1 variable.

## Immediate next work — NO HARDWARE TEST YET

Perform comparative family research first.

Suggested sequence:

1. Acquire/identify stock arcade implementation artifacts for XGO, SF2000 and GB300 v2 from existing repository assets/research and trusted sibling repositories.
2. Establish binary/source lineage: FBA version/fork, embedded libretro wrapper, vendor patches.
3. Compare stock CPU backends and MIPS-specific 68000 implementation.
4. Compare frame scheduler, frameskip, audio sync/sample rate and CPS1 timing paths.
5. Search sibling firmware/history for later arcade fixes or performance changes.
6. Produce a concrete diff/hypothesis before building another XGO hardware candidate.

The user explicitly prefers this research-led workflow because related firmware/codebases have repeatedly yielded high-value answers without blind bit-by-bit hardware probing.

## Workflow expectation

The established XGO Archeology workflow is:

```
family/source/binary research
    -> concrete hypothesis
    -> preserve analysis in GitHub
    -> minimal controlled build
    -> hardware observation
    -> commit hardware result
    -> next hypothesis
```

NOT:

```
speculate -> make ZIP -> user swaps files repeatedly -> reconstruct after chat rollover
```

The user values momentum and does not want to re-explain project history after a chat rollover.
