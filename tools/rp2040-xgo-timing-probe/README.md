# XGO native timing probe (source only)

Experimental derivative of `tools/rp2040-xgo-native-contra/main.c`. Original hardware-proven Caveman source is unchanged.

## Capture contract

- Records up to 256 **detected** load-start attempts in global `g_samples`; `g_captured` counts records, `g_failed` counts failed edge sequences, and `g_capture_done` indicates completion.
- Each record stores detected load-low-to-release duration, release-to-first-DM-fall interval, frame duration, start-to-start interval, and success flag.
- Records are committed **after** the 12-slot critical edge sequence. No printf, heap allocation, or flash writes are performed in that sequence.
- Once 256 samples are captured, the responder releases DP, stops, and leaves samples in RAM for debugger inspection. If no host load pulses are detected, capture does not complete.
- Values are microsecond-resolution **software observations**, not oscilloscope measurements. The first observed low timestamp occurs *after* detecting low; therefore `load_low_us` underestimates actual low pulse width. Likewise `release_to_first_dm_fall_us` includes sampling overhead. Samples cannot establish guaranteed min/max timing margins or a safe cooperative poll interval by themselves.
- A timeout waiting for load LOW is not stored; failed attempts after a detected load are stored. The LED and phase script are inherited from Caveman, but LED toggles happen outside critical transfer.

## Safety / status

Not compiled, flashed, or hardware-validated. This is **not** GP2040-CE Test02 and must not replace the known-working Caveman UF2. An independent code/build review is required before any optional instrumented-hardware experiment.

## Before testing

1. Confirm compiler, SDK and board target match the Caveman build; perform compile/static review.
2. Confirm USB DP/DM wiring and safe power arrangement; use the same validated Caveman setup only.
3. Verify debugger access to volatile `g_samples` without modifying timing-sensitive loops.
4. Compare observed sample distribution and failure counts against the uninstrumented responder, not just one successful sample.
5. Prefer external logic-analyzer/oscilloscope measurements for host load pulse width and slot0 deadline.

## Why this probe exists

GP2040-CE core0 and core1 both have existing work. Shortening a blocking 20 ms wait or relocating it to `processAux()` could miss the host's load edge. This probe provides an evidence path without modifying the protected Test01 integration or claiming that a specific scheduling architecture is already safe.
