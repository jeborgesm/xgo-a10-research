# Test44 hardware results — 2026-10-20

## Candidate
Controller-only GP2040-CE experiment derived from Test42, changing only CLOCK edge timeout 16 µs -> 18 µs. Attack pulse remains 18 ms. Dedicated build passed (GitHub Actions 39533151131, artifact 12316690668).

## User hardware observations
- Standard Street Fighter II car-stage save point, same kick sequence used as regression benchmark.
- **Car destroyed with one second left.**
- **Some kick inputs appeared to be missed.** This is user-observed, not established by diagnostics.
- **No unexpected directional changes observed.**
- OLED snapshot: OK 2600, ERR 58, CLK 52, REL 13.
- Follow-up user confirmation: **holding attack buttons produces no repeats**. No-repeat behavior PASS on hardware.

## Interpretation and status
Test44 passes completion narrowly and improves observed direction stability relative to Test42, but has possible kick-input misses. Initial completed/(completed+failed) = 2600/2658 (~97.8%), not directly comparable across sessions. Do not promote as final. Test42 remains the more responsive confirmed baseline; Test43 failed car-stage benchmark. Investigate attack-event lifetime and serial timeout recovery before trying arbitrary longer timeouts. No XGO-side changes.
