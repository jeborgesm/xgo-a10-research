# Test45 — offline-only candidate, NOT BUILD/FLASH READY

Derived from Test44, 18us CLOCK timeout unchanged, 18ms attack pulse unchanged. New attack delivery state: the 18ms timer starts after the first **complete** serial frame carrying the press; failed frames do not consume the timer. Undelivered pulses have a 100ms wall-clock retry cap to prevent indefinite assertion if the host fails. Physical rising-edge acquisition remains Core0-only; long holds do not themselves generate fresh events.

## Open engineering issues before build/hardware
1. A completed serial frame is not proof that the game sampled it. Need assess pulse duration vs game poll.
2. `pending_press_edges` is a bitmask; repeated press-release-press of same button during an active pulse coalesces. This predates Test45 and is not solved here.
3. Retry cap can discard an attack if serial communication stays broken for >100ms; cap is an explicit safety trade-off, not a guaranteed delivery mechanism.
4. The current code may queue pending presses while a pulse is active and deliver them after it expires; verify that no repeats occur on holds and no phantom press occurs on fast tapping.
5. Source-level inspection and build validation pending. Do not flash or present this as a tested fix.

## Test objective
Compare against Test44 at the same Street Fighter II car-stage save point and same kick sequence. Require stable direction, no repeats on held attacks, no mixed attacks, fewer missed kicks, and a car completion time at least as good as Test44 (one second remaining). Keep Test42 and Test44 intact.
