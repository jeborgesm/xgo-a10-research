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

## 2026-10-20 — Exact mask-to-logical translation boundary [BIN]

Fresh direct word-level inspection of the archived original `bisrv.asd` resolves a useful distinction:

- `0x35d52c`: `lw s4,0(a0)` reads the current player's raw serial mask.
- `0x35d530`: `lw a2,0(t1)` reads the corresponding legacy RF mask.
- `0x35d534`: `addu a0,t0,fp` changes `a0` to the per-player logical-output pointer; `0x35d538` sets `s3` to the per-player scratch pointer.
- `0x35d53c`: `or a2,a2,s4` produces the combined pressed mask. `0x35d544` stores that mask into scratch.
- `0x35d540–0x35d620` tests the combined mask's bits and writes logical output flags through `a0`.
- Therefore the `0x35d54c` and `0x35d554` stores are **to the logical-output word pointed to by a0, not to the raw serial word**. Earlier notes describing these stores as serial-state clearing were incorrect and must not be relied on.
- The `0x20` special case writes 1 to the logical-output word after an unconditional zero write. It is not proof that a raw serial word persists.

**Design implication [INF]:** the most relevant interception boundary is before or at the combined-mask calculation, while the normalizer still has the raw serial and RF masks. A Handle-as-P1 helper must merge P2 serial into the P1 combined mask and suppress its contribution to P2 while retaining the built-in P1 mask. This remains an unimplemented hypothesis; the full scratch/output state machine, alternate entry paths, register preservation, and post-Test100 boot integrity remain to be established.

**Evidence correction:** the old phrase 'the two raw serial words are consumed and cleared by the normalization loop' is not established by the cited stores. Scanner-entry clears at `0x35d780` and `0x35d788` are separately verified. Do not base routing on presumed per-iteration serial clearing.

## 2026-10-20 — Minimal routing arithmetic and interception candidate [BIN/INF]

Directly rechecked original firmware words at offsets `0x35d520–0x35d554`: the loop computes `t0 = player_index*4`, reads serial into `s4` (`0x35d52c`) and legacy RF into `a2` (`0x35d530`), switches `a0` to logical output (`0x35d534`), computes scratch pointer `s3` (`0x35d538`), then merges with `or a2,a2,s4` (`0x35d53c`) and writes the resulting mask to scratch (`0x35d544`). These are verified stock operations, not an installed modification.

**Fixed Handle-as-P1 algorithm [INF], evaluated at the pre-merge boundary:**

- P1 (`a3 == 0`): substitute `s4 := raw_serial_P1 | raw_serial_P2`; keep `a2` as current-player legacy RF state; original OR instruction then combines them.
- P2 (`a3 == 1`): substitute `s4 := 0`; keep `a2` unchanged; original OR then emits only dormant legacy RF state. On the physical XGO the user confirms there is no usable RF controller, so P2 is expected to be inactive.
- Default: leave `s4` unchanged and execute the stock OR.

This formulation avoids modifying the serial scanner, existing input translation, scratch/output pointers, or the existing RF merge. It is also independent of presumed serial-state clearing: raw P2 is only read while processing P1. The scanner independently zeroes both serial raw words at `0x35d780` and `0x35d788` before filling them; this does not prove when other writers run.

**Hook engineering gate:** a single replacement of `0x35d53c` is insufficient to implement the conditional logic. Any branch/trampoline would displace adjacent instructions, so its delay slot, register clobbers, exact re-entry, available executable code space, and the protected Test106 `bisrv.asd` boot integrity must all be established first. No code patch or firmware candidate authorized by this note.

## 2026-10-20 — Original image byte verification and container gate [BIN]

Independently reopened the supplied `XGoAnalisis.zip`, reading `bios/bisrv.asd` (12,768,452 bytes). Its first four bytes are ASCII `LCFG` (`4c 43 46 47`); the first 64 bytes also contain `logo.m2v` at file offset `0x18`. Thus the `.asd` is not demonstrably a bare MIPS text blob beginning at offset zero. **Do not infer a particular checksum or integrity algorithm from this header alone.**

The candidate region was checked directly as little-endian 32-bit words: `0x35d52c=8c940000` (load serial), `0x35d530=8d260000` (load RF), `0x35d534=011e2021` (logical output pointer), `0x35d538=01169821` (scratch pointer), `0x35d53c=00d43025` (OR), `0x35d540=30d20020` (bit test), and `0x35d544=ae660000` (scratch store). The proposed pre-merge hook boundary is consistent with these bytes.

**New mandatory gate:** map `LCFG` container layout and executable mapping, compare the exact protected Test106 image and post-Test100 failures byte-for-byte, and establish image-validation requirements before writing a trampoline or test ZIP. The archived original firmware alone cannot resolve the Test106 boot failures. No firmware modified.

## 2026-10-21 — LCFG header boundary and length relationship [BIN]

Reopened the actual supplied archive, not an assumed Test106 build. `bios/bisrv.asd` has 12,768,452 bytes (`0xC2D4C4`), SHA-256 `869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf`.

The first 0x1000 bytes are overwhelmingly zero (57 nonzero bytes), except for header fields near the start and a small record at `0x17d–0x18f`. Notable values: `LCFG` at `0x0`, `logo.m2v` at `0x18`, ASCII `End` at `0x17d`, little-endian word `0x00C2D2C4` at `0x184`, `0x00030000` at `0x188`, and `0x5EE51F11` at `0x18c`. **The length word at `0x184` is exactly the total file length minus `0x200`** (`0xC2D4C4 - 0x200 = 0xC2D2C4`). This is a strong structural relationship, not proof of what the field means. The word at `0x18c` could be integrity-related, but its meaning is not established; do not call it a CRC or checksum without testing.

The executable MIPS instructions at `0x35d53c` remain present as previously verified. No bytes were changed. A future comparison with Test106 and failing Test107/108 should include these header words and any trailer or metadata differences, as well as the actual code patch bytes. **Do not rebuild an image or assume the bootloader rejects edits based only on these header observations.**
