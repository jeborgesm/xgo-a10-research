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
