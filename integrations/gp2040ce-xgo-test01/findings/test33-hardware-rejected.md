# Test33 hardware verdict — REJECTED (2026-10-15)

## HW: user observations (Street Fighter II)

> test 33 failed. even hk is sending hp, tapping mp makes lp and mp, HP is making lk and hp, mk, does mk and coin, hk doeslp- and mp and occasionally hk. a mess

Recorded without smoothing away the contradictory reports:
- HK was observed to produce HP.
- MP tap produced LP and MP.
- HP produced LK and HP.
- MK produced MK and Coin.
- HK also produced LP and MP and only occasionally HK.

**Verdict: hardware-negative, severe cross-button/phantom-input regression.** Do not promote or flash Test33 again as a proposed fix. No evidence the per-button windows improved HP→MK.

## Baseline and next steps

- Preserve Test32 (run 38798316411, artifact 12003102743) as best hardware-validated controller firmware: all six taps respond, hold repetition gone, playable, occasional HP→MK remains.
- Preserve Test28 as original serial-timing baseline.
- Test33 changed shared attack pulse state to per-button pulse state, keeping nominal 24 ms window and serial timings; **causality of the newly observed cross-input corruption is not established**.
- Next investigation should inspect the exact serial waveform/slot handling and event-state semantics offline before another candidate. Do not modify XGO BIOS, emulator, or game mapping. Do not treat Test33 as a partial pass.
