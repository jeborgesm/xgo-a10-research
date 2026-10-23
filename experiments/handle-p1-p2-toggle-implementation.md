# Handle P1/P2 toggle — implementation boundary (2026-10-21)

## Already proven
The fixed-P1 patch in `findings/handle-interface-p1-hardware-pass-20261021.md` runs on hardware, including native menus. Keep SHA `8a8cf7a84f7771b0fc116b80521e13d3dfbd5aace73e6053fb7494eaa7d44c4a` immutable.

## Required runtime behavior
- Mode=0: stock: P1=local serial P1|RF P1, P2=Handle serial P2|RF P2.
- Mode=1: experimental: P1=(local serial P1|Handle serial P2)|RF P1; P2=RF P2.
- Only one physical external Handle port; RF unavailable on this specimen.
- Default mode 0, until a deliberate UI action changes it. Persistent setting is a later milestone.

## Hook placement
Original merge at file offset `0x35D53C`; HW-positive fixed helper at `0xA398E4` (44 bytes). The existing helper is *not* a general-purpose spare area: only four zero bytes follow it before nearby nonzero pointer tables. Do not expand it into the table.

Recommended next patch: keep the existing entry hook and redirect its helper to a *separately verified executable* extension; on mode=0 execute displaced stock OR+ANDI and return; on mode=1 run existing HW-positive conditional P1/P2 logic. Preserve a3/s4/a2/s2/t0 and all live registers, plus MIPS branch delay slots. Verify every modified instruction.

## Mode state and UI
A zero-filled firmware file offset is NOT automatically a writable runtime global. Select an independently mapped writable initialized/BSS global, verify all reads/writes and initialization, and prove it is not occupied by existing features. The native Setup UI needs a deliberately identified action seam; avoid intercepting a gameplay button chord as an unannounced toggle. State should be visible to the user (P1/P2 label), and both transitions tested in menus and gameplay.

## Binary scan observation
A scan of the hardware-proven firmware shows numerous zero runs in `0xA3A000..`, but these occur amid other nonzero content; **zero runs alone do not establish safe executable caves**. The tested helper at `0xA398E4` is HW-positive; other allocations require evidence. Do not create a hardware ZIP on the strength of zero runs alone.

## Acceptance and regression
1. Cold boot defaults to Handle=P2 and built-in=P1.
2. Change to P1 in Setup; external controller navigates menus and controls Ryu; built-in P1 remains usable.
3. Change back to P2; external controls P2 again; local remains P1.
4. Restart; default behavior per explicit persistence policy.
5. CRC-32/MPEG-2 reseal; exact baseline hash, allowed-byte manifest, executable-region audit; recovery ZIP includes HW-positive fixed-P1 binary.

Status: **design gate, not a completed toggle**.
