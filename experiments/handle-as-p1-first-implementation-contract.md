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

## 2026-10-20 — Physical XGO constraint and corrected acceptance criteria

**User hardware clarification [HW]:** The physical XGO has only one usable external-controller connection, the Handle Interface. There is no available RF controller input on this specimen. In Handle-as-P1 mode, P2 is intentionally uncontrolled; do not require a second controller or preservation of a functional RF P2 path.

**Updated user-visible behavior:** default: built-in controls P1 and Handle controls P2. Experimental: built-in controls and Handle both control P1; P2 receives no user-operable input. A theoretical RF state remains visible in stock firmware analysis [BIN], but it is not an available physical input on this XGO [HW].

**Engineering caveat:** avoid gratuitous writes to legacy RF state or changing its initialization, even though RF P2 is not an acceptance requirement. The design may leave that dormant state unchanged internally. The P2 zero-input expectation assumes the unavailable RF path is inactive; verify actual effective P2 state during the eventual hardware test.

**Revised tests:** P1 mode must allow built-in and Handle controls simultaneously, P2 must not respond to Handle, and default mode must restore proven Handle-as-P2 gameplay. No requirement to test or attach RF controllers.

## 2026-10-20 — Verified two-player iteration and serial-clearing exception [BIN]

Direct inspection of original archived firmware:

- `0x35d51c`: `move a3,zero`; `0x35d520`: compute index*4 in `t0`; `0x35d524`: serial word address = `s5+t0`.
- `0x35d52c`: load serial word to `s4`; `0x35d530`: load same-player RF word to `a2`; `0x35d53c`: OR into `a2`.
- `0x35d540`: test pressed bit `0x20`; `0x35d548`: branch if not set; `0x35d54c`: delay slot always stores zero to current serial word.
- When bit `0x20` is set, `0x35d550` loads 1 and `0x35d554` stores it back to the current serial word, overriding the zero store. Thus the raw-state lifetime has a deliberate special case; **do not claim every iteration always ends with a zero raw word**.
- `0x35d624`: branch to `0x35d638` if `a1==0`; **delay slot** `0x35d628` always executes `addiu s2,a3,1`.
- `0x35d638`: `andi a3,s2,0xff` (index for next pass); `0x35d63c`: `sltiu a0,a3,2`; `0x35d640`: if true, branch to `0x35d524`; `0x35d644`: delay slot recalculates `t0=a3*4`.

This establishes the concrete second-player pass and shows why a routing helper must not disturb `a3`, `s2`, `t0`, the special bit-0x20 state, or the branch delay slots. The XGO hardware constraint remains: one Handle Interface, no available RF controller; default external P2, experimental external P1 with built-in P1 retained. No patch or test image produced.
