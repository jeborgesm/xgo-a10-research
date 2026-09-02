# Hardware Test 08 — Stage 6 interpretation correction

The initial interpretation of the six-stage return ladder was too strong.

Observed hardware result:

- Stages 1-5 return to the game menu.
- Stage 6 remains frozen on `Loading...`.

Stage 6 differs from Stage 5 by writing `GAME_INFO`, installing external-core pointers into the stock `GFN_*` slots, and configuring controller ports. Its checkpoint then executes a direct `return 0`.

## Test-harness flaw

The direct Stage 6 return does **not** restore the stock globals that were overwritten immediately before it:

- `GAME_INFO`
- `GFN_STATE_LOAD`
- `GFN_STATE_SAVE`
- `GFN_GET_REGION`
- `GFN_GET_AV`
- `GFN_LOAD_GAME`
- `GFN_UNLOAD_GAME`
- `GFN_RUN`
- `GFN_FRAMESKIP`

Therefore a Stage 6 freeze does not prove that execution failed before the checkpoint. It may have reached and returned from the checkpoint, after which stock menu/control flow resumed with external-core pointers and modified content info still installed.

Stages 1-5 remain valid positive evidence because they return before these persistent stock-global mutations.

## Revised experiment

The Stage 5→6 window must be subdivided with **transactional checkpoints**: each probe may perform one additional group of operations, but before returning it must restore every stock global modified by that probe.

Proposed boundaries:

- 5A: write `GAME_INFO`, restore it, return;
- 5B: write `GAME_INFO` + `GFN_*`, restore both groups, return;
- 5C: additionally configure controller port 0, restore stock globals, return;
- 5D: additionally configure controller port 1, restore stock globals, return.

Controller configuration mutates FCEUmm internal state rather than stock firmware globals, so it does not need stock-state restoration for the menu-return observable.

The prior finding `hardware-test-08-return-ladder-boundary.md` should be read together with this correction; its claim that Stage 6 necessarily failed before its deliberate return is superseded by this note.
