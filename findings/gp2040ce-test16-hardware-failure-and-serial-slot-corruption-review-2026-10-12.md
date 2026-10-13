# Test16 hardware failure and serial slot-corruption review — 2026-10-12

## HW: observed by user
- HK tap triggers MP; HK hold initially MP, later HK.
- HP hold initially MK, later HP.
- MK hold repeats MK and intermittently activates Select/credit.
- MP hold initially LP, later MP.
- LP/LK comparatively reliable.
- Test16 CI passes but **fails gameplay acceptance**; Test14 remains protected.

## SRC: reviewed
- `integrations/gp2040ce-xgo-test01/candidates/test16-offline/XGODriver.cpp`
- `tools/rp2040-xgo-native-contra/main.c`
- `findings/xgo-sf2000-keypad-protocol-equivalence.md`
- `findings/xgo-controller-scanner-binary-signature.md`
- prior Test14 source-order and waveform models.

## Findings
1. Host XGO scanner reads 12 active-low slots in order R,Y,X,L,A,B,SELECT,START,UP,DOWN,LEFT,RIGHT. It samples slot0 after LOAD release and each subsequent slot following clock progression; clock low approximately 2us in stock firmware.
2. Candidate firmware waits for CLOCK-low and then writes DATA for the next slot. This **can** be too late for a host sampling deadline if detection+PHY write+propagation exceeds the available low/high interval. The precise XGO sample instruction relative to rising CLOCK remains to be verified from BIN/disassembly. This is a concrete timing-budget risk, not proof of an observed shift.
3. `wait_clock(level)` detects levels, not transitions; if a pulse is missed entirely, it may time out, and if the call begins while the next phase already holds the requested level it may silently accept the wrong transition. Source has no independent frame slot counter from the host.
4. Mask publication uses a single atomic 16-bit snapshot, so Core0-to-Core1 tearing is **not** a credible explanation for one held bit becoming multiple other bits. Test15/Test16 post-LOAD snapshot changes did not fix hardware symptoms.
5. Test16's final-rise validation only detects some incomplete frames; it does not prove all preceding 12 bits were sampled correctly.
6. The native Contra responder uses the same level waits and timing strategy. It is proof of basic protocol feasibility, **not** proof that the approach has zero marginal timing failures under the GP2040-CE dual-core workload.
7. Select/credit contamination while holding MK strongly favors a cross-slot electrical/serial error or an independent game-input mapping source. The attack substitutions cannot be conclusively mapped to exact bit shifts without establishing the arcade physical-button mapping and an actual host-side capture.
8. Repeated attacks during a held button **alone** do not establish repeated electrical events; the game may implement repeat behavior. Wrong attack identity and Select contamination are the discriminating failures.

## Required root-cause experiment — before another flash
- Recover the exact host scanner's sample-before/after-CLOCK instruction order from preserved `bios/bisrv.asd` around file offset `0x35D770`; identify sample instant and delay loop.
- Disassemble the compiled Test16 Core1 critical path; bound cycles from DM falling detection through DP OE write, and from LOAD release to slot0.
- Simulate sampled masks with realistic per-slot output delays and show which wrong-slot signatures are generated.
- Compare physical one-hot-to-game-button mapping before claiming HK→MP is a particular bit displacement.
- Only then build a candidate that moves DATA at a provably safe phase (potentially pre-staging on the opposite CLOCK phase), with a deterministic rearm rule and no cached input.

## Status
**HW FAILED:** Test16.
**SRC VERIFIED:** level polling and 12-slot write-after-fall implementation.
**INF:** clock-phase timing violation is the leading hypothesis.
**OPEN:** exact instruction-level host sample phase and measured PHY latency.
**DO NOT:** claim that successful firmware compilation or a 4096-mask logical round-trip validates electrical timing.
