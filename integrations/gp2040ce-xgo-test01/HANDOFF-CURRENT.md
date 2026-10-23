# XGO A10 / GP2040-CE controller serial integration — CURRENT HANDOFF

**Updated 2026-10-22. Read the CURRENT ADDENDUM first, then the historical record.**

## 2026-10-23 — COMPILED ACTUAL C++ RESPONDER TESTS PASS; HARDWARE STILL UNTOUCHED

Verified fast CI [39949251664](https://github.com/jeborgesm/xgo-a10-research/actions/runs/39949251664) at `7c3c4e5206fd6900102b2f7b7ad6897a1a9addff`: `xgo-fast-serial/verified-models = success`. It runs existing Test49 rising-edge Python regression, 13 Python fault/source regression unit tests, and `tests/test_responder_compiled_mock.py`, which **extracts and compiles the actual Test49 and one-line offline-candidate `emit_frame()` functions** under host g++, replacing only pin/time/IRQ operations with scripted inputs. Both variants passed 4096 idealized complete masks, 22 mid-frame abort+recovery pairs, and the final-high timeout + next-frame recovery semantics. Hardware signal timing is NOT simulated; this does not prove the host would decode correctly with shifted/missed pulses. This is not an RP2040 UF2 compile.

Investigate one source-grounded early timing difference next: minimum proven Pico pre-reads button mask before LOAD, while Test49 GP2040-CE does atomic mask reads, edge queue and pulse logic **after seeing LOAD low but before waiting for DATA high and CLOCK fall**. Given the short LOAD and early slot timing, this could reduce margin, but no measured timing or direct causal link to phantom JUMP and PAUSE is established. Use the existing host waveform models and short CI, not another OLED counter firmware. Detailed evidence: `diagnostics/SERIAL-BOUNDARY-OFFLINE-AUDIT-2026-10-23.md`.

**Do not ask user for a hardware test yet. Test50 on hold; protected Test42/Test44 and Frankie unchanged.** The postamble-only candidate is NOT a verified wrong-button fix.

---
## 2026-10-23 — OFFLINE-FIRST SERIAL INVESTIGATION, NO HARDWARE REQUEST

User requested a simpler, faster approach using existing GP2040-CE, GitHub Actions, known source and existing OLED findings; **no new analyzer, Pico, wiring, serial logger or flashing per hypothesis**.

- Corrected HW witness stands: accidental Contra JUMPS while B1/P4 processed counter remained zero; later spontaneous PAUSE, then one deliberate START. User's tapped FIRE is P5/B2. Test49 legacy Python regression wrongly modeled FIRE as bit4; corrected in test-only commit `1c0f5c047597809b4b4c6031464ff78021ebefd5`. Controller mapping unchanged.
- Source discrepancy: hardware-proven minimal Pico responder ignores failure of *final* CLOCK-high wait after slot12 low, but Test49/Test50 marks it a failed transaction and invokes `require_idle_high` recovery. The corrected HW photo series reports 186 additional cumulative slot12 failures across 261 additional CLK failures, but slot12 counts merge failed terminal low and failed terminal high. Do not claim cause of phantom input from this count.
- Offline Python source-guard plus timing/slot-alignment regression `tests/test_serial_boundary_faults_offline.py`; dedicated short non-compiling CI workflow `.github/workflows/gp2040ce-xgo-fast-serial-offline.yml`. Detailed evidence with HW/SRC/MODEL/OPEN in `diagnostics/SERIAL-BOUNDARY-OFFLINE-AUDIT-2026-10-23.md`.
- Isolated candidate `candidates/offline-terminal-postamble/XGODriver.cpp` differs by **one line only** from Test49: ignore final CLOCK-high wait timeout for transaction success, matching native contract. This is **NOT built, NOT hardware-tested, NOT approved as a fix for jumps/pauses**. Literal source diff guarded by regression. Commit `ffd59f39a6df058b8e15a5b1e667091b58c8e9ab`; fast status publishing workflow updated afterward.
- Nine dynamic Python model cases passed locally; source guard compared GitHub copies and confirms precise one-line delta. A passing synthetic model is NOT physical-host proof. Await fast GitHub CI result independently; do not presume it passed.
- Test50 hardware run ON HOLD. Protected hardware baselines Test42/Test44 untouched; XGO firmware untouched.

---
## 2026-10-23 IMPORTANT — CORRECTED TEST49 USER-WITNESS ACCOUNT

The user **DID experience multiple unintended JUMPS before photo 2**, while moving RIGHT and repeatedly tapping FIRE without ever intentionally pressing JUMP. The P4 (processed B1) attack rising-edge count was **0 in all photos**, including after the phantom jumps. Continued RIGHT+FIRE, fell off a bridge, then Contra **PAUSED ON ITS OWN** without pressing START. The user pressed START intentionally ONCE to resume and later took photo 3. The assistant initially misread this as "no jumps" and corrected the primary record in `diagnostics/CONTRA-RIGHT-FIRE-OBSERVATION.md` commit `843c26324139c9386bb94f2b0289a603adacede7`. Do not repeat the false interpretation.

Test49 counters photo 1/2/3: CLK 59/172/320; slot12 failures 40/126/226; LO 48/140/259; HI 11/32/61; P0-P4 0/0/0; P5 (processed B2) 0/29/164; RIGHT+attack RF 0/29/169; RF errors E 0/6/28. The phantom JUMPS followed by zero P4 strongly suggest the JUMP bit is introduced **after processed B1 input** if B1 is the jump binding; confirm that binding, and never claim causality to slot12 alone.

Test50 commit `b7693af7f17a0f39e318cd098775bd6ae598492b` is an isolated **processed S1/SELECT and S2/START rising-edge provenance** diagnostic, to localize spontaneous pause. Serial responder and map_mask are unchanged from Test49. OLED labels S1/S2. Dedicated workflow `.github/workflows/gp2040ce-xgo-test50-pause-edge-provenance.yml`, expected status `xgo-test50/verified-uf2`; build not yet verified at handoff time. Preserve Test44/Test48/Test49.

---
## 2026-10-22 ADDENDUM — CURRENT PRIORITY (supersedes stale 2026-10-20 snapshot below)

**Do not restart.** Branch `research-gp2040ce-xgo-integration`; protected controller hardware baselines Test42 and Test44. Never modify XGO console firmware. All subsequent candidates are GP2040-CE controller only.

- Test45 failure-aware pulse delivery was compiled but felt slower and did not improve the Street Fighter II car benchmark; rejected for playability.
- Test46 clock LOW/HIGH diagnostics preserved Test44 timing and cleared Street Fighter II car with ~1 second left. Test46 incorrectly classified slot 1–11 CLOCK-high timeouts as LOW; its LO/HI breakdown is not trustworthy.
- Test47 fixed the classification (source committed and CI workflow present); no claim of separate hardware success.
- Test48 Contra diagnostic compiled, verified and *hardware tested*. When user holds RIGHT while **tapping** FIRE, Contra intermittently produces unsolicited JUMP. One or two phantom jumps occurred before third diagnostic photo; fewer than in prior tests, not solved. Photos before/after: ERR 350→628, CLK 339→597, REL 11→31, LO 299→480, HI 40→117, RF 0→179, E 0→21. `RF` is RIGHT plus **any** attack output bit, not necessarily game's FIRE. Last photo S12 FAIL 421 of CLK 597 accumulated. See `diagnostics/CONTRA-RIGHT-FIRE-OBSERVATION.md`.
- Source-level insight: slot 12 is the terminal CLOCK handshake **after all twelve button-bit slots have been transmitted**. An S12 timeout does not itself prove the XGO decoded a wrong bit; it may nonetheless disrupt rearming. Do not infer phantom-JUMP causality from aggregate CLOCK errors.
- Test49 (source commit `4bbebb277aae0af24f9b1e6c9dfdca1cb332f92c`, CI verification commit `8771532babc74e732b05aad1bf242e6e97e81a8b`) introduces six `P0–P5` *processed Gamepad attack rising-edge* counters, plus OLED layout. Test48's entire timing-critical `emit_frame()` function and `map_mask()` are byte-for-byte identical in Test49. Source audit passed. The workflow is `.github/workflows/gp2040ce-xgo-test49-attack-edge-provenance.yml`; check **`xgo-test49/verified-uf2`** commit status, then retrieve and verify artifact before any user flashing. The CI result was not available when this addendum was written. Test49 is diagnostic, not a fix.
- Test49 OLED rows: 0 header; 1 OK/ERR; 2 CLK/S12; 3 LO/HI; 4 P0/P1; 5 P2/P3; 6 P4/P5; 7 RF/E. `P0–P5` record processed button edge transitions, **not direct GPIO voltage or XGO's decoded inputs**. Avoid assigning FIRE or JUMP to a particular P bit without empirical mapping.
- User should **not watch OLED while playing**. Take initial OLED photo; play Contra normally moving RIGHT and tapping FIRE; note occurrence of unwanted JUMP; take final OLED photo. Compare `P` counter deltas to determine if the source detects an unintended second attack button. Pure FIRE edge sequences cannot synthesize JUMP in the source-level queue model; this is not proof of wire-level integrity.
- Preserve every tested candidate; no changes to Test44/Test48. When build is verified, deliver direct UF2 and ZIP if possible, not unsupported links or promises. Any hardware followup should be short and focused.

---

## Mandatory first action in next chat
Resume branch `research-gp2040ce-xgo-integration` of `jeborgesm/xgo-a10-research`. **Do not restart archaeology.** The user explicitly asks for **actual engineering work on missed attack inputs**, not a status narrative or another unsupported promise. The immediate work is offline source analysis and implementation planning of attack event delivery across failed serial transactions. Preserve tested builds. Do not request another hardware test until there is a genuine compiled candidate and a clear reason for testing it.

## Immutable scope and contract
**ALL modifications GP2040-CE controller-side ONLY**. Do not modify XGO firmware, BIOS, emulator, game, mappings, or turbo. Every physical rising edge for LP/MP/HP/LK/MK/HK should cause exactly ONE correct attack; physical hold never repeats, release re-arms. A bounded serial pulse (currently 18 ms) is needed for game polling; avoid wrong/mixed attacks and directional reversals. Do not regress controller's existing SELECT+START+R1 LED shortcut or hardware baseline. Do not revive strict CLOCK high-phase guard (Test35), independent per-button pulse (Test33), or next-slot predrive (Test30).

## Current state: playable, NOT complete
- **Test42** (16 µs CLOCK timeout, 18 ms attack pulse): best established responsiveness and protected playable rollback. All six taps work, no held repeats, defeated Zangief. Occasional brief crouch stand-up hiccup, some remaining serial errors. CI success https://github.com/jeborgesm/xgo-a10-research/actions/runs/39526930281 artifact 12313413278. Source `integrations/gp2040ce-xgo-test01/candidates/test42-clock-timeout-16us/`.
- **Test43** (20 µs, 18 ms): no crouch hiccup but slower-feeling kicks, failed car destruction before timer. Not promoted. CI https://github.com/jeborgesm/xgo-a10-research/actions/runs/39529198311 artifact 12315311345. Source `.../candidates/test43-clock-timeout-20us/`.
- **Test44** (18 µs, 18 ms): **user actually flashed and tested**. Street Fighter II car bonus save point, same fixed kick sequence used as practical throughput benchmark: **car destroyed with 1 second remaining**, **no directional reversals**, **some kicks appeared missed**, **held attack buttons DO NOT repeat** (explicit follow-up confirmation). OLED snapshot **OK 2600 ERR 58 CLK 52 REL 13**. Playable, but NOT final. Build success https://github.com/jeborgesm/xgo-a10-research/actions/runs/39533151131 artifact **12316690668** `xgo-gp2040ce-test44-OFFLINE-UNVALIDATED-DO-NOT-FLASH` (artifact label was created before hardware validation; user subsequently tested). Source `integrations/gp2040ce-xgo-test01/candidates/test44-clock-timeout-18us/`, results `HARDWARE-RESULTS.md`. DO NOT overwrite Test44.
- **Test36** (12 µs, 18 ms): older protected playable fallback; occasional wrong attack/direction; CI https://github.com/jeborgesm/xgo-a10-research/actions/runs/39075369513 artifact 12116143787.
- **Test41** diagnostics: LOW/HI indicate CLOCK phase already present at wait entry, NOT proof of missing edges. Failures distributed across slots even with no buttons; don't attribute every ERR to kick losses. 

## CONFIRMED source-level vulnerability requiring next work
Read `integrations/gp2040ce-xgo-test01/ATTACK-PULSE-FAILURE-ANALYSIS.md` and **Test44 XGODriver.cpp**. Current implementation Core0 latches physical rising edges:
```cpp
const uint16_t snapshot = map_mask(gamepad);
const uint16_t attacks = snapshot & ATTACK_BITS;
const uint16_t rising = attacks & ~previous_physical_attacks;
previous_physical_attacks = attacks;
if (rising) pending_press_edges.fetch_or(rising, std::memory_order_release);
published_mask.store(snapshot, std::memory_order_release);
```
Core1 in `emit_frame()` after LOAD low, with IRQ masked, **BEFORE knowing whether serial frame succeeds**:
```cpp
const uint32_t now = time_us_32();
if (attack_pulse_mask && (uint32_t)(now - attack_pulse_start_us) >= ATTACK_PULSE_US)
 attack_pulse_mask = 0;
const uint16_t pending = pending_press_edges.exchange(0, std::memory_order_acq_rel);
if (pending && !attack_pulse_mask) {
 attack_pulse_mask = pending;
 attack_pulse_start_us = now;
} else if (pending) pending_press_edges.fetch_or(pending, std::memory_order_release);
const uint16_t mask = (physical & ~ATTACK_BITS) | attack_pulse_mask;
```
`ATTACK_PULSE_US = 18000`; `EDGE_TIMEOUT_US = 18` in Test44. Then slots 0–11 are transmitted, and `complete` only determined at end. **A failed frame can consume a pending edge and age out its 18ms pulse without any successful delivery**. Code comment 'A failed serial transaction cannot acknowledge the physical press' is **not implemented**. A completed serial frame also does not prove the game's poll sampled the pulse. This is a proven CODE defect/vulnerability, NOT yet a proven sole cause of observed missed kicks.

## Immediate engineering instructions
1. Inspect Test44 complete source and dedicated workflow, plus prior candidate behavior; preserve source byte-for-byte in protected folders.
2. Design/implement a **new isolated candidate** (next Test45 if appropriate) fixing the attack event commit/retry lifetime across failed serial frames while preserving strict one-shot physical hold and bounded game-visible pulse. Crucial edge cases: failure on first frame, several failures, long physical hold, release/re-press, second attack during first pulse, simultaneous presses, transient serial idle, timer rollover. A simple unconditional retry on every failed frame could cause long-held repeats; avoid. Avoid claiming that one successful transaction guarantees game observation. Consider bounded grace/retry and counters for attempts/success/expiry; distinguish host scans vs game polls. Avoid adding heavy work in timing-critical IRQ-disabled section.
3. **Do actual repository edits and compile using dedicated GitHub Actions**, fix build failures, check final artifact before asking user to flash. Do not promise asynchronous progress or say 'working' without actual tool activity. If design not sufficiently safe, commit rigorous design analysis and identify unresolved conditions honestly instead of creating unsafe firmware.
4. For user hardware tests use **the same saved Street Fighter II car stage and same kick sequence**: completion/time remaining, missed kicks, crouch direction, six correct attacks, held no-repeat, diagnostics. Test44 car success +1 second, Test43 fail, Test42 responsive. User values playability over lowering counters.
5. Never alter XGO side. Keep Test42/Test44 intact and rollbackable.

## Tool operations
GitHub connector through `functions.exec`: `tools.mcp__GitHub__fetch_file({repository_full_name:'jeborgesm/xgo-a10-research',ref:'research-gp2040ce-xgo-integration',path:'...'})`; `create_file`, `update_file`. Dedicated workflows at `.github/workflows/gp2040ce-xgo-test44-clock-timeout-18us.yml`. Use GitHub Actions API to check runs/artifacts; generic `build-xgo-p0.yml` may fail independently and is not authoritative for this controller candidate.

## Previous experiments / rejected regressions
Test28 stable original HK slot0 open-drain asserted after 3µs LOAD-low; others repeat/mix. Test29–31 timing variations rejected (Test31 HK repeats). Test32 first six-attack physical edge 24ms, occasional HP→MK and direction artifacts. Test33 independent pulses severe mixed inputs. Test34 extra release scan no fix. Test35 strict CLOCK high guard caused choppy movement/missed attacks. Test36 Test32 pulse 24→18ms improved. Test37 counters unreadable; Test38 wrong OLED screen; Test39 active screen diagnostics overlap, stable DIR:A despite Ken reversal; Test40 clean OLED eight-row diagnostics; Test41 phase counters, errors distributed; Test42 16µs significant improvement; Test43 20µs directional stability but poor throughput; Test44 18µs playable +1sec car, possible missed kicks.

## User expectations and recent interaction
User explicitly asked 'now seriously are you doing any actual work to check the missing inputs?' after joking about management deadlines. Do not respond with banter instead of code. User is frustrated by conversation limits and lost momentum. This handoff is intended to allow next chat to begin immediately with actual implementation. Be candid: at handoff time **only source-level vulnerability analysis has been committed; no Test45 or corrective build exists**.
