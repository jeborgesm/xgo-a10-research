# XGO ARCHEOLOGY — CURRENT CHECKPOINT (2026-10-24)

**Authoritative active thread:** GP2040-CE transparent controller signal reliability; do not restart the historical Test14/Test15 project detailed below. Read [the current October 24 master handoff](integrations/gp2040ce-xgo-test01/HANDOFF-2026-10-24-TRANSPARENT-BASELINE-AND-INPUT-FAULTS.md), [controller-transparency contract](integrations/gp2040ce-xgo-test01/CONTROLLER-TRANSPARENCY-CONTRACT.md) and the [branch-local handoff](integrations/gp2040ce-xgo-test01/HANDOFF-CURRENT.md) **before** the old text below. Branch `research-gp2040ce-xgo-integration`.

**HW-positive working baseline:** transparent controller + restored OLED UF2 SHA-256 `94ea7228c774a67e8252e7e09d94938530e5d74572d985332e6840ae09fe8b84`. Held/tapped inputs work; user played SFII (defeated Dhalsim) and Contra (X/Y turbo works through XGO). **OPEN:** intermittent spontaneous Contra JUMP; SFII sometimes ignores LP or gives three rapid LP punches. Exact cause unproven.

**Offline-only paged OLED candidate:** UF2 `5dcc28132ca54293a3d27dc2a452269bc47a1e7f141bd49c2c7e296918071b5b`, compiled/linked/verified via CI 40107598214, **NOT flashed or hardware proven**; fixes a source-observed Core0 I2C blocking risk but does not prove a ghost-JUMP cure. Preserve both firmware hashes and the old Test44 recovery separately.

**Latest BIN development:** [original XGO P1-dependent P2 slot0 sampling](integrations/gp2040ce-xgo-test01/findings/2026-10-24-xgo-p1-dependent-p2-slot0-sampling.md), with [hash-pinned verifier](integrations/gp2040ce-xgo-test01/tests/verify_original_xgo_slot0_p1_path.py). If P1 slot0 is LOW the XGO host executes four more MIPS instructions before reading P2 slot0; all sampled before first CLOCK-low. This is an instruction-path discriminator, **not** measured voltage/cycle timing or causal proof of Contra jumps. The protected XGO `bios/bisrv.asd`, controller driver, normal OLED, Frankie wiring and input semantics must not change without separate evidence.

**The remaining content below is HISTORICAL and contains obsolete "next task" and Test14/Test15 instructions. It MUST NOT override the active 2026-10-24 master handoff.**

---

## CRITICAL HW RESULT — Test15 REJECTED (2026-10-12)

User tested Test15: HK short taps FAIL; HK/HP hold repetitions FAIL; unintended LP from HK FAIL; unintended LK from HP FAIL; rapid tap/hold mixed attacks FAIL. OLED input display PASS; Web Config PASS. **No actual improvement over Test14.** Source: `findings/gp2040ce-test15-hardware-failure-2026-10-12.md` (commit `6ae5564`). The Test15 candidate's fresh snapshot and reduced IRQ-off diagnostics **are not a demonstrated fix**. Do not suggest Test15 again as resolved. Golden Test14 protected. Pivot to independent end-to-end processed mask/PHY/host decode and game binding evidence before Test16. Do not ask for repeat of these same tests.

---

## Test15 offline candidate compile result — 2026-10-12

**CI PASS:** [run 38274789992](https://github.com/jeborgesm/xgo-a10-research/actions/runs/38274789992); artifact `11757969447` named `xgo-gp2040ce-test15-OFFLINE-UNVALIDATED-DO-NOT-FLASH`. **Golden Test14 unchanged.** Candidate source `integrations/gp2040ce-xgo-test01/candidates/test15-offline/XGODriver.cpp`. Validation record `findings/gp2040ce-test15-offline-candidate-build-validation-2026-10-12.md`. Local deterministic 100k schedule stress passed; no hardware validation. Artifact archive digest `sha256:97223dd2da56142e40dc673c073b00d5ea1d1dc28e8436815397b7adaa62c693` (archive, not UF2). Core0 producer byte-for-byte preserved. Next meaningful dependency is explicit user approval for controlled hardware test, or further independent timing analysis; do not imply all cross-button issues fixed.

---

## 2026-10-12 OFFLINE FIX CANDIDATE CHECKPOINT (latest)

**User direction:** execute work, avoid frequent status-only stops. A narrowly scoped **Test15 offline candidate** now exists, but golden Test14 overlay and artifact remain unchanged. **Do not ask for a hardware test yet.**

- Candidate file: `integrations/gp2040ce-xgo-test01/candidates/test15-offline/XGODriver.cpp` (commit `e52160a`).
- Structural gates: `integrations/gp2040ce-xgo-test01/tests/test15_candidate_static_gates.py` (commit `9750b04`).
- Isolated CI workflow: `.github/workflows/gp2040ce-xgo-test15-offline.yml` (commit `66d9bab`), [Actions run 38274789992](https://github.com/jeborgesm/xgo-a10-research/actions/runs/38274789992), queued when created. **Do not claim compile success until run completes.**
- Mechanism corrected: Core1 now reads the atomic published mask **after** observing LOAD low (rather than before a possible 20ms wait); Core1 masks interrupts immediately after LOAD detection, then samples the mask and waits for LOAD release; atomics for diagnostic counters moved **outside** IRQ-disabled slot transfer. Clock polarity, 12-slot order, final clock handling, and failure-only rearm remain as Test14.
- This is a **source-grounded fix candidate for stale snapshots and IRQ-critical diagnostics**, not proof of the reported Street Fighter HK/HP issues. The original Caveman upstream source and physical host waveform remain open. Do not promote MODEL/INF to HW.
- Hardware-proven loose-wire reference: `tools/rp2040-xgo-native-contra/main.c`. It shares the ignored final CLOCK high and level-based acquisition with Test14; neither is an identified GP2040-specific regression.
- Additional classification tests `tests/test14_multiframe_fault_classifier.py` (commit `7425407`) and findings `findings/gp2040ce-test14-caveman-source-comparison-fault-classification-2026-10-12.md` (commit `2351d90`).

### Next: validate CI outcome, fix any compiler/test failures, then review cycle timing and candidate residual risks. Do not flash automatically. Golden Test14 must remain byte-identical.

---

# XGO ARCHEOLOGY — HANDOFF CURRENT
## GP2040-CE XGO serial responder / Street Fighter six-button fault
**Date:** 2026-10-12  
**Repository:** `jeborgesm/xgo-a10-research`  
**Branch:** `research-gp2040ce-xgo-integration`  
**Protected golden:** **Test14**. DO NOT modify, replace, or flash over it.  
**Next objective:** finish offline serial-transaction validation and identify safe Test15 candidate only when justified. **Do not ask for more hardware tests yet.**

## Resume instructions
Read this handoff **completely** and the cumulative audit `findings/gp2040ce-test14-comprehensive-offline-audit-2026-10-10.md` before work. Preserve HW/SRC/UP/BIN/MODEL/INF/OPEN evidence distinctions. This is a continuation, **not a new investigation**. Do not claim an offline model proves physical console timing or gameplay cause. Keep all findings in GitHub. No speculative timeout changes.

## Hardware setup
- RP2040 GP2040-CE Pico = **Igor**; custom XGO cable = **Frankie**.
- Golden Test14 boots, works in XGO mode, OLED input history works, Web Config available at `192.168.7.1`. Earlier ordinary gameplay worked, but Street Fighter six-button testing exposed defects.
- Test14 source commit `fb911825123f07ea8fe12e4bdf881583a76de146`; Actions run `38098786893`, artifact `11687143460`.
- Golden ZIP SHA256 `05122fa15035392e41ab0c0eb361d1d91acebe871c8e4b55399e6b5b2f5476ec`, UF2 SHA256 `ac2d948c4d3e246787988bc8a3fc91bfc3bd773a333ddafc2778c45bc823c97e`. Golden in `jeborgesm/xgo-a10-artifacts` at `golden/rp2040-gp2040ce/test14/xgo-gp2040ce-test14-UNTESTED.zip` (historical filename; subsequently tested).
- Pinned upstream `OpenStickCommunity/GP2040-CE` commit `3d1f32f7d02d418826b725b60208278d3be878c3`.
- Physical Frankie V2 Jr pad contract: 1 BLACK, 2 WHITE, 3 GREEN, 4 WHITE (2 and 4 shared), 5 RED; do not treat as USB standard pin order. Details `findings/rp2040-xgo-frankie-cable-contract.md`.
- Igor saved backup: `gp2040ce_backup_20261011165601680.gp2040` (private; do not publish raw backup), `gamepad.inputMode=18` XGO, debounce 5ms, Turbo addon enabled (GP14) but user can distinguish Turbo on OLED.
- Last Web Config screenshot GPIO mapping: GP6=A/B1, GP7=B/B2, GP8=RB/R1, GP9=RT/R2, GP10=X/B3, GP11=Y/B4, GP12=LB/L1, GP13=LT/L2; GP14 Turbo; GP16 Back/S1, GP17 Start/S2. **The exact Street Fighter in-game attack-to-logical-button bindings are not yet established; never assume HK/LP/HP/LK slot assignments.**

## User hardware findings — authoritative
1. HP works on both tap and hold; HK short taps often fail, HK hold works.
2. **Holding any Street Fighter attack should result in only one attack until release/repress** (user specifically corrected previous assistant's incorrect assertion that periodic repeats were normal). HP and HK sometimes repeat ~once/second during a sustained hold.
3. HK can introduce an unintended **LP jab**, **not MP** (previous MP report superseded).
4. Sustained HP can introduce unintended **LK**.
5. Rapid HP tapping followed by a hold can produce punches and kicks. Tapping several buttons then holding HK can produce mixed attacks. This appears history-dependent.
6. OLED consistently shows physical/logical presses correctly. When Turbo is active, OLED marks and displays repeated taps; **this is not seen in the current failure**. Turbo is a substantially weakened hypothesis, though OLED is not proven byte-for-byte equivalent to published XGO mask.
7. User explicitly expects comprehensive audit to catch such behavioral defects, not merely boot/config/structural issues. Do not burden user with repetitive tests until offline work is exhausted.

## Actual Test14 driver contract (SRC)
File `integrations/gp2040ce-xgo-test01/src/drivers/xgo/XGODriver.cpp`:
- Core0 calls `map_mask(gamepad)`, atomically publishes `published_mask` with release ordering.
- Slot order: 0=R1, 1=B4, 2=B3, 3=L1, 4=B1, 5=B2, 6=S1, 7=S2, 8=UP, 9=DOWN, 10=LEFT, 11=RIGHT.
- **L2/R2 absent from serial mask**, even though upstream XInput reports these as triggers. Thus six attack buttons must use B1/B2/B3/B4/L1/R1 if no new protocol extension.
- Core1 reads atomic mask (acquire) **before** calling `emit_frame`; waits up to `LOAD_TIMEOUT_US=20000` for DATA low. Snapshot can become stale during wait; short pulse can be missed, but stale snapshot alone cannot synthesize LP/LK.
- LOAD release wait and each CLOCK edge use `EDGE_TIMEOUT_US=12`. Core1 IRQs masked for 12-slot clock train. Slot0 driven after LOAD high; slots1..11 updated on each falling CLOCK, waits for high. Waits for final slot12 CLOCK falling, releases DATA, then calls `(void)wait_clock(true, EDGE_TIMEOUT_US)` **ignoring its result**.
- `require_idle_high` after failed active frame requires DATA high before rearming. **On success, no explicit DATA-high phase required before next `wait_data(false)`**, allowing level acceptance of already-low DATA under some waveforms.
- `raw_init()` takes ownership of USB PHY; mode change should reboot.
- Diagnostics exist: frame success/failure, LOAD/release/clock timeouts, failure slot, mask changes, etc.; not established as externally visible.
- Do not claim the ignored final CLOCK rise causes wrong attack without host trace.

## Upstream comparison (UP, already performed)
Pinned `src/gp2040.cpp:288-310`: `gamepad->process()` -> `addons.ProcessAddons()` -> `gamepad->hotkey()` -> `checkProcessedState()` -> copy processed state -> `inputDriver->process(gamepad)` -> TinyUSB task. `checkProcessedState` emits press/release events from old/current state differences; standard XInput `src/drivers/xinput/XInputDriver.cpp:253+` builds a complete report directly from held `pressed*` values, handles L2/R2 triggers. XGO likewise uses held states, but transports them through asynchronous custom serial PHY. Standard USB timing is not directly portable.

## Offline models already in GitHub
- `integrations/gp2040ce-xgo-test01/tests/test14_snapshot_contract_model.py` (commit `197a7cacde8a497efe683735e227950decc938df`): 4096 12-bit combinations and illustrative stale snapshot; **not electrical validation**.
- `integrations/gp2040ce-xgo-test01/tests/test14_phy_transaction_model.py` (commit `f91573b2a5e9ff1841e810325880ac41a4edfdbe`): 4096 normal masks, 22 intermediate clock failures, 5 missing final-rise scenarios; proves **source-model** success classification can ignore final high.
- `integrations/gp2040ce-xgo-test01/tests/test14_consecutive_load_model.py` (commit `d95d0e81393e62bbd8891d5c25f5e30eff245eed`): 8 logical combinations of success/failure, DATA high observed, DATA low now; demonstrates success path accepts already-low DATA without fresh edge.
- `integrations/gp2040ce-xgo-test01/tests/test14_temporal_rearm_model.py` (present in branch and documented in audit): 4 synthetic discrete-time traces. **Crucial counterexample:** blindly requiring fresh high-then-low LOAD can itself miss legitimate transactions if host begins next LOAD before responder re-arms, or a narrow idle-high gap is missed. **DO NOT implement unconditional edge-only rearm as proven fix.**
- The models are simplified, source-guided behavioral assertions, not waveform captures, MCU cycle-accurate emulation, or actual console decoding. Prior chat stated test outcomes; rerun scripts in new session for independent validation. Avoid overclaiming.
- Cumulative audit `findings/gp2040ce-test14-comprehensive-offline-audit-2026-10-10.md` contains findings A01–A32 plus dated SF follow-ups, including prior corrections.

## Known broader audit risks
- A16 P0: Web Config boot input mode selector missing XGO in hardcoded UI/Yup; saved return boot chord not established.
- A01 flash lockout victim registration preserved, but flash-write pause and resume can disrupt Core1 transactions.
- A02 12us edge deadlines and atomic counters inside IRQ-disabled region lack disassembly/cycle timing proof.
- A03 stale snapshot before LOAD.
- A04/A21 malformed frame/rearm and ignored final clock rise.
- A26 Turbo eligible to run but HW OLED observation argues against Turbo pulses here.
- A30 configured D-pad/SOCD hotkeys can request flash saves; A32 analog D-pad hotkeys may affect digital directions.
- Other details in audit; do not reopen already resolved items without new evidence.

## Next tasks (offline, in priority order)
1. **Independently locate original hardware-proven Caveman source or binary** and verify LOAD polarity, edge phase, slot mapping, frame termination, timing, and rearm behavior. Earlier GitHub searches did not locate original; no parity claim yet.
2. **Upgrade the model from truth-table/level examples to explicit timeline:** separate host driving DATA/LOAD vs responder sinking DATA, clock phases, responder scheduling, IRQ-disable timing, sample moments, adjacent frames, malformed sequences, and short idle gaps. Model physically plausible cases and show a concrete wrong decoded bit or false release before claiming reproduction of LP/LK.
3. Analyze `wait_data(false)` after successful frame and ignored final `wait_clock(true)` together, but use temporal rearm counterexamples to avoid naïve fix. Inspect whether success can return with DATA low under valid host timing.
4. Check Core0 published-mask transitions and Core1 output diagnostics conceptually. Determine how to distinguish processed-mask oscillation vs serial/host misdecode without modifying golden. Exact Street Fighter game bindings need eventual confirmation, but do not demand hardware tests yet.
5. Audit exact Core1 compiled timing/disassembly for 12us deadlines, including atomic operations, USB PHY writes, and release timing. Reconcile snapshot-at-LOAD vs snapshot-at-frame-start latency.
6. Only after a verified failure mechanism: design narrowly scoped **Test15** branch/candidate, add regression tests, preserve all golden Test14 functionality and recovery. Never silently overwrite Test14.

## Repo/checkpoint hygiene
Latest verified source/model commits include `281c7df7463cb1a2e7bc54d0824b85922ffb8a80` (upstream comparison), `197a7cacde8a497efe683735e227950decc938df`, `f91573b2a5e9ff1841e810325880ac41a4edfdbe`, `d95d0e81393e62bbd8891d5c25f5e30eff245eed`. New handoff commit supersedes as branch tip. Research findings and tests were checked by GitHub fetch. **No Test15 firmware built or hardware flashed.** User's raw configuration backup is private.

## User's immediate intent
Continue from this exact point; no restart. They are frustrated that comprehensive audit missed real held-button, tap and cross-button failures. Prioritize evidence-backed engineering progress, not speculative theories, repetitive test requests, or lengthy status-only replies.
