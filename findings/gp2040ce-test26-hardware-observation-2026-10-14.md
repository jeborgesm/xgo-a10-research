# Test26 hardware observation — 2026-10-14

Evidence level: HW (user-reported direct hardware observations); hypotheses explicitly INF.

## HW: activation and display
- SELECT+START+HK displayed an unexpected `Idle Rate 0/10` overlay; repeated HK advanced `1/10`, `2/10`, etc.
- Releasing the combination and pressing HK normally did not consistently start the diagnostic.
- Diagnostic sometimes started at idle-rate values 6/10 or 7/10 (and occasionally others) if HK was tapped extremely quickly after releasing the three-button combination.
- When it started, OLED header advanced through `P1 R1` and subsequent repeats/phases through `P6 R1`.

## HW: gameplay
- Street Fighter II World Warrior produced predominantly Medium Punch rather than Heavy Kick throughout the synthetic HK phases.
- Only rare Heavy Kicks observed; one at the very end of P6 R1 / 10/10. Not reproducible enough to attribute to pulse width.

## BIN/SRC: candidate mechanism
- Test26 `process()` uses SELECT+START+HK as arming chord and HK alone as trigger.
- It publishes synthetic bit 0 only during sequence; Core1 responder/PHY unchanged from Test16.
- Sequencer phases: 1000ms x1, 100ms x5, 50ms x5, 25ms x5, 10ms x5, 2000ms x1, with 2s pre-roll.

## INF: investigation direction
- `Idle Rate` likely belongs to an upstream GP2040-CE hotkey/setting handler; exact origin and interception ordering not yet established.
- Sequencer phase advancement proves Core0 scheduler ran, not that the host correctly sampled bit 0.
- Across-phase MP dominance weakens the hypothesis that ordinary press length alone explains HK failures. Host slot-0 sampling, first-bit turnaround, stream ownership and/or input remapping remain open.
- Next: trace `Idle Rate` string and upstream hotkey processing offline, then examine serial slot0/stream path. Do not infer HK success from one isolated occurrence.

Protected Test16 remains the playable baseline. Test26 is hardware-observed but not accepted as an HK fix.
