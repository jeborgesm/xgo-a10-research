# Offline analysis: attack pulse lifetime vs serial failures (Test44)

## Observed source behavior
In Test44 `XGODriver.cpp`, Core0 captures attack rising edges into `pending_press_edges`. Core1 takes pending edges using `exchange(0)` **before** attempting a 12-slot transaction, starts an 18,000 us wall-clock pulse, and clears it on a subsequent LOAD transaction when elapsed time reaches 18 ms. The serial transaction's `complete` status does **not** govern edge consumption or pulse expiry. In particular, a failed transaction does not restore consumed pending bits. Comments claiming that a failed transaction cannot acknowledge the press are not implemented by the code.

## Mechanism and limits
A rising edge can therefore be consumed at the beginning of a failed serial frame, with the 18 ms pulse counting down during later failures and idle time. The game may never sample a completed frame containing the attack. This is a **source-confirmed vulnerability**, not proof that it explains every missed kick. The 18 ms window is also not synchronized to the game's polling; merely requiring one successful frame is not necessarily sufficient to guarantee that the game saw it.

## Next candidate design constraints
- Controller-only; no XGO-side modifications.
- Preserve physical rising-edge latching and no repeats for arbitrarily long holds.
- Preserve Test44 18 us CLOCK timeout as controlled baseline.
- Do not acknowledge or age out a pending press solely because a failed serial frame began.
- Distinguish failed-transaction retries from normal intentional press pulse; do not let an event persist indefinitely or generate an extra attack on a long hold.
- Design an explicit bounded, host-visible delivery window that starts on a completed transaction, with failure retry behavior and observable counters, before preparing hardware firmware.
- Carefully handle a new physical press arriving while a previous pulse is active; avoid mixing attacks.

## Hardware context
Test44: car destroyed with one second remaining, occasional apparent missed kicks, stable direction, no repeats on held attacks. OK2600 ERR58 CLK52 REL13. Test42 is protected responsive rollback.
