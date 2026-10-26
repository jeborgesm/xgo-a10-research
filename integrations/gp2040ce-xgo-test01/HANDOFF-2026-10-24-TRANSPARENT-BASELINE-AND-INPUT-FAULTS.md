## CURRENT ELECTRICAL LEAD 2026-10-26 — RELEASED DATA IS HI-Z WITH THE RP DP PULLUP DISABLED

[New authoritative host-MIPS/source electrical-bias finding](findings/2026-10-26-PHYSICAL-DATA-HIGH-BIAS-OWNERSHIP.md), [read-only original image and protected driver verifier](tests/verify_xgo_data_line_bias_contract.py), [GREEN CI #40380342382](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40380342382). Reverified original `XGoAnalisis.zip` exact SHA and 11 opcodes locally: host L0 GPIO OUTPUT LOW during LOAD, switches L0 DIR to INPUT @0x8035D864 then reads L0 @0x8035D890 before clock. Pinned GP2040 transparent A DP=DATA has `phy_direct=0` with **DP_PULLUP_EN override ENABLED**, forcing its own DATA pull-up OFF; `data_release()` only disables LOW output (Hi-Z). It cannot itself actively restore a HIGH released DATA. Thus proper HIGH must come from XGO PCB/pin bias or other external circuit, **whose existence/strength/voltage on Frankie is not yet established**. P0 earlier observed delayed digital HIGH, so NEVER claim the XGO has no pull-up. Passive USB PHY plus probe caused ghost P2 jumps earlier with a different cable; likely electrical class, not guaranteed identical current root. Unchanged ghost rate in user's native-R A-B-A demoted small first-sample timing. DM pull-up override on CLOCK previously froze hardware; do NOT repeat or blind-enable DP pullup. The next engineering task is validate DATA bias/current/rise and design one qualified reversible line-level correction, retaining transparent 12-slot mapping/hold semantics. Paginated OLED candidate B remains unflashed for separate missed-short-taps bottleneck. No firmware, BIOS, cable or physical tests were performed this turn.

---

## CURRENT OWNER-DEFINED GOAL: MAKE THE CONTROLLER RELIABLE IN EVERY GAME (2026-10-26)

User explicitly rejected ROM/keymap detour: "why are you checking the Contra Rom ??/ what we need is to make the controller work reliably." Treat Contra only as a recognizable symptom; no .kmp inspection, ROM search, remapping or per-game workaround as next gate. **[New binding controller reliability acceptance contract](findings/2026-10-26-CONTROLLER-RELIABILITY-IS-THE-OBJECTIVE.md).** Goal: with idle external GP2040 XGO reads zero bits, with a button held reads exactly the correct held slot every host scan, valid transitions remain accurate, no false START/JUMP, no shifted/missed buttons, both logical Handle=P1/P2. Current protected A and GOLD behavior unchanged; this is target, not a claim of success.

HW negative local-R A-B-A remains authoritative, so drop branch-dependent timing as leading lever. Investigate electrical DATA turn-around / native USB PHY receiver interaction (passive P3 was ghosting even with output off), and RP clock phase alignment separately. Avoid spending another turn extending synthetic host models unless they directly discriminate an actionable controller-side modification. No blind RP output-high/pull changes or GP2040 turbo pulses, no GOLD `bisrv.asd` modifications, no special Frankie cable changes; keep golden A and OLED B unflashed.

---

## LATEST 2026-10-26 — VERIFY EXACT P2 CONTRA INPUT ORIGINS, DO NOT ASSUME R0

[New source/BIN report and forensic program](findings/2026-10-26-CONTRA-P2-ACTIVE-KEYMAP-EVIDENCE-AND-FAULT-SOURCE-GATE.md), [exact existing .kmp read-only parser](../../tools/xgo-protocol-audit/audit_fc_keymap.py), [regressions](../../tools/xgo-protocol-audit/test_audit_fc_keymap.py), [GREEN CI #40334342549](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40334342549). Owner native-R A–B–A actual HW test was **NEGATIVE**: spontaneous P2 Contra jumps in all 3 conditions, about the same rate; no support for four-extra-native-R-instructions being sufficient to alter ghost behavior, no reason to repeat. Original stock XGO NES embedded fallback is verified BIN at `0x8ddd34`, 12x32-bit records: each player `X=0x10008, Y=0x10000, L=0x10000, A=8, B=0, R=0x10008`. **R/X/A all map to Jump** under fallback; PAUSE may involve physical START slot7 or custom logical START-targets, and historical Test49 does NOT prove same mechanism as current protected A. The *actual* Contra per-ROM P2 .kmp is unknown; archives locally mounted contain NONE, which does not prove the SD has none. New forensic script reads exact 48-byte profile to distinguish P2 mappings, does NOT patch files or firmware; tests include P2 asymmetric override and custom logical START/SELECT IDs. Exact ROM basename and FC/save profile are required to promote fallback interpretation to current-game fact. Work remains OPEN on host-decoded physical P2 DATA. Protected XGO GOLD BIOS, physical GP2040 transparent A, Frankie wiring and unflashed OLED B unchanged.

---

## LATEST OWNER HW NEGATIVE — NATIVE R RELEASED/HELD/RELEASED DOES NOT CHANGE LOGICAL P2 PHANTOM JUMP (2026-10-25)

[New exact owner witness report](findings/2026-10-25-HW-NATIVE-R-ABA-NEGATIVE-CONTRA-P2-GHOST-JUMPS.md); [former design gate now marked EXECUTED/NEGATIVE](findings/2026-10-25-NATIVE-R-HANDLE-P2-NO-FLASH-AB-GATE-AND-DMA-VERDICT.md). User performed Handle=P2 Contra comparison with external GP2040 physically untouched: native R **released A1** yielded spontaneous P2 JUMPS; native R **held B** yielded spontaneous P2 JUMPS; native R **released A2** yielded spontaneous P2 JUMPS. User: "P2 still jumps no matter if the Native R is held or not in about the same rate." No exact counts, so not a statistical equality claim. Real original BIN native R press executes four extra instructions before external Handle R0 read, but **no observable sensitivity to that particular small timing path**; deprioritize simplistic early-R read explanation. Electrical loading/slow release not excluded if both read paths affected. This test in logical P2 also shows P1 raw Handle OR merge is not required for *current observed P2* ghosts.

Do not infer actual false R specifically from visible Contra JUMP: NES embedded FALLBACK has jump mapped by R0, X2, A4; actual loaded per-ROM P2 .kmp UNKNOWN (local XGoAnalisis.zip 115 members, **no .kmp / no Contra path**; other locally mounted ZIP artifacts also lack it). Historical Test49 phantom PAUSE points beyond simple false first button but source/cable differ. No new firmware/cable test performed beyond owner's A–B–A. No GP2040, GOLD, DM-pullup, Frankie or OLED changes. Next evidence target: matching actual P2 Contra .kmp and/or nonperturbing decoded-host/actual physical DATA/CLOCK during spontaneous jump; do not repeat this already completed HW trial.

---

## LATEST 2026-10-25 — VERIFIED BUILT-IN R EFFECT ON HANDLE R0 SAMPLE; NO-FLASH A-B-A TEST GATE

[Detailed electrical-test decision and DMA exclusion](findings/2026-10-25-NATIVE-R-HANDLE-P2-NO-FLASH-AB-GATE-AND-DMA-VERDICT.md). Original XGO `XGoAnalisis.zip` verified locally against exact MIPS opcodes: B15 native R **released HIGH** branches straight from 0x8035D878 to external physical L0 R0 read 0x8035D890; native R **pressed LOW** executes four additional instructions. Full duration/voltages OPEN. Because GOLD logical Handle=P2 keeps the external physical stream mapped to logical P2, a **reversible physical no-flash A-B-A experiment** can observe spontaneous P2 Contra JUMP with untouched GP2040 and native P1 R RELEASED→HELD→RELEASED. P1's intentional R/turbo jump during B must not be mistaken for P2 ghosting. Consistent reduction in ghost P2 during B supports timing sensitivity but does not distinguish analog DATA rise from timing/clock entry. No hardware result yet; comparison still pending user's opportunity.

No new probe or modification to Frankie connector permitted; historical passive native PHY attachment itself caused P2 jumping. RP2040 DMA captures via PHY register possible **in principle** per Pico SDK, but 10MHz 32bit = **40MB/s reads + 40MB/s writes**, ~80MB/s shared bus traffic, which may create/alter RP polling faults; timestamp uniformity and host R decode remain unknown. Do not build/flash as noninvasive capture without qualified interference. Preserve existing transparent UF2 A/GOLD; OLED-page B unflashed.

---

## LATEST 2026-10-24 — P0 PER-FRAME DIGITAL TRACE ANALYZER GREEN CI; ROOT CAUSE STILL OPEN

[Forensic checkpoint](findings/2026-10-24-P0-PER-FRAME-FORENSIC-DIAGNOSTIC.md): new [P0 analyzer](../../tools/rp2040-xgo-p0/analyze_frames.py) and [four synthetic tests](../../tools/rp2040-xgo-p0/test_analyze_frames.py), [CI SUCCESS #40163021139](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40163021139). Runs **host-side** on existing 10MHz passive PIO two-bit `BEGIN XGO_P0` dumps; no Pico firmware modification. Separates per-frame 12 pulse count anomalies, clock LOW/HIGH min/max and >18us stretches, DATA load/release offset to first CLOCK, and DATA transitions; exports JSON/CSV. Tests verify two valid frames, eleven-clock input, both stretched clock phases, and DATA near initial R-bit ambiguity. Existing fast-serial regressions remain GREEN.

**Critical hardware proof gap:** XGO original BIN reads external R/slot0 **BEFORE first CLOCK fall**, so DATA voltage at first CLOCK fall is not the actual host-decoded R. P0 digital threshold captures alone cannot reveal the MIPS read strobe, actual host threshold, analog rise time, or current Frankie V2 Jr PHY timing. No saved complete P0 raw dataset is present in the repository; previous P0 timing data is summarized in historical HW notes. Historical P0 loose-wire probe differs electrically from the current Frankie bridged connector and probe connections previously induced P2 phantom jump. Do not attach extra Pico casually or claim old P0 is current fault capture.

The protected transparent A `XGODriver.cpp` and XGO GOLD firmware remain unchanged. The optional paged OLED B stays unflashed. A proper independent nonperturbing electrical DATA/CLOCK capture is still needed; do not manufacture a new firmware timing fix from this tool alone.

---

## LATEST — REAL P0 CLOCK HIGH IS ~1.36US AVERAGE; PROTECTED ARM POLLING LOOP AUDITED (2026-10-24)

The source-first reliability investigation found a material correction to previous host models. Actual P0 **10MHz digital HW** complete 12-pulse capture (from `experiments/rp2040-passive-probe-p0.md`): clock first FALL 13675.5µs, last RISE 13723.6µs = **48.1µs** span. Individual 12 LOW widths sum **33.1µs** = mean LOW 2.7583µs, leaving **15.0µs** across **11** inter-pulse HIGH gaps = **mean HIGH 1.3636µs** (not the 2/2µs assumed in older models). These are one historical P0 frame, NOT actual current Frankie trace, individual HIGH minima UNKNOWN.

Recovered protected transparent A **actual linked ARM disassembly** from GitHub Actions run `40071967532`, ELF audit artifact `12551597007`, disassembly SHA256 `482031f65ae7d58f50174d6c4842a83794a9b216c0eb9845bca8dcb734b0564d`. User-tested `emit_frame()` really linked in SRAM @`0x200000f0`. Both `wait_clock(false)` and `wait_clock(true)` are **inlined 7 Thumb-instruction polling loops** (MMIO Timer 0x40054028 and USB_PHY 0x5011007c, RX_DM 0x40000) with 18us timeout checks; Core1 IRQ masked using PRIMASK across full scan. This confirms a fast source path in principle, not measured maximum observation interval or crossbar stalls. [Exact ELF verifier](tests/verify_transparent_a_linked_clock_waits.py) passed locally against downloaded audit.

[New actual-source P0-derived clock-shape comparison](tests/test_p0_measured_short_clock_high_exact_cpp.py), [GREEN CI run 40161383012](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40161383012): a uniform 2.758µs LOW/1.364µs HIGH aggregate waveform and old 2/2µs model each have **zero errors** across 78 modeled phase/mask cases at synthetic read-call advance 0.035–0.50µs. Both show missed/wrong bits at much slower invented observation advances (0.70µs and above), not proof the current RP is that slow. The modeled step is advanced **for each Timer/PHY read** and must not be described as a measured polling interval. P0 aggregate HIGH is real but short-HIGH alone does NOT establish the source of ghost R or held action losses.

[Complete new evidence report](findings/2026-10-24-P0-CLOCK-HIGH-DUTY-CYCLE-AND-LINKED-RP-POLL-LATENCY.md) separates HW/SRC/MODEL/OPEN, and supersedes any prior claims that physical XGO is proven 2µs LOW/2µs HIGH. Continue fault separation: passive native PHY/slot0 DATA recovery is stronger for ghost R; clock-miss / host IRQ-stretch still potential for held-input glitches. Keep protected transparent A source Git SHA `cccb985a05baa8bb9078b6e336eb5f991c1a7a8f`, user-tested UF2 and protected GOLD. No new flashed binary, BIOS edit, Frankie rewiring or user test. Paged OLED B remains unflashed.

---

## NEW 2026-10-24 ORIGINAL XGO IRQ-GATED CLOCK TIMING DISCOVERY + 24 EXACT C++ TESTS

[Full new IRQ/BIN and host clock-stretch investigation](findings/2026-10-24-XGO-IRQ-GATED-SCANNER-AND-HOST-CLOCK-STRETCH-MODEL.md). Actual pinned `XGoAnalisis.zip/bios/bisrv.asd` original SHA `869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf`, [new CP0 helper opcode verifier](tests/verify_xgo_irq_windows_original_bin.py) **PASS locally**:
- Scanner `0x8035D770..0x8035DE04` has **30 helper calls to disable and 30 to enable CPU interrupts**, plus 13 timer delays. These are real helper routines that manipulate nesting counter `gp-0x64F0` and MIPS CP0 Status IE bit0 under normal EXL/ERL conditions.
- **After physical external L0 DATA release `0x8035D864`, IRQ re-enable helper at `0x8035D868` executes before native B15 R read `0x8035D870` and external L0 R read `0x8035D890`**; native R released/HIGH follows shorter external R read path. An actual interrupt could vary that sample interval (no IRQ duration/timestamp measured); increasing the interval does not automatically cause an earlier ghost R.
- For host CLOCK LOW store `0x8035D8BC`, the normal code re-enables IRQ at `0x8035D8C0`, waits nominal 2us at `0x8035D8C8`, disables at `0x8035D8D0`, sets CLOCK HIGH at `0x8035D8E4`. Pattern repeated across scanner; a host IRQ could stretch real clock phases beyond RP's 18us wait budget **without any electrical pulse missing**. This is a plausible *conditional* mechanism, not observed IRQ behavior.

[New exact protected-C++ RP responder synthetic clock-stretch test](tests/test_xgo_irq_stretched_clock_exact_cpp.py), [GREEN CI run #40160377104](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40160377104), 24 cases (normal + 12 clock-LOW + 11 clock-HIGH). Inject +25us host LEVEL delay while retaining all 12 clock pulses. Extended LOW #1–11 yields `CLK error at affected slot 1..11`; LOW #12 yields failed final-HIGH with **no protected A CLK counter increment**. Extended HIGH after #1–11 yields `CLK error at following slot 2..12`. All next normal scans recover held A in this virtual model. Unlike this, a whole RP-unobserved pulse in prior model almost invariably reports terminal S12. This may help interpret old Test48/49 HI/LO/S12 counters but **cannot assign historical errors to real CPU IRQs without waveform evidence**. No changes to protected XGO GOLD / transparent A / Frankie; OLED-page B stays unflashed; no user HW test requested.

---

## 2026-10-24 LATEST: XGO P1 R CONDITIONALLY SHIFTS EXTERNAL R0 SAMPLE; PASSIVE USB PHY GHOST

[New evidence report](findings/2026-10-24-USBPHY-PASSIVE-GHOST-AND-P1-CONDITIONED-P2-R-WINDOW.md). The real original XGO firmware BIN verifier [here](tests/verify_xgo_p1_r_conditioned_p2_first_sample.py) passed on original SHA-pinned `XGoAnalisis.zip`. Native P1 R **released/HIGH** makes MIPS BNE at `0x8035D878` take the short path to L0 physical P2 R0 read `0x8035D890`. Native P1 R **pressed/LOW** executes 4 extra instructions before the P2 R0 sample. This *polarity* and instruction count are confirmed BIN, not a measured voltage or sample timing delta.

[Current-versus-P3 native PHY audit](tests/test_current_phy_passive_ghost_comparator.py), [GREEN CI #40153719664](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40153719664), confirms identical ten PHY override settings, native RX, source P3 output completely disabled. Yet actual passive P3 hardware with ordinary cable caused unsolicited P2 JUMPs, so active transmitted button masks are not necessary for that earlier electrical symptom. Historical forced DM-pullup override froze XGO. P0 actual DATA rise is 0.9–1.3us before first CLOCK FALL; actual first-bit sample before FALL, voltage at that time OPEN. Current working Frankie V2 Jr has a bridge between **physical pads 2 and 4 via WHITE**; earlier passive ordinary cable does not. Do not assume the two conditions have identical electrical loading.

Remain on protected GP2040 transparent controller A, XGO GOLD BIOS, and current Frankie cable; paged OLED B unflashed. No new firmware/hardware tests; no DM pullup changes or timing guesses.

---

## LATEST CI-PASSED EXACT C++ TWO-FRAME REARM + MISSED CLOCK SWEEP (2026-10-24)

New investigation [full bounded fault report](findings/2026-10-24-TWO-FRAME-RECOVERY-AND-SLOT12-ERROR-AMBIGUITY.md), [exact protected responder chronological source test](tests/test_exact_xgo_rearm_two_frames.py), [GREEN CI #40129993336](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40129993336). **No firmware edited.**

The actual protected transparent `emit_frame()` C++ is compiled with a two-frame fake XGO clock/data host at 16.03ms interval. With physical A held continuously, host raw `0x0080`:
- **No fault**: both host scans decode A.
- **RP misses any ONE of host CLOCK pulses 1–11** (host still generates 12): source reports **CLOCK failure at terminal slot12**, regardless of which actual pulse was missed. For missed #1–4 first host reads B `0x0040` instead of A; missed #5 reads A+B `0x00c0`; missed #6–11 still reads A `0x0080`. RP `xgo_diag_clock_timeouts=1`, `xgo_diag_last_failure_slot=12`, even when physical observation fault occurred at pulse1. All eleven **recover to correct A on the next host scan** in this model.
- **RP misses only the final CLOCK HIGH**: first XGO word STILL A, source `complete=false` and rearm occurs, but protected A increments NO `xgo_diag_clock_timeouts` (diagnostic accounting gap unlike Test48/49); next frame A correct.

**Major interpretation:** old OLED S12=421 Test48 / S12=226 controlled Test49 **do not locate failure at last pulse nor count wrong game words**. S12 may reflect earlier missed CLOCK, terminal failure or earlier diagnostic firmware's final-HIGH classification. No source reason yet to attribute a *lasting* 1–2sec unreliable held button to a single timeout+rearm: with normal DATA idle-high between frames, protected rearm returns correctly after one error. Recurring physical electrical faults remain possible, unmeasured. False slot0 R/Jump is a separate acquisition mechanism (can occur with zero CLK errors); **the sweep did not reproduce Jump**. Previous Test35 strict clock-phase gate was HW rejected, do not resurrect. Preserve both protected firmware images and unflashed OLED B; do not force a fix.

---

## LATEST CI-GREEN EXACT SOURCE GHOST/PHASE DIFFERENTIAL — 2026-10-24

New [actual C++ `emit_frame()` chronological fake-host harness](tests/test_exact_xgo_frame_phase.py) extracts **unchanged source** from protected GP2040 transparent A, compiles with g++ and virtual host DATA/CLOCK GPIO. Pinned [successful CI run 40129373359](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40129373359), all existing fast serial regressions PASS. A separately compiled CLOCK-first alternative changes only the in-memory `wait_data(true,18us)` gate for released R0; **NO firmware files are edited**. Both original and alternative pass **4096/4096 physical masks** in the ideal host model.

With physical A continuously HELD and R released, simulated DATA rise after host R sample but before missing CLK #1 yields host `0x1080` (real A + phantom R), *responder reports successful frame and no CLOCK error*, under **both** policies. DATA rise after CLOCK #1 already rose yields: protected A host `0x3040` (R+Y+incorrect B replacing A), terminal slot12 timeout; hypothetical CLOCK-first host `0x3080` (R+Y+correct A), no clock timeout. **False early R/Y persist** under clock-first: therefore a CLOCK-first-only patch is NOT a ghost-jump fix. Separate physical R+A held yields modeled `0x3080` with no timeout because R pre-drive bypasses DATA-high gate, though false Y may still contaminate. All virtual recovery delays/thresholds synthetic and NOT measurements on Frankie V2 Jr.

[Full exact-C++ finding](findings/2026-10-24-EXACT-CPP-RESPONDER-CHRONOLOGICAL-HOST-DIFFERENTIAL.md). Preserve XGO GOLD BIOS SHA `75f858b6d9a1eb81235ae9e9c9b449a6a3052ad4365e5411b8ce041075e99d6b`, transparent A UF2 SHA `94ea7228c774a67e8252e7e09d94938530e5d74572d985332e6840ae09fe8b84`, and unflashed paged-OLED B. Original user's Test48/49 CLK errors are not current A host-bitword captures. Next source-only discriminator: LOAD re-arm/false-start and first-FALL timing cases while maintaining serial transparency; only eventual measured DATA voltage relative to XGO sample can prove first-slot electrical cause. No new user hardware test requested.

---

## LATEST BIN + MODEL: LATE DATA RECOVERY CAN LINK FALSE R AND SHIFTED HELD A (2026-10-24)

Continued actual offline ghost-input investigation without modifying firmware: original user's XGO `XGoAnalisis.zip/bios/bisrv.asd` SHA `869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf` has **both R0 reads before CLOCK**, then exactly **12 host B7 LOW/HIGH pulses** each with nominal 2us LOW, verified via 13 original MIPS delay JAL calls and 24 GPIO stores. Do **not** posit stock XGO only outputs 11 pulses or conflate non-detected 12th pulse with no host pulse.

Protected GP2040 A `emit_frame()` calls `wait_data(true,18us)` for R0 released BEFORE its first `wait_clock(false)` call. Under a deliberately synthetic late HIGH after host CLOCK #1 rose, RP catches CLOCK #2 and emits physical slot4/A during host slot5/B, then expects nonexistent FALL #13 and times out; earlier physical DATA LOW can simultaneously make host falsely read R0 (Jump) and Y1. Exact illustrative model: stable held physical A `0x0080` decoded as `0x3040` (R+Y+B), *not* a captured current Frankie word. Another synthetic scenario generates false R `0x1080` **without CLOCK timeout**. Controlled CLOCK-first alignment policy model would retain held A in that scenario but **would not fix false R/Y**, and may have other unverified tradeoffs. NO firmwares patched, built or flashed based on this model.

**Canonical report**: [Original 12-clock host scanner and DATA-release phase-loss mechanism](findings/2026-10-24-HOST-12-CLOCK-DATA-RECOVERY-AND-GHOST-INPUT-MECHANISM.md). Test sources [actual original BIN verifier](tests/verify_original_xgo_12_clock_train.py), [late-rise phase MODEL](tests/test_xgo_data_release_first_clock_phase.py), [source-policy differential MODEL](tests/test_xgo_clock_first_sync_hypothesis.py). All 3 have passed locally. Preserve XGO GOLD `75f858b6d9a1eb81235ae9e9c9b449a6a3052ad4365e5411b8ce041075e99d6b`, transparent GP2040 A `94ea7228c774a67e8252e7e09d94938530e5d74572d985332e6840ae09fe8b84`; paged-OLED B unflashed. User's requested task remains **investigation**, no unjustified change in direction.

---

## AUTHORITATIVE OWNER CORRECTION: XGO A10 IS WIRED-ONLY — NO WIRELESS CONTROLLER CAPABILITY (2026-10-24)

**Owner's user-supplied HW fact:** Their XGO does NOT support wireless controllers. The Micro-USB-shaped Handle port is the **wired controller interface**. The previously speculated SF900-on-XGO wireless use was incorrect; **do not propose pairing/testing the SF900 with XGO**. Original XGO `bisrv.asd` contains inherited SF2000 RF software/protocol tables [BIN], but this is **software lineage, not evidence of a functional/populated receiver or wireless capability**. The SF900 pads demonstrably work on the **separate SF2000**, and their radio code is a conceptual comparator, NOT a replacement or feature path for our wired GP2040-CE. Preserve the actual physical XGO B15/L0/B7 DATA/CLOCK scanner + GP2040 responder and user-tested Handle=P1/P2 GOLD normalizer as the only operative controller transport/role architecture.

This explicit statement **supersedes any previous HANDOFF passages suggesting board RF population is an OPEN engineering lead or that the user might test SF900 on XGO**. No hardware test requested; no firmware changes. [Correction on the SF900 comparison](findings/2026-10-24-SF900-SF2000-KNOWN-GOOD-RF-VERSUS-XGO-HANDLE.md).

---

## SF900/SF2000 KNOWN-GOOD RF COMPARATOR — NEW OFFLINE EVIDENCE (2026-10-24)

User owns SF900 wireless controllers that reliably operate their SF2000 and select P1/P2 with physical switch. User suggested comparing those with ongoing XGO/GP2040 transparent-controller fault research, **not changing direction or requesting a radio redesign**. Work completed offline:

- **XGO original BIN verified**: the five stock SF2000/SF900 XN297L RF channel/address/calibration sequences are each present exactly once at 0xC2D0E8..0xC2D10C; MIPS at 0x35D6E8 RX-ready 0x40, 0x35DE44 payload command 0x61, 0x35DE4C 2-byte length, and 0x35DE7C P1/P2 status 0x02. Exact original `bios/bisrv.asd` hash 869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf. Read-only verifier PASS.
- **Upstream SRC cross-check**: pinned 2026-10-24 UniFrog XN297L driver and independently implemented ESP32-S3 SF900 receiver confirm `raw=(pkt[0]<<8)|(~pkt[1]&255)`, status/pipe P1=0x40, P2=0x42, all twelve XGO pressed-button masks match. Wireless uses complete CRC-protected packets; wired XGO remains vulnerable to host-driven DATA release and bit0 sampling. Hardware XGO RF receiver population **still OPEN**.
- **Specific wired family clue:** current *UniFrog replacement SF2000/GB300 scanner* inserts deliberate **4us DATA settle** after 4us host LOAD-low and before sampling R0; original XGO host scanner explicitly lacks the same settle. This is SRC design evidence and a falsifiable comparator, **not stock SF2000 proof, XGO measured threshold, or permission to patch GOLD firmware**.
- Offline MODEL PASS: 4096 distinct button masks in P1 and P2 from a correctly decoded RF packet match XGO's correctly decoded wired serial bits; hypothetical first-slot false R can contaminate only the wired acquired state in this constructed comparison.

[Full SF900/SF2000 comparison](findings/2026-10-24-SF900-SF2000-KNOWN-GOOD-RF-VERSUS-XGO-HANDLE.md), [original XGO RF byte verifier](tests/test_sf900_sf2000_rf_lineage_original_xgo.py), [4096x2 mask model](tests/test_sf900_xgo_button_state_boundary.py). Preserve XGO GOLD firmware and user-tested GP2040 A, paged OLED B stays unflashed. No new hardware trials.

---

## NEW RETROSPECTIVE — OLED ERROR COUNTERS WERE REAL RESPONDER TIMEOUTS, NOT CONFIRMED WRONG BUTTONS (2026-10-24)

The user's observation that diagnostic OLED screens *always recorded errors* is supported by hardware photo logs. Test48 final **ERR=628=CLK597+REL31**, of which **S12=421**. Test49 controlled final **CLK=320, S12=226**; phantom JUMPs and unsolicited PAUSE occurred before/during those photos while GP2040 P0..P4 processed-edge counts stayed zero. **~70% of CLOCK timeouts were classified as slot12 in each final photo**, yet S12 can be missed *terminal falling edge* OR missed *trailing rise* **after all 12 button slots were output**. Those may be false-negative completion status without wrong XGO bits. Conversely 176 Test48 and 94 Test49 controlled errors classified at **non-S12** clock waits and present a stronger mid-frame integrity risk. Derived accounting lower bounds: at least 304 of 421 Test48 S12 and 165 of 226 Test49 S12 were terminal **falling** timeout classifications, using available LO/HI totals. This distinction is SOURCE+HW-RETRO, not a current firmware error frequency measurement.

[Complete retrospective + source-path comparison](findings/2026-10-24-OLED-ERROR-COUNTERS-RETROSPECTIVE.md), [reproducible numeric reconciliation](tests/test_historic_error_counter_reconciliation.py). These were **RP2040 local timed-wait diagnostic counters**, not XGO host's receipt acknowledgments. The protected new transparent A retains 18us waits and terminal-edge logic, but final-high error accounting differs from old Test48/Test49, so rates cannot be projected forward. No current A serial waveform/counter captures. Prioritize DATA release and host CLK synchronization in the physical external L0 channel; do NOT infer from many diagnostic errors that every XGO game bit was wrong. Keep XGO GOLD and transparent A unchanged; OLED-page-only B CI verified/unflashed.

---

## NEW HW RESULT — EXTERNAL HANDLE=P2 IN CONTRA FEELS WORSE; RANDOM JUMPS AND INTERMITTENT A/B ACTIONS (2026-10-24)

**User now compared external-controller roles:** With the XGO native GOLD Handle=P2 selection, the external GP2040-CE character in Contra jumps unexpectedly and **physical A or B holds** produce jump/fire actions intermittently, informally ~1–2 seconds apart; user says P2 feels worse than P1. These are *visual/gameplay* observations, **not** measured host bit cadence or proof that the RP2040 produces periodic tap pulses. This differs from earlier HW: Handle=P1 selected, built-in P1 gameplay, external connected but untouched, also phantom JUMP. No new built-in P1 observation under Handle=P2 was supplied.

**Revised diagnosis:** Because Handle=P2 feeds the L0 serial stream to logical P2 without P1 OR merge, **P1 mode routing is not necessary for ghost JUMP**. The Handle serial clock/DATA PHY is physically unchanged by the logical toggle, so P2 feeling worse does not establish worse transmitted timing; per-player keymap/game interpretation remains possible. The **actual transparent responder source** when R/slot0 is released calls `wait_data(true,18us)` before emitting later bits. Late electrical DATA recovery can hypothetically generate a false slot0 R and delay/abort later held A/B serial output. Aborted response does not imply clean host bits, because the wire may remain LOW. This connects two failure classes as a testable timing hypothesis **without claiming actual Frankie measurements or a verified cause**. A correctly held bit transmitted on every ~16ms scan is not made intermittent over seconds just because the OLED takes ~23ms per Core0 loop; the user's ~1–2s is an action impression, not waveform timing.

**New canonical addendum:** [updated actual-P1/P2 investigation](findings/2026-10-24-CORRECTION-HANDLE-P1-ACTUAL-TEST-CONFIGURATION.md). Keep XGO GOLD and transparent RP2040 firmware A unchanged; paged OLED B unflashed, no speculative turbo/pulse/cable/PHY tweaks.

---

## CRITICAL NEW HW FACT — BUILT-IN P1 CONSTRAINED GHOST INPUT WITH EXTERNAL IDLE (2026-10-24)

The user now confirms an essential discriminator: while GOLD XGO Setup **Handle=P1** is selected and the GP2040-CE remains **physically connected but untouched**, they play Contra **using the XGO built-in P1 controller** and nevertheless observe occasional uncommanded **logical P1 JUMP**. This rules out intentional external keypresses as a necessary trigger, NOT false external serial bits. The GOLD native normalizer ORs physical P1/B15 with physical Handle P2/L0 into logical P1; local activity **does not disable or take exclusive priority over the attached external channel**. Correct OR alone fabricates nothing; a transient false pressed bit from either stream, RF P1 (if active), or downstream keymap/game behavior remains possible. Prior passive P3 attached-idle ghost is analogous but electrically different and not a proof for current Frankie. **No P2-mode / unplugged comparison has been performed in this new report**.

[Latest exact observation, causal constraints, and future single-mode discriminator](findings/2026-10-24-CORRECTION-HANDLE-P1-ACTUAL-TEST-CONFIGURATION.md). With current external connected and untouched, a future controlled change **only Handle=P1→P2** while continuing built-in P1 play could test whether the routed Handle stream is needed for the false P1 action; disappearance in one short play session would still not prove a cure due to intermittency. This is NOT a request for repeated trials now. No RP2040 firmware or XGO GOLD BIOS modification, no button suppression. Distinguish from earlier SFII LP observations, for which the user did not specify this same built-in-only usage.

---

## CRITICAL NEW HW CONTEXT — RECENT SFII/CONTRA TESTS WERE LOGICAL P1 (2026-10-24)

The user explicitly clarified that ALL their recently reported transparent-controller gameplay observations (SFII defeated Dhalsim; LP missed/triple punch; Contra playable with/without X/Y native turbo and intermittent unsolicited JUMP) were observed with the **XGO native Setup Handle=P1 setting selected**. This is not ordinary stock Handle=P2 gameplay. The **RP2040 still transmits on the physical Handle P2/L0 serial line**; the GOLD XGO firmware merges **built-in physical P1/B15 OR physical Handle P2/L0** (plus existing P1 auxiliary input) into **logical P1** at the native normalizer. It suppresses physical Handle contribution to logical P2. Full source/binary provenance, verified GOLD hashes, correction of fault attribution, and 3,200-case SOURCE-derived MODEL are in [CRITICAL actual-P1 configuration findings](findings/2026-10-24-CORRECTION-HANDLE-P1-ACTUAL-TEST-CONFIGURATION.md).

**Binding correction:** P2-slot0 scanner remains physically relevant, but current user-visible JUMP/LP actions are **P1 game input** and can arise from either physical channel or downstream P1 mapping. A correct OR merge cannot fabricate a pressed bit. Prior P2-only claims for the recent tests are superseded. Historical P2 passive probes remain P2 observations. Do not confuse this GOLD XGO host BIOS with the separate protected GP2040 transparent UF2. Neither device's firmware was modified in response to this clarification.

**Additional original-BIN correction (2026-10-24):** `0x8035D54C: sw zero,0(a0)` clears the **logical** output word because `a0` is repointed to `gp-0xd18` at `0x8035D534`. The older Handle investigation's claim that this instruction clears **raw serial** was wrong. The actual raw serial inputs are explicitly reset at **scanner entry** `0x8035D780` / `0x8035D788`. Verified all 13 opcodes from the hash-pinned original XGO archive; see [full correction and 13-opcode verifier](findings/2026-10-24-CORRECTION-HANDLE-P1-ACTUAL-TEST-CONFIGURATION.md). Alternate normalization-loop entry is NOT by itself proof of synthetic release. No changes to GOLD firmware.

---

# XGO A10 / GP2040-CE — DEFINITIVE ENGINEERING HANDOFF

**Checkpoint:** 2026-10-24, after user's successful transparent-controller gameplay test and subsequent offline OLED-pagination investigation  
**Repository:** `jeborgesm/xgo-a10-research`  
**Work branch:** `research-gp2040ce-xgo-integration`  
**Main living handoff:** `integrations/gp2040ce-xgo-test01/HANDOFF-CURRENT.md`  
**This document:** `integrations/gp2040ce-xgo-test01/HANDOFF-2026-10-24-TRANSPARENT-BASELINE-AND-INPUT-FAULTS.md`  
**Priority:** Preserve what works. Distinguish current hardware facts from simulations and hypotheses. Do not restart archaeology.

## 0. REQUIRED FIRST READ / OVERRIDING USER RULE

The user explicitly mandated a **non-negotiable GP2040-CE controller-transparency contract**:

> GP2040-CE must function as a controller, not an emulator-specific input interpreter. A physical press is reported pressed; a held button stays reported pressed; a sampled release is reported released. The XGO alone determines logical actions, keymaps, turbo, repeats and all game/emulator behavior.

This applies to all **12** wire bits; no X/Y exception, no 18ms edge-to-pulse mask, no RP2040 autofire, no game-aware filtering, no gameplay-conditioned input suppression, and no fabricated press or release to mask an electrical symptom.

Read and obey:
- Root `AGENTS.md`; local `integrations/gp2040ce-xgo-test01/AGENTS.md`;
- `integrations/gp2040ce-xgo-test01/CONTROLLER-TRANSPARENCY-CONTRACT.md`;
- Source preflight `integrations/gp2040ce-xgo-test01/tests/test_controller_transparency_contract.py`;
- `integrations/gp2040ce-xgo-test01/HANDOFF-CURRENT.md` (newest addendum first; old contradictory pulse-era instructions are HISTORICAL ONLY).

**The new transparent controller is the positive hardware baseline.** The historically hardware-proven **Test44** still exists as an emergency rollback artifact but its 18ms attack-pulse behavior is ARCHITECTURALLY INVALID. Do NOT return to Test44's pulses as a “fix” for missed inputs.

## 1. USER'S EXACT LAST HARDWARE OBSERVATIONS — DO NOT INVENT MORE

The user flashed/tested the **transparent physical-state controller** (NOT the later paged-OLED trial), UF2 SHA-256:

`94ea7228c774a67e8252e7e09d94938530e5d74572d985332e6840ae09fe8b84`

They reported:
- **Positive:** Holds arrive as holds and taps as taps; **Street Fighter II** was playable as intended and they beat **Dhalsim**.
- **Positive:** **Contra** was playable with and without X/Y turbo. GP2040-CE is not implementing turbo; XGO/game keymap creates repeat behavior when it receives physical held bits.
- **Problem A:** Contra **still spontaneously jumps at random** without intentional jump input. This problem persisted across earlier controller firmware experiments as well; **not resolved**.
- **Problem B:** SFII is **not perfect**: while LP was held once, the game produced **three fast punches**; on another LP hold, the game did **nothing / apparently missed the press**. User suspects some inputs are being lost.
- **Only these observations** were supplied. No new timing capture, OLED error counts, exact physical LP duration, actual I2C bitrate measurement, per-game `.kmp` inspection, or verified RP2040 GPIO trace for this firmware. Do NOT fabricate any.

**Separate acceptance verdicts:** transparent held/tap behavior = **HW-positive**; completely reliable attack recognition = **OPEN**; absence of Contra phantom jump = **FAILED/OPEN**; causality of triple LP = **OPEN**.

User expressly requested deep investigation and **small, targeted corrections** to this already useful controller, not a complete rebuild or speculative new hardware projects.

## 2. TWO FIRMWARE IMAGES — NEVER CONFUSE OR OVERWRITE THEM

### A. Protected, USER-TESTED, hardware-positive baseline (currently preferred)

- File: `XGO-Transparent-Controller-RESTORED-OLED-HARDWARE-UNVERIFIED.uf2` (the historical filename still says UNVERIFIED; the USER SUBSEQUENTLY TESTED IT).
- **SHA-256:** `94ea7228c774a67e8252e7e09d94938530e5d74572d985332e6840ae09fe8b84`.
- Size: **2,515,456 bytes**; 4,913 blocks.
- Exact trial source commit: `2ff4d85b226539350921fece221b266504792ea4`.
- [Build and RP2040 audit 40071967532](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40071967532) **SUCCESS**.
- [Fast real-C++ input-to-wire model 40071967462](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40071967462) **SUCCESS**.
- GitHub Actions firmware package artifact: **12551696668**, name `XGO-TRANSPARENT-CONTROLLER-RESTORED-OLED-UNVERIFIED`; ELF audit artifact **12551597007**.
- Transparent driver: `candidates/offline-test44-transparent-controller/XGODriver.cpp`, exact Git blob `cccb985a05baa8bb9078b6e336eb5f991c1a7a8f`.
- Pre-diagnostic OLED screen: `candidates/offline-test44-transparent-controller/ButtonLayoutScreen.cpp`, exact Git blob `d15cfdc4953647c9d67e7467e244bf5da7233d76`.
- Source is pinned to GP2040-CE upstream commit `3d1f32f7d02d418826b725b60208278d3be878c3` and Pico SDK **2.3.1**.
- **Keep the exact UF2**: do not replace the sole copy or claim later candidates supersede it before actual hardware results.

### B. NEWER, BUILT AND BYTE-VERIFIED, **UNFLASHED** paged-OLED trial

- File: `XGO-Transparent-Controller-PAGED-OLED-HARDWARE-UNVERIFIED.uf2`.
- **SHA-256:** `5dcc28132ca54293a3d27dc2a452269bc47a1e7f141bd49c2c7e296918071b5b`.
- Size **2,515,968 bytes**; 4,914 blocks.
- Source commit `cce1b948d1af9b7cbf0138c802ec63426155bbe2`.
- [Actual C++ fast tests 40107598212](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40107598212) **SUCCESS**.
- [Full RP2040 build/ELF audit/UF2 packaging 40107598214](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40107598214) **SUCCESS**, status confirmed.
- GitHub package artifact **12565735941**, name `XGO-TRANSPARENT-CONTROLLER-PAGED-OLED-UNVERIFIED`; ELF audit **12565402520**, name `XGO-TRANSPARENT-PAGED-OLED-LINKED-ELF-AUDIT`.
- Only candidate code change relative to A: `candidates/offline-transparent-page-oled/tiny_ssd1306.cpp`, Git blob `e441ecc441a1d495413fbd56171a9a72e7321883`.
- **UNCHANGED from A:** transparent driver blob `cccb985a...`, OLED button-layout screen blob `d15cfdc...`, twelve-slot mapping, PHY setup, 18µs CLOCK timeout, frame recovery, and non-XGO behavior.
- Compared the linked **time-critical ARM Thumb instruction encodings** in the two actual ELF binaries: **133 instructions 0x20000156..0x20000260 are byte-for-byte identical**. `emit_frame()` resides in RP2040 SRAM at `0x200000F0`, 728 bytes, 161 statically reachable IRQ-masked instructions, **ZERO reachable calls and ZERO FLASH/XIP calls** in masked paths.
- Verified actual ZIP UF2 magic, SHA-256 vs manifest, block count; downloadable through GitHub Actions run artifacts. The ChatGPT sandbox links from prior chats may expire; **do not invent or reuse sandbox links without re-creating/verifying files this turn**.
- **Status: NOT TESTED BY USER ON HARDWARE.** It is a narrow OLED scheduling experiment, not an approved final firmware or a proven cure for any of the remaining symptoms.

**Never tell the new chat that candidate B was flashed or that it fixed SFII or Contra.** Do not silently replace protected image A.

## 3. XGO CONTROLLER PHYSICAL PROTOCOL — HARD-WON FACTS

- Proprietary **12-bit synchronous serial** on the XGO controller connector, **NOT** USB HID despite RP2040 USB hardware being used.
- The RP2040 uses the **native USB PHY in direct override mode**: USB `DM` is input XGO CLOCK; USB `DP` is bidirectional open-drain-like DATA. RP2040 sinks DATA for pressed bits by asserting `TX_DP_OE`, otherwise releases to **high-impedance**; never push-pull drives DATA HIGH.
- Host asserts a DATA/LOAD LOW pulse around **6.8–7.8 µs** in recorded cases and then releases; first CLOCK falling edge follows approximately **1.2 µs** after DATA release in an early P0 hardware capture; nominal CLOCK period around **4 µs**; XGO scans at approximately **16.03 ms**. Captures vary; do not convert isolated figures into worst-case guaranteed margins.
- **Slot0 has no preceding CLOCK edge**. Original XGO MIPS32 host scanner in user-supplied `bios/bisrv.asd` **BIN evidence**: reads P1 B15 first bit at `0x8035D870` and P2 L0 first bit at `0x8035D890`, **before** driving CLK LOW at `0x8035D8B0`; then samples later bits on clocked steps. Exact bisrv SHA-256 `869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf`. **Never modify bisrv.asd**.
- Zero-based serialization:
  | Slot | Physical GP2040 input | Semantic layer |
  |---:|---|---|
  | 0 | R1/R | XGO per-game/default mapping; NES default may map to A/JUMP+turbo |
  | 1 | B4/Y | XGO mapping; NES default B/SHOOT+turbo |
  | 2 | B3/X | NES default A/JUMP+turbo |
  | 3 | L1/L | NES default B/SHOOT+turbo |
  | 4 | B1/A | NES default A/JUMP |
  | 5 | B2/B | NES default B/SHOOT |
  | 6 | S1/SELECT | SELECT |
  | 7 | S2/START | START/PAUSE |
  | 8 | UP | UP |
  | 9 | DOWN | DOWN |
  | 10 | LEFT | LEFT |
  | 11 | RIGHT | RIGHT |
- **Game mappings are XGO-owned.** A per-ROM `.kmp` can override embedded defaults. A visual Contra jump does **not** identify a unique failed serial slot; R0, X2 or A4 could cause jump under the stock embedded FC fallback.
- Stable original behavior from `Test27`: pre-drive an intentional pressed R/slot0 as an open-drain sink a few µs into LOAD-low; for released slot0, wait for DATA HIGH and leave Hi-Z. This is still in transparent firmware. It is NOT a fix for host-side slow HIGH recovery.
- Code uses 18µs per CLOCK transition timeout; do not arbitrarily shorten to 6µs/4µs (nominal synthetic host regressions) or change phases without grounded evidence.
- Frankie V2 Jr working cable has special shared pad wiring (pads 2 and 4 share WHITE); **do not rewire**. Older P3 passive experiment used an ordinary cable; hardware behavior is not electrically equivalent across these cases.

## 4. TRANSPARENT DRIVER: WHAT IS ACTUALLY FIXED

`XGODriver::process()` on Core0 snapshots the twelve physical inputs via `map_mask()` and publishes a coherent `std::atomic<uint16_t> published_mask` using release ordering; Core1 `emit_frame()` loads it (acquire) at host LOAD, sends `const uint16_t mask = physical;`, and physically sinks/releases the DATA wire at each slot.

There is **NO** `ATTACK_PULSE_US`, `attack_pulse_mask`, special X/Y pulse exception, event-generation SPSC queue, controller-side auto-repeat clock or emulator lookup.

Preserve:
- Exactly accurate pressed/held/released state for **all 12 bits** across multiple scans.
- Existing original Test13-style OLED controller graphics, physical input highlight and pressed-history bottom row.
- The original SELECT+START+R1 LED shortcut / non-XGO functions.
- Core1 critical responder and helpers in SRAM, no flash-resident call under disabled IRQ; do not reintroduce spinlock-13 atomic helper under IRQ mask.
- Existing 18µs timeout and LOAD-high recovery sequence **unless** independent evidence supports a controlled, tested improvement.
- Physical input mapping unchanged.
- Protected test/source variants preserved unchanged; do not overwrite original Test44, transparent driver, or trial A.

[Fast compiled C++ tests 40071967462](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40071967462) cover all **4096 button combinations**, all **12 holds/releases** over eight host scans, simultaneous chords, short captured taps, **150 RIGHT+FIRE sequences**, **22 midframe abort/recovery** paths and independent synthetic host CLOCK. This establishes source/model behavior in tested schedules, **not** RP2040 electrical reliability.

## 5. NEW OFFLINE INVESTIGATION RESULT: CORE0 BLOCKING OLED TRANSFER

The pinned GP2040-CE architecture + XGO overlay places serial polling on Core1 and moves auxiliary OLED drawing onto Core0 by calling `xgo_aux_tick()` **on every Core0 input loop**, with no frame-rate limit.

Actual source path:
```text
GP2040::run() / Core0
  -> scan/read/debounce physical Gamepad, add-ons, XGODriver::process()
  -> xgo_aux_tick()
     -> GP2040Aux::processOnce()
       -> DisplayAddon::process()
         -> GPScreen::draw()
           -> GPGFX::render()
             -> GPGFX_TinySSD1306::drawBuffer()
               -> PeripheralI2C::write()
                 -> i2c_write_blocking()
```

The old firmware synchronously writes a **1025-byte SSD1306 whole frame** or **8×131-byte SH1106 pages** each update before Core0 can sample Gamepad again.

At nominal default 400kHz I2C (saved settings might override, actual bus speed not measured):
- Original SSD1306: **23.063 ms nominal wire time** (1025 × 9 ÷ 400000).
- Original SH1106: **23.580 ms**.
- Candidate B single page SSD1306: **129 bytes / 2.903 ms**.
- Candidate B single page SH1106: **131 bytes / 2.948 ms**.
- Real end-to-end loop duration also includes commands, software overhead, clock stretching and other add-ons; these are calculated model bounds, **not measured actual button-sampling intervals**.

Thus original OLED stalls can cause a tap/press to arrive and depart between Core0 samples, explaining **possible missed SFII inputs** and delayed recognition. But OLED blocking by itself does **NOT** create an unsolicited jump, nor does it explain precisely three rapid LP punches when a held input is already published. Treat those separately; do not falsely combine into one root cause.

Candidate B changes ONLY the SSD1306/SH1106 draw routine under XGO input mode: writes **ONE 8-row page per invocation**, cycles 8 pages across updates, leaves every other input mode's full-frame drawing behavior unchanged. Actual extracted C++ driver mock tested **24 SSD1306 pages and 16 SH1106 pages** in sequence; full ARM binary audit and exact critical-code comparison succeeded. See:
- `findings/OLED-PAGE-LATENCY-AND-CONTRA-JUMP-2026-10-24.md`;
- `tests/test_xgo_oled_page_cpp.py`;
- `candidates/offline-transparent-page-oled/tiny_ssd1306.cpp`;
- `.github/workflows/gp2040ce-xgo-paged-oled-build.yml`.

**Next sensible experiment if user chooses:** one brief hardware session on candidate B to observe input responsiveness and whether missed SFII LP improves, while separately logging ghost Contra JUMP. Do not confuse prospective reduction in missed taps with proven fix of spontaneous jump.

## 6. CONTRA GHOST JUMP — VERIFIED EVIDENCE VS OPEN CAUSE

**HW evidence:**
1. P0 passive loose-wire probe: DATA LOW ~7.8µs, first CLOCK falling ~1.2µs after release. When a measurement/probe load was attached to GREEN/DATA, P2 **unexpected jumps were reproducible**; without connection, reference DATA HIGH across subsequent pulses. Measurement topology is NOT current Frankie cable.
2. P3 passive RP2040 USB-PHY probe: intermittent P2 jumps even with RP2040 TX DATA output-enable disabled, **no active bit serializer**. The passive source initializes the same ten PHY-direct override flags as current active source, but P3 used a different (ordinary) cable.
3. In Test49 with RIGHT+rapid FIRE, unsolicited jumps and PAUSE were observed, processed R/P0 counters remained zero; diagnostic counters are processed edges and **NOT host-received bits**. Synthetic models permit slot/clock misalignment but are not waveform measurements.
4. The *new transparent firmware* is HW-positive for correct physical button hold/tap semantics yet **still ghosts JUMP in Contra**. Eliminating the old flash/spinlock/SPSC queue hazard and eliminating attack pulses was not sufficient to eliminate ghost jumping.

**BIN evidence from exact original XGO scanner:** first P2 slot R0 sampled before first clock (see scanner addresses above), very near host release of DATA after LOAD LOW. In response, controller releases DATA to Hi-Z, not actively high. This makes transient LOW/slow pullup recovery a **credible hypothesis**, not a confirmed electrical cause in the current cable.

**Possible causes (do not promote INF to HW):**
- False LOW on slot0 due to load-release / pullup / PHY/cable electrical settling; no connected-Frankie analog rise-time capture exists.
- Other serial bit corruption or missed CLOCK phase: X/slot2 and A/slot4 also map to NES jump by embedded default. A simple monotonic slow-rising DATA-low tail that reaches X2 would also contaminate prior R0 and Y1; an isolated false X2 needs different mechanism. Synthetic virtual-host examples are models only.
- RP2040 upstream physical input processing/mapping versus host sampling timing; existing diag screens aren't exact host bit captures.
- XGO per-ROM keymap mapping that differs from embedded defaults; exact user's ROM-specific `.kmp` not verified.
- Final 12-bit postamble phase detection could cause missed *next* scans but does not by itself explain a false jump.

**DO NOT** propose speculative USB-DP active HIGH, pullups, resistor changes, wire modifications, button masking, new turbo, or BIOS patches as established remedy. Each either violates controller transparency or lacks necessary electrical timing evidence.

See `findings/2026-10-24-CONTRA-JUMP-CAUSAL-DISCRIMINATORS.md` and `findings/OLED-PAGE-LATENCY-AND-CONTRA-JUMP-2026-10-24.md`.

## 7. STREET FIGHTER II INPUT ANOMALIES — OPEN DISCRIMINATORS

**Reported only:** one held LP produced three quick punches; a later held LP produced no action. Note LP semantics might be implemented by XGO/emulator/core, not by GP2040-CE.

Possible contributors to investigate **offline in this order**:
1. Core0 missed actual button onset due full blocking OLED I2C; candidate B targets this without changing the controller transport. This may address missed LP but not establish cause of rapid triple punching.
2. Host serial frame never completed or late synchronization led to a missed/shifted physical button bit. Existing transparent tests pass under modeled nominal CLOCK; actual connected timing still unmeasured.
3. The game's own input repeat/animation behavior for a held button, or controller keymap override. Do not call three punches three firmware-generated edges without capture.
4. Distinguish transient physical GPIO debounce/add-on processing from downstream host reading. Do not infer any user's button hardware defect without evidence.

No new diagnostics OLED or hardware instrumentation has been approved. The actual XGO mapping must be left untouched.

## 8. KNOWN FAILED APPROACHES / DO NOT REGRESS

- **Legacy Test44:** physical button press artificially transmitted for ~18ms then released even if held; violates user contract. Still preserve as historical emergency recovery.
- **Initial SPSC coherent trial:** removed flash-backed atomic helper calls under masked IRQ, but still truncated attack holds; user's Contra jump persisted.
- **XY-only held “turbo” patch:** made X/Y held and R/L/A/B pulses, wrongly implying GP2040 should interpret XGO mapping. Violated physical transparency. No return.
- Decreasing transition timeout to 6µs/4µs failed nominal virtual host tests. Arbitrary strict CLOCK high guard Test35 caused choppy controls/missed attacks.
- Prior Test30 next-slot predrive/phase tweaks and Test33 independent pulses caused regressions/mixed inputs.
- A genuine RP2040 spinlock-13 flash-backed atomic helper hazard was found in Test49 and removed by transparent implementation; do not reintroduce it.
- Multiple diagnostic OLED builds cluttered display and were abandoned; user explicitly requested original normal controller diagram and bottom input history.
- Test49 timeout counter S12 did **not** uniquely correlate to host false START in simulated scenarios; don't equate S12 with ghost PAUSE.
- **Do not repeatedly flash new candidates** without source + C++ host simulations + linked ELF review, and keep user's rollback.

## 9. CURRENT EXACT STOPPING POINT / NEXT ENGINEERING TASK

User requested a **DETAILED GITHUB HANDOFF TO A NEW CHAT** immediately after beginning further review of scanner and clock/bit fault evidence. At this checkpoint:

- NO new modification to the actual transparent driver `XGODriver.cpp` after the tested positive release.
- NO new modification to the known-good OLED normal screen.
- The OLED page-only candidate B is **compiled, source-pinned, tested offline and ready**, but remains **unflashed**.
- A detailed investigation report already exists and has been updated with verified full build results.
- The **primary unresolved question** is how to eliminate unintended Contra JUMP and intermittent SFII LP behavior without breaking accurate physical holds/releases.
- This handoff documentation itself does not authorize changing XGO firmware or Frankie wiring or requesting additional hardware.

**Next chat execution plan:**
1. Read this handoff and `HANDOFF-CURRENT.md` **newest sections only**, then the transparency contract and the paged-OLED findings. Verify branch head and CI runs rather than inferring status from older “pending” sections.
2. Preserve currently good transparent hardware UF2 **A** (SHA `94ea...b84`). Treat paged OLED **B** (SHA `5dcc...5b`) as a separate unflashed test with source diff limited to OLED drawing.
3. Focus **offline** on XGO slot0 / DATA release analog-vs-digital implications, actual MIPS scanner sample timing, and GP2040 Core0 input scheduling. Do not assume OLED page change fixes ghost jumps.
4. Decide whether to request ONE short, explicit candidate-B hardware test for missed SFII presses. If testing, measure only user-observable behaviors: held LP, short LP, quick button taps, normal OLED display and Contra unexpected JUMP; separately report positive/negative. Keep A for rollback.
5. For any future serial fix, write falsifiable causal prediction and a new **offline-only candidate**; run direct-source 4096-mask/hold tests, independent CLOCK phase/fault model, linked ARM SRAM/IRQ audit and pinned CI before offering a UF2. Avoid speculative timing tuning.
6. Document final accepted HW observations, NOT presumed fixes, and update this handoff.

## 10. TOOL WORKFLOW / WHERE TO FIND EVERYTHING

Use GitHub connector tools in `functions.exec` on `tools.mcp__GitHub__*`. Fetch repository content with:
```js
await tools.mcp__GitHub__fetch_file({
  repository_full_name: "jeborgesm/xgo-a10-research",
  ref: "research-gp2040ce-xgo-integration",
  path: "integrations/gp2040ce-xgo-test01/HANDOFF-CURRENT.md"
})
```
Use `fetch({url:"https://api.github.com/repos/jeborgesm/xgo-a10-research/branches/research-gp2040ce-xgo-integration"})` for current HEAD. For edits: `create_blob`, `create_tree`, `create_commit`, `update_ref` with `expected_sha` lease; check actual new branch ref and use meaningful commits. Never rewrite historical protected test folders.

Canonical paths:
- `integrations/gp2040ce-xgo-test01/HANDOFF-CURRENT.md`
- `integrations/gp2040ce-xgo-test01/CONTROLLER-TRANSPARENCY-CONTRACT.md`
- `integrations/gp2040ce-xgo-test01/candidates/offline-test44-transparent-controller/{XGODriver.cpp,ButtonLayoutScreen.cpp}`
- `integrations/gp2040ce-xgo-test01/candidates/offline-transparent-page-oled/tiny_ssd1306.cpp`
- `integrations/gp2040ce-xgo-test01/findings/OLED-PAGE-LATENCY-AND-CONTRA-JUMP-2026-10-24.md`
- `integrations/gp2040ce-xgo-test01/findings/2026-10-24-CONTRA-JUMP-CAUSAL-DISCRIMINATORS.md`
- `integrations/gp2040ce-xgo-test01/tests/test_transparent_controller_end_to_end.py`
- `integrations/gp2040ce-xgo-test01/tests/test_xgo_oled_page_cpp.py`
- `integrations/gp2040ce-xgo-test01/tests/test_controller_transparency_contract.py`
- `.github/workflows/gp2040ce-xgo-paged-oled-build.yml`
- `.github/workflows/gp2040ce-xgo-transparent-controller-build.yml`
- `experiments/rp2040-passive-probe-p0.md`, `experiments/rp2040-usbphy-p3-passive.md`
- `tools/rp2040-xgo-p3-usbphy/main.c` (passive PHY source)
- `findings/embedded-default-keymap-patch-points.md`, `findings/keymap-runtime-behavior.md`

Remember the user's workflow expectation: **do real engineering, not multi-paragraph promises**; verify sources and CI, communicate precise success/failure, do not prematurely declare root cause. The whole project is XGO first, RP2040 physical-controller transport, not generic USB gamepad design.

## 11. EXACT NEXT-CHAT RESUMPTION MESSAGE

> Resume XGO Archeology from branch `research-gp2040ce-xgo-integration` in `jeborgesm/xgo-a10-research`. Read `integrations/gp2040ce-xgo-test01/HANDOFF-2026-10-24-TRANSPARENT-BASELINE-AND-INPUT-FAULTS.md` completely, then the CURRENT newest addenda in `HANDOFF-CURRENT.md` and the immutable `CONTROLLER-TRANSPARENCY-CONTRACT.md`. Do not restart archaeology. The **user-tested transparent controller** UF2 SHA `94ea7228c774a67e8252e7e09d94938530e5d74572d985332e6840ae09fe8b84` is the protected GOOD hardware baseline: button holds/taps work, SFII playable (Dhalsim defeated), Contra playable with/without native X/Y turbo. Remaining HW faults: spontaneous Contra JUMP; intermittent LP no-response and one held LP producing three rapid punches. An **OLED-page-only source correction** targets Core0's synchronous full-frame I2C input-scan stalls; its **full ARM build 40107598214 passed**, UF2 SHA `5dcc28132ca54293a3d27dc2a452269bc47a1e7f141bd49c2c7e296918071b5b` is packaged and NOT HARDWARE TESTED. Preserve the tested UF2; do not change serial controller semantics, XGO firmware, Frankie, or normal OLED UI. Continue offline investigation into slot0 DATA-high recovery, host MIPS scanner timing, clock/frame reliability and input polling; distinguish evidenced facts from hypotheses. Only propose a narrowly justified next trial or correction with source/host-C++/linked ARM evidence, and update the handoff.

## 12. POST-HANDOFF OFFLINE RESULT — P1-DEPENDENT P2 FIRST-BIT SAMPLING (2026-10-24)

After restoring context in the new chat, reexamined the **actual original 12,768,452-byte XGO `bios/bisrv.asd`** with the known SHA `869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf`. New **BIN** distinction: the P1 B15 first-bit read at `0x8035D870` is followed by an active-low conditional `bne` at `0x8035D878`. When P1 is HIGH/released, the host takes a short path to the P2 L0 read at `0x8035D890`; when P1 is LOW/pressed it executes **four additional instructions**, including a state load/store, before that P2 read. Both first-bit reads occur **before** the first shared CLOCK-low write at `0x8035D8BC`. Branch-delay behavior and binary words were checked with a hash-asserting standard-library Python verifier.

Evidence: [host-path finding](findings/2026-10-24-xgo-p1-dependent-p2-slot0-sampling.md) and [read-only verifier](tests/verify_original_xgo_slot0_p1_path.py). This is a falsifiable **instruction-path timing discriminator**, not a measured sample-time difference or proven Contra JUMP cause. The P1-idle fast route might expose a slowly releasing P2 DATA line to an earlier sample, but **analog rise-time, CPU cycles, current cable and mapped ghost-jump bit remain OPEN**. Do not change PHY, cabling, original XGO firmware or protected transparent driver based on this alone; continue bounded offline models and targeted source analysis. No new hardware test requested.

The tested transparent A `94ea7228…fe8b84` remains protected. The paged OLED B `5dcc2813…071b5b` remains **unflashed**, with its completed CI status unchanged.

## 13. POST-HANDOFF TWO-SAMPLER FAULT-CLASSIFICATION CLOSURE (2026-10-24)

Detailed [two-clock reliability report](findings/2026-10-24-two-clock-controller-reliability-closure.md) and [deterministic phase-grid source model](tests/test_xgo_sampling_and_slot0_discriminators.py) add a scope limit to the existing paged-OLED fix. The transparent controller has TWO asynchronous sampling boundaries: Core0 physical input publication and XGO host's approximately 16.03ms LOAD cadence. Full SSD1306 OLED 1025-byte/400kHz data transfer takes nominally 23.063ms; page-only 129-byte transfer 2.903ms. In a 40×40 synthetic independent-phase grid, a modeled 12ms physical tap was observed at a host poll in 840/1600 full-frame phases versus 1204/1600 paged-OLED phases. **These are synthetic phase-grid coverage figures, not measured miss rates**; the model assumes an optimistic Core0 period equal only to I2C data transfer duration. Paged OLED removes a source-demonstrated long blocking transfer but does NOT guarantee all brief taps reach the independent 16ms XGO host. A sustained 250ms held bit is eventually recognized in both no-fault model variants. Neither physical-input sampling model can invent a spontaneous JUMP. A separate synthetic P1-dependent slot0 settling-tail discriminator captures potential false R only under explicitly invented submicrosecond assumptions; it is NOT an analog observation.

**Implication for next candidate:** Preserve hardware-positive transparent A (`94ea7228…fe8b84`). The existing OLED-page-only B (`5dcc2813…071b5b`) remains the single narrow compiled candidate and STILL UNFLASHED; do not claim it fixes ghost JUMP or every SFII LP behavior. No new serial physical firmware correction is justified without a discriminating waveform or host-received bitword during a fault. Continue read-only analysis; any later hardware trial should be one bounded B-versus-A comparison with rollback, not a blind progression of rewrites.
