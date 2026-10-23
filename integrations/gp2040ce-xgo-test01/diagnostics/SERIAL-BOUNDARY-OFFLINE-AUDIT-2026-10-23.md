# XGO GP2040-CE — focused serial boundary offline audit (2026-10-23)

## Scope and user constraint

No equipment purchase, no Frankie rewiring, no XGO firmware modification, no OLED replacement, and **no request for a hardware test**. Preserve Test42/Test44 hardware baselines and Test48/49/50 diagnostic source. Goal: avoid one firmware build/flash per hypothesis. Only Python offline models/source guard and a clearly unvalidated *isolated candidate* are introduced.

## Hardware witness (HW)

Corrected Test49 run: intentional **RIGHT + tapped FIRE only**; multiple unintended JUMPS before OLED photo 2, with processed Gamepad **P4/B1 = 0** in photos 1, 2, and 3. Later the game spontaneously PAUSED before photo 3; user deliberately pressed START once to resume. Processed P5/B2 FIRE edges = 0 / 29 / 164. CLOCK errors = 59 / 172 / 320; slot-12 CLK failures = 40 / 126 / 226. Do not misstate "no phantom jumps." See `CONTRA-RIGHT-FIRE-OBSERVATION.md`.

## Source comparison (SRC/HW provenance distinguished)

The hardware-proven minimal RP2040 (`tools/rp2040-xgo-live-controller/main.c`, same frame end in `tools/rp2040-xgo-native-contra/main.c`) sends the 12 bits, waits for terminal CLOCK low, releases DATA, and **ignores the result** of the final `wait_clock(true,EDGE_TIMEOUT_US)` (12 us budget). It returns success when the final CLOCK-low edge was observed.

Test49 GP2040-CE (`candidates/test49-attack-edge-provenance/XGODriver.cpp`) sends the same 12 numbered slots but, after terminal low, **marks the entire transaction failed** if `wait_clock(true, EDGE_TIMEOUT_US)` does not succeed within 18 us; it then sets `require_idle_high` for its next transaction. Test50 carries the same behavior.

The discrepancy is concrete (SRC), and the hardware logs show a substantial number of terminal-slot failures (HW). The slot-12 counter does **not** separate absence of terminal low from absence of terminal high, so we **cannot yet say** how many observed failures the discrepancy explains. Nor can this terminal-postamble difference, by itself, demonstrate a wrong JUMP or START bit: all 12 bits were already sent when terminal high is awaited.

A separate test-script issue was corrected: Test49's `test49_attack_edge_provenance.py` had labeled bit 4 as FIRE and bit 5 as OTHER, contrary to the controlled run where tapping FIRE generated P5/B2 presses and no P4/B1 presses. The test now models FIRE bit 5, OTHER bit 4. This is a test-only change, not a change in the controller's button mapping.

## Offline regression design (MODEL, not HW)

`tests/test_serial_boundary_faults_offline.py` models the specific scenarios and is guarded against real source text:

- Complete tail: minimal and Test49 both succeed.
- Final low present but final high delayed/absent: minimal accepts; Test49 marks failure/rearm. The modeled misclassification **does not alone invent a JUMP bit**.
- Final low missing: both fail.
- A valid RIGHT + tapped B2/FIRE sequence with no B1 or S2 cannot create JUMP or START through the modeled Core0-to-Core1 pulse queue and correctly aligned serial slot decoder.
- A *hypothetical* one-slot advancement of FIRE bit 5 would appear in host slot 4 (possible wrong JUMP); a hypothetical two-slot delay would appear in slot 7 (possible wrong START). **These are examples of what a loss of alignment could do, not evidence that the XGO actually drifted by these amounts.** The electrical root cause is still OPEN.
- Source checks ensure the native, Test49, Test50 behaviors and the intentional one-line candidate change match the actual repository sources, guarding against misleading model-only passes.

## Isolated candidate (SRC only; no compilation or hardware pass)

`candidates/offline-terminal-postamble/XGODriver.cpp` is an exact copy of Test49 except for **one line**: allow the terminal CLOCK-high wait to time out without marking the already transmitted frame failed, matching the native controller's end-of-frame success policy. The timeout call and time budget remain; no timing, mapping, pulse queue, IRQ windows, or GPIO hardware behavior elsewhere is changed.

**Warning:** this may suppress false failures / unnecessary recovery, but cannot be claimed to fix phantom JUMP or spontaneous PAUSE. The candidate is deliberately **not** flashed or promoted to baseline. The source guard enforces a literal one-line delta.

## Faster process going forward

`.github/workflows/gp2040ce-xgo-fast-serial-offline.yml` runs the two focused Python regressions on GitHub's hosted runner. It does **not** install a toolchain, compile firmware, create an UF2 or perform a hardware action. Future changes should first improve these repeatable cases rather than request further Contra runs. Only propose a physical test when one scoped, source-supported correction has passed offline checks and build review.

## What remains OPEN

1. Which of the observed slot-12 errors are missing terminal low versus missing terminal high? Current counters cannot distinguish them.
2. Whether early-slot loss of synchronization actually occurred in the spontaneous JUMP/PAUSE episodes. Synthetic shift examples are not physical proof.
3. Exact in-game JUMP binding vs logical B1 and whether external interference or controller electrical behavior is involved.
4. Whether the one-line candidate impacts reliable host-to-controller frame acquisition under real-world timing. It is uncompiled and untested on hardware.

## Follow-up: compile actual C++ responder with scripted host signals (2026-10-23)

**CI verified PASS:** [GitHub Actions run 39949251664](https://github.com/jeborgesm/xgo-a10-research/actions/runs/39949251664), commit `7c3c4e5206fd6900102b2f7b7ad6897a1a9addff`, status `xgo-fast-serial/verified-models = success`.

The regression `tests/test_responder_compiled_mock.py` extracts the *actual* `bool emit_frame()` function from the repository for **both Test49 and the postamble-only offline candidate**, compiling it as ordinary host-side C++ with deterministic substitute `wait_clock`, `wait_data`, `data_sink`, `data_release`, atomics, and timer/IRQ stubs. It does NOT replace the function with a Python rewrite.

Each of the two compiled source variants completed:

- **4,096 / 4,096 idealized synchronized 12-bit masks** with exact expected slot values, including START/SELECT/JUMP and all combinations.
- **22 injected mid-frame aborts and corresponding next-frame recovery checks** (a failed CLOCK-low and CLOCK-high at each of slots 1–11). Both variants report failed frame and require DATA-high rearm, then pass subsequent frame.
- **One final CLOCK-high failure after sending all 12 bits, followed by a good next frame.** Test49 reports failed frame and requires an extra DATA-high rearm. The one-line candidate reports successful frame without extra rearm, precisely matching its intended native-style postamble classification.
- With right + B2/FIRE as the only active bits, the idealized serial output does not spontaneously set B1/JUMP or S2/START.

The source test runs with only a host `g++` compiler in the short existing CI job, without downloading/compiling the full GP2040-CE firmware. The first two CI attempts failed on **mock-test harness compile issues** (prototype ordering then assertion parentheses under `-Werror`), fixed before the verified green run; these were test-harness failures, not XGO firmware defects.

**Limit of proof:** The mock intentionally advances a scripted host transition sequence when the C++ responder asks for each CLOCK/DATA level. It does not simulate a free-running real-clock waveform, electrical glitches, delayed interrupt entry, physical LOAD length, or the XGO host's actual button sampling. Consequently, the result proves there is no ordinary source-level wrong-bit mapping or wrong-bit insertion **under correctly sequenced inputs**, not that the real XGO serial link is clean. A successful mock C++ compile is NOT a successful RP2040 firmware compile. The one-line candidate remains offline and unvalidated on hardware.

### Next offline priority (no new firmware, no flash)

Focus on **acquisition timing at the start of a frame**, not more aggregate counters: in Test49 the LOAD-low detection is followed by `save_and_disable_interrupts()`, an atomic published-mask read, 18ms pulse expiry/queue processing, an atomic pending-edge exchange, and mask composition *before* attempting `wait_data(true)` and the first CLOCK-low wait. The minimal proven Pico samples its GPIO mask **before waiting for LOAD**, then performs the load-release/clock handshake without that queue work between LOAD-low acquisition and first clock. This is a genuine source difference that could reduce early-slot timing margin; no cycle-accurate time budget or missed-CLOCK event has yet been established. Prefer offline early-slot timing analysis and analysis of existing Test14 synthetic waveform scripts over changing the responder speculatively.

**Stop condition:** Do not promote the terminal-postamble-only candidate as a phantom JUMP/PAUSE fix. If an offline candidate is eventually justified, require source-level invariant checks, actual RP2040 compilation, and only then a single physical test of a small set of grounded changes rather than isolated counter firmware updates.
