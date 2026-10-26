# Hardware result — Polish 01 paged OLED: smooth extended SFII gameplay, no missed inputs noticed

**Date:** 2026-10-26. **Branch:** `research-gp2040ce-xgo-integration`.
**Category:** [HW] owner's observation; [SRC/BIN] precompiled firmware build provenance; [OPEN] remaining ghost inputs / rare LP/MP repeat cause.
**Status:** **HARDWARE-POSITIVE INITIAL TRIAL**, *not* global perfection and *not* a fix for phantom P2 inputs.

## Owner's direct report

The owner installed the newly supplied **Polish 01 paged-OLED firmware** package (transparent physical input, XGO GOLD host and Frankie V2 Jr unchanged) and reported verbatim:

> "the new firmware works, I don't see any missed inputs. If I hold the lp or mp buttons i get some sporadic repetitions. notning major. Beated all opponents until the bonus car adn broke it with 3 secs to spare"

Interpretation:
- [HW] New firmware **boots and works for gameplay**.
- [HW] The owner reports **no missed inputs noticed** during this session. This is a successful targeted acceptance observation for the earlier Core0 full-frame OLED blocking problem, not a formal statistically quantified zero-missed-input guarantee.
- [HW] Holding LP or MP can still produce **sporadic repetitions**, described as minor. The owner did **not** say there were unexpected *different button identities* on this particular firmware test, and did not quantify repetition count/timing. Do not invent a cross-button mixing result.
- [HW] Sustained **Street Fighter II** gameplay progressed through the opponents to the bonus car; the car was destroyed with **three seconds remaining**. Strong positive evidence that controls remain practically usable and input response is improved under realistic gameplay.
- [OPEN] This report **does not say whether spontaneous P2 ghost/Contra jumps were observed on Polish 01**, because the user did not mention that test or outcome. **DO NOT mark phantom-input issue fixed**.
- [OPEN] No oscilloscope trace, GPIO host-decoded state, actual loop frequency, or explicit quantified input loss was measured in this session.

## Which exact artifact was tested

**From preceding distribution context**, the named trial is `XGO-Controller-Polish-01-Paged-OLED-With-Rollback.zip`, whose paged-OLED diagnostic firmware was previously compiled as:
- **Paged OLED RP2040 UF2 SHA-256** `5dcc28132ca54293a3d27dc2a452269bc47a1e7f141bd49c2c7e296918071b5b`;
- Original transparent controller rollback UF2 SHA-256 `94ea7228c774a67e8252e7e09d94938530e5d74572d985332e6840ae09fe8b84`;
- Original transparent controller C++ source immutable Git blob `cccb985a05baa8bb9078b6e336eb5f991c1a7a8f`;
- New paged OLED `tiny_ssd1306.cpp` Git blob `e441ecc441a1d495413fbd56171a9a72e7321883`.

The prior full linked build and tests [CI #40107598214](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40107598214) PASS; [OLED C++ regression #40107598212](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40107598212) PASS. Paged code sends at most one I2C page per Core0 input loop, rather than blocking an entire screen transfer each loop, while leaving responder source unchanged. The owner did not independently report a flash-readback hash; link to the packaged build by preceding context, not re-proven device bytes.

## Baseline decision

**Promote Polish 01 to a user-HW-positive *input-latency candidate***, superseding its former label `HARDWARE-UNVERIFIED` in investigation reports, without editing archived UF2 metadata or renaming immutable build artifacts. It is **not** a verified perfect electrical transport or a ghost-input fix.

Keep immediate rollback to original transparent A and do NOT touch XGO GOLD `bios/bisrv.asd` SHA-256 `75f858b6d9a1eb81235ae9e9c9b449a6a3052ad4365e5411b8ce041075e99d6b`, special Frankie V2 Jr pad-2/pad-4 bridge, or RP USB PHY pull-up configuration.

**Prior user hardware result retained separately:** on the earlier transparent A, idle P2 ghost actions were connection-dependent (present connected, absent disconnected, present on reconnection). This new Polish 01 SFII playthrough does not update that specific test outcome.

**Next scope:** polish remaining intermittent hold/repetition and physical ghost inputs **without undoing successful paged-OLED responsiveness or introducing per-game patches, blind resistors, GPIO pull-up overrides or repeated diagnostic builds**. Any claim of rare repeat improvement should be supported by behavior on *the same Polish 01 build* and distinguish normal held-input game/autofire semantics from wrong physical serial bits.

## Supporting materials

- [Original paged-OLED bottleneck and compile/ELF audit](OLED-PAGE-LATENCY-AND-CONTRA-JUMP-2026-10-24.md).
- [Connected/disconnected/reconnected phantom P2 observation](2026-10-26-HW-HANDLE-CONNECTION-A-B-A-GHOST-DEPENDENCY.md).
- [User's universal controller-reliability requirement](2026-10-26-CONTROLLER-RELIABILITY-IS-THE-OBJECTIVE.md).
