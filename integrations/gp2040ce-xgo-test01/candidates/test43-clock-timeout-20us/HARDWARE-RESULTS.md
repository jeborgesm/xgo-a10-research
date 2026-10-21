# Test43 initial hardware observations — 2026-10-20

Test43 is derived from Test42 and changes only `EDGE_TIMEOUT_US` from 16 to 20 µs; attack pulse remains 18 ms.

User reports: **"Honestly feels a bit slower."** Preserve this subjective gameplay observation; do not dismiss it on microsecond arithmetic alone.

OLED first readings: OK 30170, ERR 97, CLK 85, REL 13. Later: CLK 112, REL 22. LAST SLOT varies (9,1,4,8,11,2), one `FAIL 9` reading. Counters are cumulative and not all contemporaneous. Initial completed fraction is 30170/(30170+97) ~99.68%, but cannot compare directly to Test42 across uncontrolled session lengths/conditions.

No report yet on whether Test43 eliminates Test42's residual brief crouch interruption or preserves all six attack identities under holds; **do not mark Test43 as a hardware pass**. Test42 remains the best *playability-confirmed* candidate, and Test36 remains the earlier fallback.

Next: ask specifically whether Test43's crouch stability is improved and whether all six attacks remain correct/no-repeat; if no perceptible improvement, retain Test42 rather than optimizing counters.

## Follow-up hardware observation
User reports **no observed brief stand-up/crouch interruption** during Test43 car bonus stage, but Ken destroyed the car slowly and **did not finish the bonus stage**, motivating the perceived slowdown report. This is a gameplay observation, not proof of added per-input latency; no controlled attack-count/timing comparison yet. Keep Test42 as preferred playable baseline. Test43 improves perceived crouch stability but appears worse for practical attack throughput. Do not promote Test43 on counters alone.
