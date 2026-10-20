# Experimental Handle Interface → Player 1 routing

**Status:** EXPERIMENTAL / FUN DERIVED BRANCH  
**Date opened:** 2026-10-06  
**Repository:** `jeborgesm/xgo-a10-research`  
**Branch:** `research-handle-interface-p1-experimental`  
**Derived from:** `research-rp2040-controller-adapter` at `e332656ae6551925efeddf505b5a14bbe882519d`

## Isolation rule

This branch is deliberately derived from the RP2040 controller-adapter work and is **not** the continuation branch for the current RP2040/GP2040 integration effort.

Do not let experiments here alter, redirect, or block the ongoing controller-integration work. The proven native transport and its documentation remain the source baseline. Changes developed here are optional experiments until independently hardware-proven and deliberately promoted.

## Why this branch exists

A side conversation raised a useful/fun possibility: the XGO already accepts the hardware-proven RP2040 responder through the Micro-USB-shaped Handle Interface as **Player 2**. Rather than inventing a new controller protocol or disconnecting the built-in controls, investigate whether firmware can optionally route that already-decoded Handle Interface state into **Player 1**.

The desired behavior is:

- Default/current mode: built-in controls → P1; Handle Interface → P2.
- Optional mode: built-in controls remain active for P1; Handle Interface input is merged into/overrides P1 when external buttons are asserted.
- Do **not** physically disable the local P1 controls.
- Preserve the existing Handle Interface transport unchanged.
- Prefer a simple selectable setting such as `External Controller: Player 2 / Player 1`.
- Default must remain Player 2 so existing behavior is preserved.

Conceptually only (not yet a literal patch):

```text
NORMAL / DEFAULT
local P1 -----------------> P1
Handle Interface ---------> P2

HANDLE-AS-P1
local P1 -----------+
                    +-----> P1
Handle Interface ---+
```

The actual merge operation must respect the firmware's real active-low representation and input pipeline; do not blindly implement a C-style OR from the conceptual discussion.

## Evidence already established before this branch

The RP2040 controller-adapter line has already hardware-proven the important transport question. The XGO Handle Interface is a proprietary five-conductor synchronous controller transport using the Micro-USB physical connector, not USB HID.

The current documented responder contract is approximately 62.37 Hz, 12 active-low slots, with slot order:

`R, Y, X, L, A, B, SELECT, START, UP, DOWN, LEFT, RIGHT`

The native Micro-USB proof established:

- XGO powers the Pico at about 3.15 V.
- Pico native PHY DP carries DATA/load.
- Pico native PHY DM carries CLOCK.
- DP is driven LOW-sink/high-Z.
- The native Contra responder hardware-passed as Player 2.
- The prototype cable has a known mechanical intermittency issue; that is a harness problem, not evidence against the protocol.

Therefore this branch must **not** restart USB/HID or Handle Interface protocol archaeology. Its question is downstream routing inside the XGO firmware.

## Experimental question

Locate the point after Handle Interface state has been decoded/assembled where it is assigned or merged into the firmware's Player-2 state.

Determine whether a minimal, reversible routing selector can:

1. retain the stock/current Handle→P2 path as the default;
2. when enabled, feed Handle state into P1 instead;
3. retain built-in P1 input concurrently;
4. avoid changing the RP2040 responder protocol;
5. avoid regressions to RF/P2 behavior and the cumulative XGO baseline.

## First offline task

Trace the existing input merge/routing path in the protected firmware evidence before creating any hardware-test candidate. Identify:

- decoded Handle state location;
- local P1 state location;
- P2 destination/merge site;
- active-low merge semantics;
- safest persistent or runtime location for a P1/P2 routing flag;
- whether an existing settings/menu mechanism can expose the selector without invasive firmware changes.

Given the recent history of boot-sensitive `bios/bisrv.asd` modifications, do not casually patch firmware merely to test the idea. Establish the routing site and safe modification strategy first.

## Promotion policy

This branch is intentionally playful and experimental. Nothing here becomes part of the protected RP2040 integration line or cumulative XGO baseline merely because it works offline.

Promotion requires explicit hardware evidence and a deliberate decision to carry the feature forward.

## 2026-10-11 — SF900/SF2000 comparison and offline routing analysis

**New user hardware observation [HW, SF2000 comparator, not XGO]:** two eBay SF900 controllers work on the SF2000; the switch on each controller permits controlling P1 or P2. The switch mechanism (wireless pairing identity, receiver routing, or firmware mapping) has **not** been established. This is proof of user-facing controller-role selection on the comparator, not proof that stock XGO already supports that selection.

**XGO evidence [BIN/HW]:** GPIO B15 is the local P1 serial stream; L0 is P2; B7 is shared clock. Both channels serialize the same 12-button encoding. RP2040 native Handle Interface responder already hardware-passed as P2. Thus the safest candidate design is a post-scan logical routing change, not GPIO reassignment or RP2040 protocol changes.

**Candidate routing [INF; not implemented]:** preserve the independent scanner outputs, normalize active-low state to a pressed-button representation, and choose: default P2 = handle, P1 = local; optional P1 = local merged with handle, P2 = no handle contribution. If P2 has other input sources, retain those sources unchanged. Confirm whether local/handle masks are active-low or normalized before choosing AND/OR. Do not confuse the SF900 physical P1/P2 switch with the XGO's proposed software setting.

**Still OPEN:** exact binary instructions/addresses of the post-scan routing/merge; whether P2 has other independent sources; settings persistence; game/menu input consumers; and safe bisrv.asd modification/boot-integrity rules. No firmware has been changed, and no hardware candidate is authorized by this note.

**Next offline action:** inspect disassembly and address maps for the scanner's two output stores and the consumer(s) of those stores, then specify a minimal conditional redirect that preserves stock P2 behavior by default. Keep this branch separate from ongoing RP2040 live-controller integration.

## 2026-10-11 — Pinned input addresses and candidate interception point

Offline review of repository findings `player2-end-to-end-libretro-path.md` and `player2-revisit-and-handle-interface.md` yields these [BIN] addresses (original stock image):

| Function/state | Address |
|---|---|
| Scanner | `0x8035d770` |
| Raw serial P1 / P2 | `0x80c33a48` / `0x80c33a4c` |
| Per-player normalization, serial + RF merge | `0x8035d4c4` |
| Final P1 / P2 | `0x80c33a40` / `0x80c33a44` |
| Snapshot copier | `0x8035e360` |
| Keymap compiler | `0x8035ea38` |
| Libretro callback | `0x8035eb20` |
| Frontend player-index accessor | `0x803526a0` |

The normalizer merges serial and RF per player using OR of *pressed-button* masks. The scanner first converts active-low wire samples into set bits, so post-scan OR is appropriate; the wire-level active-low convention does not imply AND at this stage.

**Preferred hypothesis [INF]:** after scanning but before per-player RF merge, logically redirect `serial_p2` into `serial_p1` under an optional setting: `serial_p1 |= serial_p2; serial_p2 = 0`. The original RF P2 word must remain untouched. Default setting bypasses this transformation. If the UI reads P1 from the shared state snapshot, this could enable frontend navigation as well as gameplay. However, we must inspect call ordering and exact stores to verify a safe interception point and avoid mutating the raw scanner outputs prematurely.

**Artifact check [BIN]:** The available `XGoAnalisis.zip` includes `bios/bisrv.asd` (12,768,452 bytes); bytes at file offsets `0x35d770`, `0x35d4c4`, `0x35e360`, `0x35ea38` match the expected MIPS instruction regions, and the scanner's first 16 bytes match the pinned signature. This establishes that the archive is suitable for deeper offline static inspection; it does not establish boot-safe patching or whether the archive matches the latest protected hardware baseline.

**Next tasks:** disassemble `0x8035d4c4` with the actual MIPS calling convention and identify exact raw/RF loads and writes; inspect the caller sequence to choose a reversible intercept; assess menu setting persistence separately; resolve post-Test100 `bisrv.asd` boot-integrity problem before proposing a firmware candidate. No binary modified.

## Instruction-level checkpoint — 2026-10-11

Source: preserved XGO `bios/bisrv.asd` in the analysis archive; these are stock-image MIPS addresses, not verified offsets in the latest modified firmware.

The two-player normalization function at `0x8035d4c4` uses the serial base `gp-0xd2c`, RF/auxiliary base `gp-0xd0c`, and logical output base `gp-0xd18`. In the player-indexed loop, `0x8035d52c` loads the serial word, `0x8035d530` loads the corresponding RF word, `0x8035d53c` ORs the pressed-button masks, and `0x8035d544` stores the combined state to scratch for translation. Raw serial P1/P2 words are at `0x80c33a48` and `0x80c33a4c` using the documented stock `gp` value.

**Implementation hypothesis [INF]:** in optional Handle-as-P1 mode, transform the two serial words after scanning and before normalization so P1 receives the union of built-in and Handle presses and P2 no longer receives the Handle presses. Do not alter either RF word; default mode must remain byte-for-byte equivalent in behavior. This is not yet a patch or hardware proof.

**Open:** verify scan-to-normalizer call ordering, source-word lifetime, hook space, settings persistence, and boot integrity of any modified `bisrv.asd`. No hardware candidate until those are addressed.

## Offline binary verification — scanner/normalizer call-site caution

Independently opened `bios/bisrv.asd` (12,768,452 bytes) from `XGoAnalisis.zip` and decoded little-endian MIPS words around `0x35d4c4`. Confirmed:

```text
0x35d4f4  2797f2f4  addiu s7,gp,-0xd0c   RF base
0x35d4fc  2795f2d4  addiu s5,gp,-0xd2c   serial base
0x35d508  279ef2e8  addiu fp,gp,-0xd18   logical base
0x35d51c  00003821  move a3,zero         player index
0x35d520  00074080  sll t0,a3,2
0x35d524  01152021  addu a0,t0,s5
0x35d528  01174821  addu t1,t0,s7
0x35d52c  8c940000  lw s4,0(a0)        serial[player]
0x35d530  8d260000  lw a2,0(t1)        RF[player]
0x35d53c  00d43025  or a2,a2,s4       merged pressed mask
0x35d544  ae660000  sw a2,0(s3)       scratch combined
```

This verifies the earlier repository address map against the supplied stock binary. A literal byte search for direct JAL encodings targeting `0x8035d770` and `0x8035d4c4` returned **no matches** in this binary. This is not proof that the functions are unused: possible causes include indirect calls, a different effective load base, and address-mapping conventions. **Do not claim call ordering is closed.** Next analyze surrounding task dispatch, pointer tables, and the firmware's actual virtual/file address mapping. No patch or hardware test.

## 2026-10-11 — Direct binary cross-reference check

Re-read original `bios/bisrv.asd` from the supplied `XGoAnalisis.zip` and scanned for little-endian MIPS `JAL` encodings. Exact direct-call targets `0x8035d770` (scanner) and `0x8035d4c4` (normalizer) have **zero matches** in this image. This does not mean the routines are unreachable; examine indirect dispatch, function-pointer tables, and potential alternative entry points.

In contrast, direct `JAL 0x8035e360` (state snapshot) appears at file offsets `0x3526b4` and `0x35f14c`. Within the normalizer entry, `0x35d4f0` is `JAL 0x8035c6e8`, and the verified per-player pressed-mask merge remains at `0x35d52c` (serial load), `0x35d530` (RF load), `0x35d53c` (OR), and `0x35d544` (store).

**Implication:** do not assert scan-to-normalizer ordering or choose a hook until the task/dispatcher control flow is reconstructed. In particular, absence of a direct `JAL` is not evidence of a safe unused routine. Original image only; not yet a candidate for patching.

## 2026-10-11 — Control-flow correction: scanner reached by branch, not JAL

Direct verification against the supplied original `bios/bisrv.asd` found an important control-flow edge overlooked by the earlier JAL-only search. At `0x8035d514`, instruction word `0x11000096` decodes as `beq t0,zero,+0x96`, targeting `0x8035d770` (the scanner entry). The branch delay-slot instruction at `0x8035d518` must be accounted for. Therefore **the absence of a direct JAL to the scanner is explained at least in part by a conditional branch from the normalization routine to the scanner address**. This is not an indirect-call mystery alone. Other entry/caller relationships still need tracing.

Within the player loop, `0x8035d54c` (`0xac800000`) is `sw zero,0(a0)` and clears the current player's raw serial word after its mask was read and combined with RF. The preceding `0x8035d548` is a conditional branch to `0x8035d558`; `0x8035d54c` is its delay slot and **executes regardless of branch direction** on standard MIPS delay-slot semantics. This makes the scanner-word lifetime explicit: scan populates, normalizer consumes and clears. Do not place a redirect after consumption.

Another branch at `0x8035d504` targets `0x8035d6e0`; inspect both paths and return edges before choosing any patch location. No firmware changes made.

## 2026-10-11 — Controller task state-machine edges (offline verified)

Fresh decoding of the original `XGoAnalisis.zip/bios/bisrv.asd` confirms that the controller code is not a simple linear scan-then-normalize function. Relevant little-endian MIPS branches (file offsets; runtime mapping per prior notes) are:

| Branch site | Opcode | Target | Meaning / caution |
|---|---|---|---|
| `0x35d504` | `bne v0,zero` | `0x35d6e0` | bypasses early normalizer entry |
| `0x35d514` | `beq t0,zero` | `0x35d770` | reaches scanner entry |
| `0x35d6d8` | `beq v0,zero` | `0x35d510` | returns to state check |
| `0x35d6fc` | `beq s0,zero` | `0x35d514` | scanner gate re-evaluation |
| `0x35d758` | `bne a0,zero` | `0x35d510` | state check re-evaluation |
| `0x35d764` | `bne t0,zero` | `0x35d51c` | enters player normalization loop without scanner entry |

Branch delay slots must be modeled, especially `0x35d768: sw zero,gp-0xd08`, which executes on either branch outcome at `0x35d764`. The normalization loop also clears consumed raw serial state in a branch delay slot (`0x35d54c`).

**Design implication [INF]:** no safe pre-normalizer injection point is established yet. There are paths that enter normalization without entering scanner immediately beforehand. Before implementing, construct a control-flow graph across `0x35d4c4..0x35de34`, identify loop invariants and serial-word writes, and check the effect on the RF P2 state. Do not modify the active firmware baseline.

## 2026-10-20: scanner return path verified

Original XGO image verification: the scanner tail at file offset `0x35de10` contains an unconditional MIPS branch back to `0x35d520`, with its delay slot resetting the player index to zero. This establishes a concrete scanner-to-normalization control-flow edge, resolving an important part of the prior call-site uncertainty. A separate path at `0x35d764` can re-enter normalization without executing the scanner first. Its delay slot clears an auxiliary/RF state word, distinct from the per-player serial state clearing in the normalization loop.

The optional Handle-as-P1 transformation remains an inference, not an implemented or hardware-proven feature. Neither the full control-flow graph nor a boot-safe patch location is established. Preserve the protected firmware and active RP2040 work.
