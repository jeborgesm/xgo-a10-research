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
