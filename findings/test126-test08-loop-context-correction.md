# Test126 follow-up — Test08 loop context is part of the proven mechanism

Date: 2026-09-22
Branch: `research-refresh-gb-gbc-gba`

Status: **scope correction before next implementation**

## User observation that changes the comparison

Test08 was not a selective per-emulator entry point. Its HW-proven behavior was
one invocation that iterated the console systems in sequence:

`FC -> SFC -> MD -> GB -> GBC -> GBA`.

The forgotten raw GB files were discovered while that single scanner was
already progressing through the earlier systems.

Test125/Test126 changed two dimensions at once:

1. six-system loop -> one-system worker;
2. firmware-resident scanner -> externally loaded Stage2 helper.

Therefore an instruction comparison that treats a Test08 per-system pass as an
independent callable ABI would be invalid. The loop's carried state and
per-iteration initialization/restoration must be recovered first.

## Consequence

The next design must not assume that extracting the GB/GBC/GBA body from
Test08 preserves its semantics. We need to distinguish:

- state initialized once at Test08 Refresh entry;
- state reset at the top of each system iteration;
- state intentionally carried from one system to the next;
- classifier/global state saved/restored per iteration versus once for the
  whole six-system run;
- list ID / folder / resource-table / count-cache derivation from the loop
  variable;
- scratch and candidate buffers reused between iterations.

Only after that separation can we implement independent command 3/4/5 safely.

## Preferred reuse direction

If Test08 proves that important state is loop-scoped rather than system-local,
prefer preserving the HW-proven generalized scanner engine and adding a
**selected-system start/end bound** (or selected-ID parameter) rather than
maintaining three separately reconstructed workers.

That would keep the proven scan/merge mechanism intact while changing only the
iteration range:

- command 3 -> execute generalized engine for GB only;
- command 4 -> GBC only;
- command 5 -> GBA only.

This is preferable to copying/reconstructing the worker three times if the
exact Test08 binary supports a bounded-loop adaptation.

No Test127 candidate until the exact Test08 loop state is decoded and this
choice is evidence-driven.
