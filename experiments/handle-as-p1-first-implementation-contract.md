# Experimental Handle-as-P1 — first implementation contract

**Status:** offline design only, NOT a firmware candidate.  
**Branch:** research-handle-interface-p1-experimental  
**Source:** original `XGoAnalisis.zip/bios/bisrv.asd` (12,768,452 bytes), plus existing RP2040 hardware proof.

## Confirmed stock binary evidence [BIN]

The stock scanner produces two positive/pressed-bit raw serial words:
- P1: `gp-0xd2c` (`0x80c33a48`)
- P2/Handle: `gp-0xd28` (`0x80c33a4c`)

The two-player normalization loop begins with player index zero at `0x35d51c`. It uses:
- `0x35d520`: `sll t0,a3,2` (player index times four)
- `0x35d524`: serial pointer `s5 + t0`
- `0x35d528`: RF pointer `s7 + t0`
- `0x35d52c`: load serial[player]
- `0x35d530`: load RF[player]
- `0x35d53c`: OR serial and RF pressed masks
- `0x35d544`: store combined mask to scratch
- `0x35d548`: conditional branch
- `0x35d54c`: **delay-slot** store zero to serial[player], unconditional with respect to that branch
- `0x35d638`: extract low byte of player loop index from s2
- `0x35d63c`: test index < 2
- `0x35d640`: branch to `0x35d524` when index < 2
- `0x35d644`: delay slot recalculates index*4.

The exact index advancement and register lifetimes need full validation before code generation. The loop uses a mixture of `a3`, `s2`, and `t0` across iterations; do not infer an ordinary C for-loop from the first few instructions.

## Proposed behavioral contract [INF]

Default:
- P1 effective pressed mask = local_serial_P1 | RF_P1
- P2 effective pressed mask = Handle_serial_P2 | RF_P2

Experimental fixed Handle-as-P1:
- P1 effective pressed mask = local_serial_P1 | Handle_serial_P2 | RF_P1
- P2 effective pressed mask = RF_P2
- Both raw serial words still clear on their respective normalizer iterations.

Do not change scanner GPIO or RP2040 protocol. The already hardware-proven Handle-to-P2 transport is the reference.

## Why consumption-boundary routing is promising

The P2 raw word exists before the P1 loop iteration. A conditional read of P2 while computing P1 could merge its pressed bits without mutating the P2 raw word. On the P2 iteration, its serial contribution can be suppressed from the combined mask while preserving the original raw-word clearing side effect. This is a hypothesis requiring full register/control-flow proof, not a safe patch recipe.

## Offline acceptance tests before firmware candidate

1. Decode complete player-index transitions and branch delay slots, including the alternate path into normalization.
2. Identify exact instruction site and register-save/restore obligations; do not overwrite the scanner or corrupt the loop.
3. Prove default mode leaves both players identical to stock across no-input, local-only, Handle-only, RF-only, and simultaneous inputs.
4. Prove experimental mode preserves independent RF P2 and avoids repeated/stuck Handle presses.
5. Verify exact protected Test106 image provenance, executable region mapping, and the known post-Test100 bisrv.asd no-boot issue before generating any test ZIP.
6. First hardware proof should use the existing working RP2040 responder, with a reversible firmware build and protected recovery image.

No firmware image modified; no test requested.
