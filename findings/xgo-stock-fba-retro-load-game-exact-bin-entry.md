# XGO stock FBA retro_load_game — exact BIN entry anchor

Date: 2026-09-26
Branch: research-arcade-refresh-four-family
Status: BIN anchor recovered. No hardware candidate authorized.

## Exact XGO callback identity

Existing direct XGO disassembly already closed the arcade callback-install block at 0x80360870..0x80360964.

The stock arcade wrapper installs:

gfn_retro_load_game 0x80c33acc <- 0x8036d658

Therefore 0x8036d658 is the exact XGO stock FBA retro_load_game entry used by the native arcade path.

This is BIN, not an upstream approximation.

The same function has already been independently recognized by its load-time behavior:
- stock audio constants 22050 Hz / 367 samples;
- framebuffer allocation and setup;
- transition into the stock FBA runtime.

## Why this matters to Test04

The current Refresh investigation can now stop treating driver selection as an unlocated generic FBA behavior.

The exact function receiving the preprocessed game/content state is known:
0x8036d658.

The relevant chain is therefore bounded as:

stock run_game preprocessing
  -> native Arcade/FBA dispatch
  -> gfn_retro_load_game
  -> 0x8036d658
  -> driver selection/archive opening/ROM resolution
  -> FBA initialization

Known frontend state before this boundary includes the persistent current archive filename component used in the stock "%s/bin/%s" path construction.

For Test04 that state is expected to resolve from the wrapper trailer 1941.zip; for the known-good comparator it resolves from dino.zip.

## Classification correction

Prior notes described the source-family driver-selection algorithm as SRC/UP with matching BIN diagnostics. That remains correct.

What is newly BIN-closed is the exact XGO retro_load_game entry address and callback installation.

The instruction-level short-name scan inside 0x8036d658 remains to be recovered before promoting that internal algorithm to BIN.

## Immediate offline task

Disassemble / recover the 0x8036d658 function neighborhood from the exact bios/bisrv.asd and identify:
- the game-info/path pointer dereference;
- basename/extension stripping or short-name preparation;
- driver-table iteration/comparison;
- nBurnDrvActive write;
- "Cannot find driver" diagnostic xref;
- call/transition to archive parsing.

Then connect those operations to the already-mapped frontend archive-name globals.

No Test05 authorized.
