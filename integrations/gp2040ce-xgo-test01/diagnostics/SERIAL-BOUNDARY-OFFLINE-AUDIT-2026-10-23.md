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
- A *hypothetical* one-slot advancement of FIRE bit 5 would appear in host slot 4 (B1, NOT the hardware-proven Contra JUMP); a hypothetical two-slot delay would appear in slot 7 (possible wrong START). **These are examples of what a loss of alignment could do, not evidence that the XGO actually drifted by these amounts.** The electrical root cause is still OPEN.
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

## CRITICAL CORRECTION — Contra JUMP is hardware-proven R / serial position 0

Earlier sections inherited a faulty provisional interpretation from Test49: they associated phantom JUMP with `P4 / B1`, then used a one-slot synthetic misalignment (B2 slot5 -> B1 slot4) as an example of a potential *jump*. That association was **wrong for the confirmed Contra mapper**.

The archaeology already contains a physical hardware proof:

- `experiments/rp2040-responder-p1-fixed-r.md`: an intentionally forced R/serial-position-0 input made Contra Player 2 jump repeatedly, with no other input asserted.
- `tools/rp2040-xgo-p2-contra/README.md`: confirms raw R maps to FC A/JUMP in the tested Contra .kmp and the full scripted controller's jump action passed on hardware.
- `experiments/rp2040-usbphy-p3-passive.md` independently notes unsolicited Contra jumping when merely attaching a passive native PHY, and explicitly connects that to R/slot0 sensitivity.
- In the latest user-controlled Test49 run, **P0=0 and P4=0 throughout** while unsolicited JUMPs occurred. This means processed `pressedR1()` (bit0) did NOT rise, not that the host couldn't perceive a pressed R/slot0.

Thus the strongest source/hardware-consistent explanation for **the JUMPS** is erroneous **host interpretation of position 0**, potentially associated with DATA returning high from the XGO's own load-low pulse too slowly or a slot0 software/line setup problem. It remains a hypothesis, not a measured live fault.

### Timing evidence matters more than the Test04 source comment

P0 passive capture established **host DATA/LOAD low approximately 6.8–7.5 us** and the first CLOCK low **approximately 0.9–1.3 us after DATA release**. Source: `experiments/rp2040-responder-p1-fixed-r.md` and `experiments/rp2040-usbphy-p3-passive.md`. The earlier GP source comment asserting a 12us first-bit interval must not override this later timing evidence from hardware. XGO firmware samples serial position 0 immediately after releasing DATA as its load/reset line, *before* the first CLOCK pulse.

The source's open-drain `data_release()` only relinquishes controller drive; it cannot itself guarantee that the host's GPIO input crossed the valid-HIGH threshold by the initial sample. Physical release threshold timing with Igor/Frankie during Test49 was NOT measured.

### New short offline tests and true limitations

- Updated `tests/test_serial_boundary_faults_offline.py` uses `JUMP_R0=1<<0`, explicitly distinguishes B1/slot4, and refuses to label synthetic B2->B1 one-slot movement as an actual Contra JUMP. It retains the separate speculative B2->START two-slot shift demonstration for the unsolicited pause.
- Updated `tests/test_responder_compiled_mock.py` treats unpressed-R/slot0 ideal sampling at the host DATA-release event rather than at the first CLOCK fall; the separately pre-driven R/slot0 path is folded into that earlier event because there is no `wait_data(true)` call in that code path. It also injects a *hypothetical* host-sampled-low slot0 despite the responder logically sending R=0 and later seeing DATA high. That demonstrates a clean C++ `emit_frame()` success can coexist with host-visible JUMP under this modeled external DATA-transition error, not that the error actually happened.
- New `tests/test_slot0_release_settle_offline.py` uses the proven 0.9–1.3us release-to-first-CLOCK window and explicit *synthetic* recovery-delay/sample-offset pairs. A transient LOW at the earlier slot0 sample, followed by valid HIGH before first CLOCK, would give jump-only input while DATA appears high during the clock burst. This reconciles the earlier physical GREEN probe's jump-only symptom with the clean later CLOCK DATA idle observation, but does not prove Igor suffers the same analog effect.
- The spontaneous **PAUSE** (START/slot7) is a distinct observed failure; the slot0 mechanism cannot explain it. Do not overfit both symptoms to a single analog hypothesis without host-side evidence.

These source and model corrections do not change ANY RP2040 firmware and do not require physical testing. The one-line terminal CLOCK-high candidate remains a separate unvalidated recovery experiment, NOT a demonstrated phantom-JUMP fix. If a proposed firmware tweak cannot influence the XGO's immediate slot0 DATA sample, it is not a grounded fix for this specific mechanism.


## 2026-10-23 follow-up: free-running CLOCK actually executing production C++ body

**Verification:** [GitHub Actions run 39963557253](https://github.com/jeborgesm/xgo-a10-research/actions/runs/39963557253) for commit `f387e00edbd0e51ef2dd1709ad2751dfc90d5223` reports `xgo-fast-serial/verified-models: SUCCESS`.

New regression `tests/test_responder_free_running_clock.py` extracts the production `emit_frame()` C++ from Test49 and the isolated one-line postamble candidate and compiles each with host `g++`. Unlike the prior scripted-event mock, XGO's 12 CLOCK pulses and host sampling advance on a **free-running virtual timeline** regardless of the responder's calls to `wait_clock()`. Clock pulses are nominally 4.0us period / 2.0us half-phase, XGO LOAD is 7.2us low, and its release precedes first CLOCK-low by 1.2us: these are representative values inside the earlier **HW** P0 ranges. The absolute host sample offset (+0.1us), C++ polling-time overhead, DATA recovery delay and injected firmware stalls are **MODELED/INF** and **are NOT measured in the Test49 controller setup**.

### Independent source-level failure reproductions (MODEL + SRC)

1. **No injected fault:** for 18us timeout, both actual compiled source functions serialize all **4,096 / 4,096 masks** correctly under the free-running virtual host. The separate earlier ideal scripted-edge mock also passes.
2. **R/slot0 false JUMP:** a hypothetical 0.35us DATA valid-high recovery delay after host LOAD release creates an extra LOW at the modeled immediate slot0 sample, while the actual C++ `emit_frame()` still returns success and `published_mask` contains only RIGHT+B2 FIRE. This demonstrates one way **P0=0 upstream** and an unintended host-decoded **R/Contra JUMP** can coexist without bad button mapping. The 0.35us analog recovery delay and sample offset are not physical measurements; no claim that Igor actually has this delay.
3. **START/slot7 contamination from FIRE/slot5:** inject a hypothetical **9.0us stall after the responder finished the FIRE/slot5 CLOCK-high wait** while DATA remains sunk for FIRE. The *independent* host clock continues, samples FIRE LOW in later SELECT and START slots, and the decoded word in this scenario is `0x0e0` (B2/FIRE bit5 + SELECT bit6 + START bit7); RIGHT bit11 is lost. The actual responder eventually reports a CLOCK failure. The false START/PAUSE input was already accepted by the host **before** the failure return. This is a tangible source-level consequence of `wait_clock(level)` synchronization without CLOCK pulse sequence identity. It is **not** evidence of a real 9us stall on Core1: hardware interrupts are disabled during the transfer.
4. **Systematic synthetic sweep:** in this virtual setup, the first after-FIRE timing gap yielding false START is **7.75us**; a prep delay immediately after LOAD-low acquisition can also yield START at **13.75us**. These are thresholds **of this model**, not tolerances or measured GP2040-CE execution times.
5. **Timeout-only tuning is not a clean fix.** With EDGE_TIMEOUT_US changed *only inside the host-compiled mock* (not in firmware), timeout budgets 18us and 8us both give 4,096/4,096 clean masks AND allow the modeled 7.75us FIRE-to-START contamination. More aggressive 6us and 4us budgets cause 2,048/4,096 and 4,096/4,096 **ordinary-frame failures** respectively in this particular virtual CPU/host model. This demonstrates why changing just the timeout is an unjustified fix; **do not extrapolate** those failure counts to actual XGO hardware, because virtual polling overhead is a chosen parameter.
6. **One-line postamble candidate changes none of these outcomes.** The Test49 and native-style-postamble candidate exhibit identical host-decoded synthetic false R/START behaviors under all compared settings. Reclassifying the final CLOCK-high timeout cannot reverse any button already sampled by the host.

### Practical engineering implications

- The existing Test49 diagnostics and old game tests have done their job: they establish actual unexpected game actions, absence of corresponding processed R/P0 (and B1/P4) rising edges, and many serial failures. The code now has a source-grounded mechanism for a host-side false R/slot0 input and a *different* mechanism for START/slot7 contamination, but no definitive physical cause.
- **Do NOT flash a postamble-only fix or randomly decrease EDGE_TIMEOUT_US as a phantom-input cure.** The source/mock evidence rejects both as adequate standalone remedies; the protected Test44 hardware baseline stays untouched.
- GP2040-CE's START/S2 processed input was not counted in Test49, so the spontaneous pause might still reflect an upstream processed START or physical control event; Test50 was designed to localize this, but another OLED hardware test remains deferred.
- The remaining discriminating offline work is to assess whether any *plausible* GP2040-CE Core1 execution path could incur sufficient delay while DATA is sunk, and whether the native USB PHY's physical DATA release/receiver coupling could plausibly affect slot0. That requires cycle/source-level evidence, not treating synthetic stall durations as observed.
- Continue relying on the short CI suite; it does not require a spare Pico, logic analyzer, Frankie wiring changes, modified console BIOS, or another user gameplay run.

**Verified class:** CI/SRC for compiling/running actual responder functions, HW for existing P0 and Test49 separately, MODEL for host clock and injected failures, OPEN for actual causal link.
