# Held-button investigation after protected Test27

## Offline inspection: timing boundary

The Test27 Core1 responder changes DATA for slots 1..11 **after** observing CLOCK low, and only then waits for CLOCK high. This is consistent with a host that samples after the rising edge, but it leaves a finite falling-edge-to-DATA-settle interval. A held mask stays constant across scans (published_mask sampled once per transaction), so an incorrect extra attack under a stable hold cannot be explained merely by a changing Core0 snapshot.

At the end of each frame, the responder waits for a final CLOCK low, releases DATA, and waits for CLOCK high. It then loops and waits for LOAD low again. If the host performs another LOAD without an intervening observable DATA-high idle state, distinguishing frame boundary and late CLOCK edges may matter. No physical waveform or simulator result yet establishes that as the cause.

**Important:** A game can generate multiple attacks for one sustained input; wrong *type* of attack (LP/MP or HP/MK mixing) is the unresolved signal. Correct LK and MK repetition rules out an across-the-board hold defect.

## Working hypothesis, not a proven fix

For slot 1 onward, a timing margin problem could create a wrong bit in a scan if DATA settles after the host samples, or if the controller misses a clock edge. However the specific LP/MP and HP/MK pairs must be reconciled with the physical slot ordering before claiming this explanation. A host-waveform model with a full 12-slot held mask, sequential frames, and explicit host sampling times is required.

## Safe next steps

1. Freeze Test27; keep its early-sink HK path intact.
2. Compare MIPS host scanner clock/read instruction ordering against the Core1 `wait_clock(false)` → `data_sink/release` → `wait_clock(true)` ordering.
3. Reproduce stable held-mask transitions in a model and distinguish clock-edge slip from actual game-generated repeat.
4. Only then produce a separate Test28 candidate. No hardware request yet.
