# OCT 28 2026 — POLISH02 BUILT AND PACKAGED WITH TWO ROLLBACKS; HARDWARE TEST PENDING

**Full linked ARM build SUCCESS**: [Actions #40696044674](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40696044674); [fast exact-C++ 24 case suite SUCCESS #40695772983](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40695772983). [Final technical evidence and firmware hashes](integrations/gp2040ce-xgo-test01/findings/2026-10-28-POLISH02-CLOCK-48US-SOURCE-AND-SYNTHETIC-RESULT.md). Separate source `candidates/offline-polish02-clock-tolerance/XGODriver.cpp` Git blob `eff10e585ee46805801c3d218d5d8412630dd650`, changes **only CLOCK waits from 18→48us**, keeping DATA release at 18us, exact transparent twelve physical held bits, signal drive and PHY config unchanged. Combined with already HW-tested paged OLED UI, source `e441ecc441a1d495413fbd56171a9a72e7321883`. Real Cortex-M0+ UF2 2,515,968 bytes **SHA256 `699e46f1e157510e6fda03534700ba80824966bf74663c87c6457396986bce72`**, ARM linked `emit_frame()` in SRAM and no-XIP IRQ hotpath PASS, GitHub artifact ID 12819837151. Second linked ELF artifact ID 12820245338.

**Conversation download ZIP prepared and checksum-verified** at `/mnt/data/XGO-Controller-Polish-02-Clock-Tolerance-With-Rollback.zip`, SHA256 `f70e2c5733a80445e209a21c8a23bd1cd423a2c841ab53ddc578039f92239f4e`, contents 01 Polish02 test UF2, 02 current owner HW-positive Polish01 paged-OLED rollback UF2 SHA `5dcc28132ca54293a3d27dc2a452269bc47a1e7f141bd49c2c7e296918071b5b`, 03 older HW-tested A rollback UF2 SHA `94ea7228c774a67e8252e7e09d94938530e5d74572d985332e6840ae09fe8b84`, README and manifests. This is a **new genuine firmware revision**, not a diagnostic-only image. But no Polish02 on-device pass yet. The tests model hypothetical 25us host CLOCK stretches; actual XGO IRQ timing unmeasured. Do NOT claim this has fixed idle spontaneous jumps or held rifle repetitions until user sees it. Original user statement: Contra **starting rifle single-shot** repeats when B is held = BUG, not Machine Gun autofire; user sees idle P2 ghosts too. Retain current Polish01 until voluntary trial, rollback immediately if inputs worsen. No GOLD `bisrv.asd`, Frankie, power, pads, ROM, pinmux or USB pull-up changed.

---

# OCT 28 2026 — POLISH02 CLOCK-ONLY 48us CANDIDATE PASSES EXACT-C++ STRETCH REGRESSION

[Polish02 detailed source, model and preservation report](integrations/gp2040ce-xgo-test01/findings/2026-10-28-POLISH02-CLOCK-48US-SOURCE-AND-SYNTHETIC-RESULT.md). User Polish01 paged OLED remains current hardware-tested firmware: long Street Fighter II gameplay showed no missed inputs; SFII held LP/MP occasional repetitions; Contra still has spontaneous idle P2 JUMP plus **held A repeated JUMP and held B repeated SHOTS on the game's INITIAL SINGLE-SHOT RIFLE** (owner corrected prior mistaken Machine Gun excuse; this IS abnormal, do not dismiss it). Original hardware-connected-vs-disconnected-vs-reconnected ghost isolation still applies to predecessor transparent A, not necessarily live Polish01 waveform. The user wants final polish, not re-diagnosing ROMs, adding resistors, remapping buttons, or repeatedly inspecting gameplay.

**A real but modest CODE CHANGE has been made OFFLINE**: `candidates/offline-polish02-clock-tolerance/XGODriver.cpp` Git blob `eff10e585ee46805801c3d218d5d8412630dd650`, changes only host CLOCK timeout from 18 to 48us at four wait_clock sites; initial DATA `wait_data(true,EDGE_TIMEOUT_US)` remains **18us**, and all 12 physical hold semantics, DATA low-sink/Hi-Z, USB PHY overrides and early slot0 preserved. [Fast C++ CI run #40695772983 SUCCESS](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40695772983). New `tests/test_polish02_clock_tolerance_cpp.py` source-token guard and 24 extracted C++ cases show original 18us fails 23/23 synthetic 25us stretched LOW/HIGH events, Polish02 succeeds 23/23 and subsequent clean frame. This is conditional MODEL of host IRQ pauses, **NOT measured real clock or proof it fixes phantom idle inputs or repeated rifle shots on hardware**.

Full Cortex-M0+ linked build workflow `.github/workflows/gp2040ce-xgo-polish02-build.yml` [Actions #40696044674](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40696044674) was **running when this checkpoint was recorded**; check completion, exact UF2 artifact/provenance and linked SRAM audit before offering a new flash. Build layers Polish02 driver onto **current HW-accepted paged OLED** `tiny_ssd1306.cpp` blob `e441ecc441a1d495413fbd56171a9a72e7321883`. Preserve user-installed Polish01 UF2 SHA256 `5dcc28132ca54293a3d27dc2a452269bc47a1e7f141bd49c2c7e296918071b5b`, original approved A rollback `94ea7228c774a67e8252e7e09d94938530e5d74572d985332e6840ae09fe8b84`, XGO GOLD BIOS `75f858b6d9a1eb81235ae9e9c9b449a6a3052ad4365e5411b8ce041075e99d6b`, unusual Frankie V2 Jr bridge. No user HW test on Polish02 yet. **Ghost inputs remain OPEN**.

---

# LATEST POLISH01 HARDWARE FOLLOW-UP — CONTRA GHOST JUMPS PERSIST; HELD A/B ACTIONS CAN REPEAT (2026-10-26)

[New exact HW witness and root-cause boundaries](integrations/gp2040ce-xgo-test01/findings/2026-10-26-HW-POLISH01-CONTRA-GHOST-AND-HELD-AB-FOLLOWUP.md). Owner installed paged-OLED Polish 01 and reported earlier extended SFII play with no missed presses noticed and slight sporadic held LP/MP repetitions. **NEW owner hardware report on same installed Polish 01: "contra still has the ghost jumps and when I hold a or b i get repeated jumps or repeated shots... there should be only one and no repeats when hold".** Thus Polish 01 is **HW-POSITIVE for improved scan responsiveness** but **HW-NEGATIVE for resolving idle P2 ghost jump**. **DO NOT mark ghost fixed** or call controller perfect. A/B held causes repeated *game actions*, but this is not yet proof that serial data emits repeated press *edges*: transparent GP2040 source intentionally holds true physical level across all XGO scans. In stock NES Contra some equipped weapons intentionally fire repeatedly when holding B. Whether held A causes normal repeat-jump in actual game context unknown; don't overgeneralize. **Never “fix” by translating physical holds to artificial one-shot pulses**: this would break other games and native XGO turbo semantics. Ghost inputs when no button is touched are unquestionably wrong and continue to be priority. Do NOT shift effort to game ROM/keymap; only use game as witness. Separate known line/PHY electrical interaction and CLK stability from potential display blocking; paged OLED source preserves 12-bit responder unchanged. No new firmware produced by this checkpoint. Protect paged OLED current-installed build, prior transparent A UF2 rollback, XGO GOLD, Frankie special pad bridge. Owner wanted final polish, not repeated diagnostic builds.

---

# NEW USER HARDWARE SUCCESS 2026-10-26 — POLISH 01 PAGED OLED PLAYABLE; NO MISSED INPUTS NOTICED

**[HW] NEW USER REPORT, highest-priority current firmware status:** [Precise witness and artifact provenance](integrations/gp2040ce-xgo-test01/findings/2026-10-26-HW-PAGED-OLED-POLISH01-PLAYABLE-NO-MISSED-INPUTS.md). The user **flashed the distributed Polish 01 paged-OLED firmware** and reported: "the new firmware works, I don't see any missed inputs. If I hold the lp or mp buttons i get some sporadic repetitions. notning major. Beated all opponents until the bonus car adn broke it with 3 secs to spare". **Hardware positive for display-scanning/input-responsiveness polish**, longer Street Fighter II gameplay passed, no missed presses noticed. LP/MP held occasional repetitions **remain minor**; do not fabricate cross-button substitution, counts or claim that game-native repeats are definitely malformed. **No P2 spontaneous ghost observation on THIS Polish 01 run was supplied**: ghost-input closure remains OPEN and preceding connected/disconnected/reconnected test applies to prior transparent A. **DO NOT conflate Polished responsiveness with phantom-input fix**.

Previously build-tested paged OLED UF2 SHA256 `5dcc28132ca54293a3d27dc2a452269bc47a1e7f141bd49c2c7e296918071b5b`, distribution `XGO-Controller-Polish-01-Paged-OLED-With-Rollback.zip`; protected original transparent A rollback UF2 `94ea7228c774a67e8252e7e09d94938530e5d74572d985332e6840ae09fe8b84`, driver source blob `cccb985a05baa8bb9078b6e336eb5f991c1a7a8f`, original GOLD host SHA `75f858b6d9a1eb81235ae9e9c9b449a6a3052ad4365e5411b8ce041075e99d6b`. Polish 01 is now user-HW-POSITIVE initial trial, do not keep saying "unflashed" or "hardware-unverified" as current status; archived pre-trial names remain immutable. **Keep this working installed firmware and rollback, avoid regressing responsiveness in pursuit of rare ghost/repeat polish.** No new firmware or hardware modifications created by this recording.

---

# LATEST OWNER HARDWARE RESULT — GHOST P2 INPUT DEPENDS ON FRANKIE/RP2040 CONNECTION (2026-10-26)

**HIGH-VALUE [HW] RESULT, ALREADY EXECUTED:** [Original exact owner report and revised controller fault tree](integrations/gp2040ce-xgo-test01/findings/2026-10-26-HW-HANDLE-CONNECTION-A-B-A-GHOST-DEPENDENCY.md); [prior A–B–A proposal now CLOSED](integrations/gp2040ce-xgo-test01/findings/2026-10-26-HANDLE-CONNECTION-PRESENCE-NO-FLASH-DISCRIMINATOR.md). Following the already established protected GOLD Handle=P2/two-player/physically idle GP2040 setup, user reported (1) **CONNECTED** Frankie+RP: spontaneous P2 actions; (2) **DISCONNECTED** from XGO Handle: NO spontaneous P2 actions observed; (3) **RECONNECTED** original assembly: spontaneous P2 inputs returned. **This is the strongest real hardware isolation to date:** under these sessions, ghost depends on the external connection. Exact ghost count/rate, whether P2 still enabled/displayed disconnected, host decoded bits, analog voltage UNKNOWN. Do NOT falsely declare DATA pullup defective or GP2040 transmitter guilty. Earlier native-R held/released A-B-A was **NEGATIVE** and is also CLOSED.

**NEXT ENGINEERING GATE:** separate passive wired PHY/Frankie load from *active* DATA TX. Offline prepare and source/link-audit a **single-variable, separate revertible RP2040 diagnostic UF2** keeping SAME Frankie cable and same USB PHY RX init/scheduler but NEVER enables DP TX OE at all; compare idle ghost P2 to protected transparent A. Do NOT flash before independent guards and owner's agreement to this temporary nonplaying diagnostic. Historical P3 receive-only on an **ordinary cable** did ghost, but current Frankie electrical equivalence NOT demonstrated. If no TX still ghosts => passive connection likely; if no TX stops ghosts => physical Core0 input / unintended output / slot timing warrant closer focus, not instant repair. DO NOT use Strong USB DP pullup, DM pullup (HW freeze), active HIGH, XGO BIOS edits, game/ROM keymaps, extra probes, Frankie connector changes, or arbitrary filters. The protected GP2040 A source blob `cccb985a05baa8bb9078b6e336eb5f991c1a7a8f`, flashed UF2 `94ea7228c774a67e8252e7e09d94938530e5d74572d985332e6840ae09fe8b84`, GOLD `75f858b6d9a1eb81235ae9e9c9b449a6a3052ad4365e5411b8ce041075e99d6b` remain unchanged, OLED B unflashed. **Controller reliability universally in every game** remains goal, not Contra-specific workaround.

---

# LATEST 2026-10-26 — EXACT XGO L0 STARTUP AND HC15XX GPIO BIAS GATE; NORMAL CONNECTOR A–B–A NEXT

**User objective remains UNIVERSAL GP2040-CE controller reliability (no ROM/keymap detour).** [Original XGO, HC15xx and RP bias electrical findings](integrations/gp2040ce-xgo-test01/findings/2026-10-26-HC15XX-STARTUP-PAD-BIAS-AND-RP-DP-ENGINEERING-GATE.md), [11-instruction SHA-pinned original XGO startup verifier](integrations/gp2040ce-xgo-test01/tests/verify_original_l0_startup_ownership.py) **original XGoAnalisis.zip MIPS words locally PASS**. During initial XGO controller task setup `0x8035DF2C..3C`, L0 direction bit0 is explicitly cleared, making Handle DATA INPUT; B15/native also INPUT. During each scan XGO temporarily drives L0 OUTPUT LOW then releases to INPUT before reading slot0. Original stock image alone does not prove XGO internal/external pull-up presence. External HC15xx HCRtos `bnister/sf2000_hcrtos` GPIO driver `gpio_configure` sets GPIO mode/dir and has no pull-up API; pinmux byte may have independent pad details unverified. **Controller RP2040 USB DP pull-up is forced OFF** and data_release Hi-Z; USB Rpu network is relatively strong (datasheet ~1.2k/2.3k), potentially draws mA while host asserts LOW. Do NOT blind-enable it. Analog electrical HIGH-return source/strength on bridged Frankie V2 Jr remains OPEN, not proven floating.

**Most discriminating safe next HW gate now identified**: [powered-down connector presence A1–B–A2](integrations/gp2040ce-xgo-test01/findings/2026-10-26-HANDLE-CONNECTION-PRESENCE-NO-FLASH-DISCRIMINATOR.md). Use known working GOLD Handle=P2 and any game with observable idle P2. A1 existing Frankie+Pico attached idle -> observe ghost; B power OFF, unplug only normal Handle external plug, power on identical two-player session idle P2 -> observe; A2 power OFF reconnect, rerun. NEVER hotplug, rewire physical pad2/4 bridge, or use new probe. If software hides P2 without pad or no ghost occurs in A1/A2, inconclusive. Ghost only connected suggests cable/PHY interaction; ghost even disconnected suggests XGO idle-side input or downstream path. Not executed by owner as of this checkpoint; no claim of fix. Prior owner's **native R HELD/RELEASED A-B-A was NEGATIVE** and must not be repeated as new idea.

Protected GOLD BIOS `75f858b6d9a1eb81235ae9e9c9b449a6a3052ad4365e5411b8ce041075e99d6b` and transparent A source blob `cccb985a05baa8bb9078b6e336eb5f991c1a7a8f` untouched. OLED paged B still unflashed, only targets missed tap scanning not idle ghost. No new UF2 or firmware edit.

---

# CURRENT 2026-10-26 TRANSPORT ELECTRICAL LEAD: DATA HIGH BIAS IS NOT DRIVEN BY RP2040

**Owner goal remains universal controller reliability, NOT ROM/keymaps.** [New exact BIN/SRC electrical contract](integrations/gp2040ce-xgo-test01/findings/2026-10-26-PHYSICAL-DATA-HIGH-BIAS-OWNERSHIP.md), [reproducible bias verifier](integrations/gp2040ce-xgo-test01/tests/verify_xgo_data_line_bias_contract.py), [GREEN fast CI #40380342382](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40380342382). On SHA-verified ORIGINAL stock `XGoAnalisis.zip/bios/bisrv.asd`, eleven exact MIPS opcodes independently checked locally: host GPIO **L0** is configured to OUTPUT, driven LOW during LOAD (`0xb8800054` output latch / `0xb8800058` direction); changed to INPUT at scanner `0x8035D864` and read at `0x8035D890` (`0xb8800050`) before first CLOCK. NO pull-up config is established by this scan. The actual user-approved GP2040 transparent A is single-ended DP=DATA, DM=CLOCK; `phy_direct=0` with **DP_PULLUP_EN_OVERRIDE_EN** explicitly ON -> RP2040 *DATA DP pull-up forced OFF*, and `data_release()` clears TX_DP_OE -> **Hi-Z**, not driven HIGH. `data_sink()` drives LOW only. Thus physical DATA HIGH after XGO releases its LOAD must be supplied by *XGO/internal/external/circuit bias not by RP DP pullup*. Prior P0 digital high after release proves some threshold was crossed in that older setup; actual strength/rise at GOLD XGO's sample under Frankie V2 Jr remains OPEN. **Do not falsely claim no pull-up exists.**

This is a more actionable electrical gap for **phantom idle presses** than the already HW-rejected native R four-instruction timing test. Earlier passive native PHY itself caused P2 ghost while transmit OFF, consistent but different cable. Historical forced DM_PULLUP override froze XGO; DM=CLOCK not DP=DATA, and neither register should be changed blindly. No DP pullup trial, no active-HIGH drive, no external resistor, no GOLD timing patch or Frankie rewire until measured voltage/sink capability. Separate paged OLED B built for Core0 dropped taps but UNFLASHED and not a phantom-input fix. Protect GOLD BIOS SHA `75f858b6d9a1eb81235ae9e9c9b449a6a3052ad4365e5411b8ce041075e99d6b`, GP2040 transparent A source blob `cccb985a05baa8bb9078b6e336eb5f991c1a7a8f`/UF2, and Frankie. Next: qualify true DATA voltage/bias and permitted low-impact repair, not game mapping, arbitrary masks or more synthetic clocks.

---

# CURRENT TOP PRIORITY — UNIVERSAL GP2040-CE WIRED CONTROLLER RELIABILITY (2026-10-26)

**BINDING USER CORRECTION:** "why are you checking the Contra Rom ??/ what we need is to make the controller work reliably." Contra is an observation fixture ONLY, not the work target. Do NOT pursue the ROM, keymap or FC/save .kmp as a gate. **Primary objective:** no ghost input while idle, no dropped/shifted input while held, exact physical press/release propagation, in any game and both GOLD P1/P2 routing modes. See [controller reliability scope and evidence](integrations/gp2040ce-xgo-test01/findings/2026-10-26-CONTROLLER-RELIABILITY-IS-THE-OBJECTIVE.md).

Actual latest HW negative native-R A-B-A still stands: owner observed P2 spontaneous jumps at about equal rates whether local R held or released, so deprioritize four-instruction external first-bit sample-window. Prior passive P3-with-TX-disabled spontaneous jumps support electrical coupling as a serious line-level cause, though cable differs from current Frankie. Separate clock synchronization/lost-held-bit question remains. Protected transparent A `emit_frame()` currently waits for external DATA HIGH on released slot0 *before* arming first CLOCK; test model shows this can lose first edge. But pure clock-first alternative does **not** repair a false host-read first bit. Prior models not live electrical proof. Resume at **PHY line bias/receive loading + XGO DATA turnaround + clock phase integrity**. No more game mapping detours, no random BIOS changes, no active HIGH, no DM pull-up override (HW froze XGO), no Frankie rewiring. Protect A/GOLD rollback baselines, OLED B unflashed. This checkpoint changes research priority, not firmware.

---

# LATEST 2026-10-26 — FC CONTRA P2 KEYMAP FORENSIC GATE, NEGATIVE A–B–A RETAINED

[New detailed BIN/SRC/HW report](integrations/gp2040ce-xgo-test01/findings/2026-10-26-CONTRA-P2-ACTIVE-KEYMAP-EVIDENCE-AND-FAULT-SOURCE-GATE.md), [read-only P1/P2 FC .kmp analyzer](tools/xgo-protocol-audit/audit_fc_keymap.py), [five regression tests](tools/xgo-protocol-audit/test_audit_fc_keymap.py), [GREEN CI #40334342549](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40334342549). The owner **already completed** native R RELEASED→HELD→RELEASED in GOLD Handle=P2 and saw spontaneous P2 Contra JUMP at about the SAME RATE all three phases. Demote the four-instruction native-R sample-window perturbation as practical lead. Do NOT suggest repeating it.

Read-only actual original stock `XGoAnalisis.zip/bios/bisrv.asd` SHA `869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf`, NES fallback at ASD offset `0x8ddd34` confirmed two P1/P2 6-word blocks `00010008 00010000 00010000 00000008 00000000 00010008` each. Thus physical R slot0, X slot2, A slot4 **ALL** trigger NES A/JUMP under embedded fallback, and visible ghost JUMP is NOT evidence for R0 specifically. FC `.kmp` has six independent face/shoulder records for each P1/P2; actual *active* Contra 48-byte `.kmp` is **NOT available in mounted current files** (no .kmp in XGoAnalisis.zip, transparent A, paged OLED B, or linked ELF audit). The new read-only analyzer identifies P2 jump/fire and logical START/SELECT targets from an EXACT real profile, or says UNKNOWN if it cannot verify the matching path. Logical START/SELECT IDs 3/2 can be targets of custom face/shoulder profiles even though physical START/SELECT serial bits are fixed; the user's older Test49 PAUSE is not automatically proof of raw START bit. Actual active per-ROM keymap and physical DATA/CLOCK root cause remain OPEN.

Protect XGO GOLD `bisrv.asd` and GP2040 transparent A `XGODriver.cpp`, current Frankie V2 Jr pads and unflashed paged OLED B; no candidate firmware, game mapping edits, new hardware trial or wire changes. Need actual selected ROM basename + existing matching FC/save .kmp if any, then reliable non-perturbing physical/host decoded word evidence for causal closure.

---

# LATEST HARDWARE RESULT (2026-10-25): NATIVE R A–B–A HAS NO OBSERVABLE EFFECT ON P2 GHOST JUMPS

**OWNER TEST EXECUTED — HW NEGATIVE.** [Complete witness record and updated fault tree](integrations/gp2040ce-xgo-test01/findings/2026-10-25-HW-NATIVE-R-ABA-NEGATIVE-CONTRA-P2-GHOST-JUMPS.md). The prior A–B–A proposed in [the gate note](integrations/gp2040ce-xgo-test01/findings/2026-10-25-NATIVE-R-HANDLE-P2-NO-FLASH-AB-GATE-AND-DMA-VERDICT.md) is **DONE**. User confirmed same spontaneous logical **P2** Contra jumping with **native R RELEASED → HELD → RELEASED**, GP2040 otherwise untouched per trial; **jumping at about the same rate in all phases**, without exact counts or timers. Thus original XGO BIN's *real* native-R LOW four-instruction extension before external L0/Handle R0 sample DOES NOT yield a meaningful observable change. **Demote marginal early R0 read branch as primary ghost cause.** The test DOES NOT exclude slower DATA line recovery/load persisting across both sample windows, later corrupted X/A bits, CLOCK phase errors or downstream .kmp mapping. Do not repeat native R A–B–A or present it as pending, do not patch GOLD firmware or alter Frankie/DMA/PHY. Logical Handle=P2 isolates current symptom from GOLD P1 raw OR merge.

CRUCIAL SOURCE CAUTION: embedded FC fallback has **three JUMP sources** R/slot0, X/slot2, A/slot4 (R/X turbo), so visual Contra Jump is NOT evidence false R bit. Active per-ROM P2 .kmp **NOT verified**. Current local archive check: `XGoAnalisis.zip` has 115 entries, no .kmp or Contra path; other mounted controller/ELF ZIPs also have none. Historical Test49 also recorded unsolicited PAUSE, not explained by R0 alone, but different diagnostic build/cable. Preserve XGO GOLD and transparent A protected binaries unchanged; paged OLED B remains unflashed. The remaining meaningful evidence is the *actual* active P2 Contra keymap, and live trustworthy DATA/CLOCK plus host decoded inputs; extra source timing models cannot establish real culprit.

---

# LATEST 2026-10-25 — SAFE NO-FLASH PHYSICAL DISCRIMINATOR: NATIVE R CONDITIONALLY CHANGES HANDLE P2 R SAMPLE

[Full new gate and DMA verdict](integrations/gp2040ce-xgo-test01/findings/2026-10-25-NATIVE-R-HANDLE-P2-NO-FLASH-AB-GATE-AND-DMA-VERDICT.md). Stock XGO original `XGoAnalisis.zip` hash and actual MIPS branch **reverified on local original**: native built-in R HIGH/released branches at `0x8035D878` skipping four instructions before external L0 R0 sample at `0x8035D890`; native R LOW/pressed executes those four, providing a conditional longer (unmeasured in real µs) sample interval. P1/P2 GOLD toggle routes AFTER physical scanner.

**Next concrete diagnostic, no firmware/test ZIP/extra probes:** set GOLD `Handle=P2`, use same 2-player Contra and keep GP2040 physically untouched. Observe P2 ghost Jump with native P1 R RELEASED (A), then HELD (B) while ignoring P1's intentional attacks, then RELEASED (A). Look for repeatable ghost P2 jump change across A-B-A. If jumps diminish only in B, this supports a source-timing-dependent external slot0 issue (DATA rise or first-CLOCK alignment), not a direct analog proof. Unchanged counts do not rule out PHY loading; four instructions may not suffice; no ghost events at all yields inconclusive comparison. No new user hardware observation exists yet, and no external lead/cable modifications are needed.

Investigation of internal RP2040 DMA self-capture as an alternative to external probing: Pico SDK supports DMA timer DREQ, wrap ring and native PHY physical RX register. But a 10MHz 32bit trace would cost **40MB/s PHY reads + 40MB/s SRAM writes = 80MB/s aggregate traffic**, potentially disturbing the protected seven-Thumb-instruction RP CLOCK polling timing; samples may be uneven under bus stalls and no XGO decoded-R signal exists. **NOT built or approved**; require interference/timestamp validity gate before any diagnostic UF2. Protected GP2040 transparent A / GOLD BIOS / Frankie V2 Jr unchanged, OLED B remains unflashed.

---

# LATEST — P0 DATA/CLOCK FRAME-LEVEL ANALYZER IMPLEMENTED AND VALIDATED (2026-10-24)

[New finding](integrations/gp2040ce-xgo-test01/findings/2026-10-24-P0-PER-FRAME-FORENSIC-DIAGNOSTIC.md), [analyzer](tools/rp2040-xgo-p0/analyze_frames.py), [four synthetic P0 capture tests](tools/rp2040-xgo-p0/test_analyze_frames.py), [GREEN existing fast XGO CI #40163021139](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40163021139). New analyzer decodes unchanged P0 `BEGIN XGO_P0` packed 10MHz CLOCK+DATA text captures per polling frame: number of real clock pulses, each LOW/HIGH length/min/max, >18us clock stretches, DATA host load and release-to-first-clock interval, and DATA edges. JSON/CSV exports; no new UF2 or firmware changes. CI regression passed two scans, missing pulse/truncated input, stretched clock HIGH/LOW and R0 ambiguous DATA scenario.

**Important limit:** external R/slot0 is sampled on XGO MIPS **before first CLOCK**, so no P0 digital GPIO capture by itself can prove what R bit the host read. Historical P0 pulse averages do not equal current Frankie analog timing. The old P0 breakout probe and bridged Frankie V2 Jr cable are distinct, and old probing itself induced P2 jumps. There is no complete original raw P0 capture in this repository. This closes trace-decoder tooling, **NOT** the live ghost-input root cause. Protected transparent controller A and GOLD firmware unchanged, paged OLED B not flashed. Actual nonperturbing DATA/CLOCK physical evidence still required to distinguish false-R electrical recovery from missed/stretched CLOCK; do not guess a firmware patch.

---

# LATEST — HARDWARE CLOCK HIGH ~1.36US VS LINKED RP2040 SEVEN-INSTRUCTION POLLING (2026-10-24)

[New HW/source/CI comparison](integrations/gp2040ce-xgo-test01/findings/2026-10-24-P0-CLOCK-HIGH-DUTY-CYCLE-AND-LINKED-RP-POLL-LATENCY.md). Original user P0 10MHz capture: 12 clock LOW widths total **33.1µs** in first FALL→final RISE **48.1µs**; eleven intervening HIGH phases total 15.0µs = **mean HIGH 1.364µs**, mean LOW 2.758µs, not the prior ideal model's 2us HIGH/2us LOW. HIGH mean is one old idle capture, no individual distribution nor current Frankie waveform; at least one HIGH <=1.364µs, but exact minimum OPEN.

Newly retrieved **actual protected GP2040 transparent A ARM linked disassembly**, original build Actions `40071967532`, artifact `12551597007`, SHA256 `482031f65ae7d58f50174d6c4842a83794a9b216c0eb9845bca8dcb734b0564d`. `emit_frame` executes in SRAM at `0x200000f0`, both CLOCK wait loops are **seven Thumb instructions each** (timer MMIO 0x40054028; native USB PHY MMIO 0x5011007c; compare 18us), IRQs PRIMASK-masked across scan. Linked disassembly check passed locally; real execution polling interval remains UNKNOWN.

[Actual-C++ synthetic P0-average duty comparison](integrations/gp2040ce-xgo-test01/tests/test_p0_measured_short_clock_high_exact_cpp.py), [GREEN CI #40161383012](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40161383012): old uniform 2/2us and new P0-aggregate 2.758/1.364us clock both send 78 modeled phase/mask cases perfectly when timer/PHY read-call virtual step <=0.5us, both fail in some cases at synthetic >=0.7us steps. NO actual RP observation speed measurement and no evidence short HIGH alone caused real ghost inputs. Primary real phantom JUMP evidence remains passive P3 receive-only and GREEN probe loading => possible slot0 DATA false read even without transmit; separate CLK/held bit cause OPEN. Protect user-tested transparent A, XGO GOLD, Frankie V2 Jr, unflashed OLED B. No new user HW test or firmware candidate.

---

# LATEST 2026-10-24 ORIGINAL XGO SCANNER IRQ WINDOWS — HOST CLOCK STRETCH CAN TIME OUT GP2040

[New pinned investigation](integrations/gp2040ce-xgo-test01/findings/2026-10-24-XGO-IRQ-GATED-SCANNER-AND-HOST-CLOCK-STRETCH-MODEL.md). Read-only [original MIPS IRQ-window verifier](integrations/gp2040ce-xgo-test01/tests/verify_xgo_irq_windows_original_bin.py) **PASS locally on SHA-verified user's stock XGoAnalisis.zip**: 30 IRQ-disable plus 30 IRQ-enable helper calls in XGO physical dual-stream scanner, which touch MIPS CP0 Status IE via helpers and nesting counter. External physical L0 DATA release `0x8035D864` is immediately followed by IRQ re-enable helper `0x8035D868` *before* native/Handle R sampling; independent branch on native R released/pressed controls four-instruction Handle sample latency. Each nominal 2us host CLOCK-low interval also has IRQ-enable helper after asserting LOW and disable before HIGH. **Conditional inference:** real XGO CPU IRQ could stretch LOW/HIGH > RP2040's 18us wait even if all 12 host pulses are emitted. IRQ incidence/duration on actual XGO unknown; not evidence ghost Jump is host IRQ-driven.

[24-case source-extracted original RP2040 C++ clock-stretch regression](integrations/gp2040ce-xgo-test01/tests/test_xgo_irq_stretched_clock_exact_cpp.py), [GREEN CI #40160377104](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40160377104): 25 virtual µs stretched LOW pulses #1–11 cause CLOCK HIGH-wait error at respective slot, final #12 high failure does not increment protected A CLK counter; stretched HIGH gaps after pulses #1–11 cause CLOCK LOW-wait errors at following slots 2..12. Contrast earlier whole missed RP-observed clock → S12 timeout. All clean following scans recover A in virtual model. Historical Test48/49 OLED LO/HI/S12 counters do not identify which cause occurred; first-bit electrical false-R remains OPEN as separate/possibly concurrent mechanism. **No firmware candidate, original XGO GOLD, transparent A or Frankie cable changes; paged-OLED B remains unflashed**. Continue source-only investigation; do not alter XGO interrupt handlers or blindly widen 18us timeout without real timing.

---

# LATEST XGO GHOST INPUT: P1-R DEPENDENT P2-R WINDOW + PASSIVE PHY GHOST (2026-10-24)

[Full BIN+SRC+HW evidence](integrations/gp2040ce-xgo-test01/findings/2026-10-24-USBPHY-PASSIVE-GHOST-AND-P1-CONDITIONED-P2-R-WINDOW.md). Original XGO image `XGoAnalisis.zip` HASH-verified and opcode-checker PASS: native B15 P1 R HIGH (button released) causes MIPS branch at `0x8035D878` to skip four instructions, thus external Handle P2 R/slot0 DATA is sampled **earlier** at `0x8035D890`. Native P1 R pressed/LOW executes four extra instructions and samples Handle later. Actual physical time/voltage and current false-R root remain OPEN. Separate source audit [GREEN CI #40153719664](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40153719664) confirmed same 10 USB-PHY override flags in receive-only passive P3 and protected transparent controller A. P3 had TX disabled and nevertheless produced unexpected P2 jumping with **ordinary cable**, so passive PHY loading can cause that older symptom independently of GPIO publication/serial output. DM-pullup override trial froze device; do not repeat. Original P0 DATA HIGH precedes first CLK falling by only 0.9–1.3us [HW], while original XGO samples R before first CLK. **Frankie V2 Jr working cable bridges physical Micro-B pad positions 2 and 4 via WHITE**, unlike P3 ordinary cable; not equivalent analog loading, not proven standard USB pin roles. Keep protected GP2040 transparent A, XGO GOLD and physical Frankie wiring unchanged; OLED B remains unflashed; no new hardware test requested. Continue investigating first-bit electrical read error distinct from held-input clock phase loss.

---

# LATEST INVESTIGATION — EXACT GP2040 SOURCE: MISSED CLOCK #1..11 ALWAYS REPORTS SLOT12 (2026-10-24)

[Full exact source-based two-frame recovery findings](integrations/gp2040ce-xgo-test01/findings/2026-10-24-TWO-FRAME-RECOVERY-AND-SLOT12-ERROR-AMBIGUITY.md), [reproducible CI test](integrations/gp2040ce-xgo-test01/tests/test_exact_xgo_rearm_two_frames.py), [GREEN Actions #40129993336](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40129993336). Full protected GP2040 transparent `emit_frame()` C++ compiled with simulated XGO host 12 CLOCK pulses and 16.03ms frame interval, source immutable. With physical A HELD, missing RP reception of *any* single host CLOCK #1–11 leads to responder S12 clock timeout; host receives **B** instead of A for missed #1–4; **A+B** for #5; still correctly A for #6–11. **All recover correctly on next frame** under clean synthetic DATA gap. Final CLOCK HIGH missing returns failed status and rearm with host A correct, but **protected source increments no CLOCK timeout** (historical Test48/49 counted it); next frame recovers. Thus S12 in old OLED cumulative screenshots is NOT a location of actual lost clock, nor proof of a wrong decoded host button, and one timeout does not itself prove sustained second-scale input loss. This model did NOT reproduce ghost Jump, which remains a distinct R0 false-read hypothesis (prior exact-C++ test). Do not revive previously HW-rejected Test35 strict clock-phase guard, change XGO GOLD, flash a new controller UF2 or OLED B. Preserve user-tested transparent A and XGO GOLD. Continue LOAD resync / native RP2040 USB-PHY electrical audit offline.

---

# LATEST CI PASS — REAL GP2040 `emit_frame()` UNDER SYNTHETIC XGO CLOCK (2026-10-24)

[Full source-extracted chronological test report](integrations/gp2040ce-xgo-test01/findings/2026-10-24-EXACT-CPP-RESPONDER-CHRONOLOGICAL-HOST-DIFFERENTIAL.md), [source test](integrations/gp2040ce-xgo-test01/tests/test_exact_xgo_frame_phase.py), [GREEN CI #40129373359](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40129373359). Both protected `emit_frame()` and a TEMPORARY COMPILED hypothetical CLOCK-first policy PASS all **4096** ideal button masks. On simulated host delayed DATA rise and constant physical A held: ghost R can be host-decoded with **no CLK error** (`0x1080`); if current responder misses CLK #1, model host decodes `0x3040` (phantom R/Y, shifted A→B) and source records terminal S12 timeout. CLOCK-first alternate prevents modeled slot shift `0x3080`, but phantom R/Y **remain**, thus it is NOT a standalone ghost-input repair. Held R+A predrive correctly maintains slot phase in fake timeline but still receives false Y while host DATA remains LOW. Synthetic phase offsets are not physical Frankie measurements. Tested ONLY in hosted compiler/harness; **no GP2040 UF2 candidate or XGO GOLD firmware edit**. Retain earlier Test48/49 evidence as local timeout classes, not proof of current A root cause. Preserve protected A and XGO GOLD, OLED B unflashed. Future offline gate is LOAD false-trigger/clock alignment recovery analysis, with real DATA rise still OPEN.

---

# LATEST XGO GHOST INPUT INVESTIGATION — HOST HAS 12 CLOCKS, RP MAY MISS FIRST ONE (2026-10-24)

New read-only original XGO BIN verifier **PASS**: exact host MIPS scanner samples R0 before CLK, then emits all **12** shared-clock pulses (nominal 2us LOW), not 11. Protected transparent RP2040 code for R0 released waits `wait_data(HIGH,18us)` **before** arming `wait_clock(LOW)`; a synthetic late DATA rise after first clock RISE can make it miss FALL #1, transmit intended held A/slot4 at host slot5/B, falsely read early R/Y while host DATA remains low, and then timeout waiting for a 13th clock. Two distinct modeled outcomes: false R without any CLOCK error (when HIGH rises before missing #1), or false R/Y + shifted held A + slot12 terminal timeout when #1 missed. This is a falsifiable **MODEL**, **not measured current Frankie voltages or proof the current ghost arises from it**. CLOCK-first synchronization hypothetical prevents the modeled bit shift only if RP arms before first fall; does not repair false R/Y. No firmware candidate built/flashed or protected baseline changed.

[Detailed 2026-10-24 original-BIN + synthetic phase analysis](integrations/gp2040ce-xgo-test01/findings/2026-10-24-HOST-12-CLOCK-DATA-RECOVERY-AND-GHOST-INPUT-MECHANISM.md), plus 3 original BIN/model tests. Continue source-first reliability investigation without changing XGO GOLD, GP2040 transparent A or unflashed OLED B.

---

# XGO WIRELESS CAPABILITY CORRECTION — WIRED-ONLY XGO HANDLE (2026-10-24)

User explicitly confirms their XGO A10 **does not have wireless-controller capability**. Their SF900 wireless pads work with their **SF2000**, not XGO. XGO supports the proprietary **wired Micro-USB-shaped Handle Interface**, and the GP2040-CE reaches it using the decoded physical L0 DATA + B7 CLOCK channel before the XGO GOLD logical Handle=P1/P2 selector. All SF2000 wireless RF code and RF fingerprint matches in XGO firmware are inherited/software lineage only. Withdraw the previous suggestion to try SF900 pairing on XGO; do not spend effort testing for an XGO wireless radio or imply one could work. Comparison remains useful for common pressed-button representation and the separate SF2000/UniFrog wired settling-time clue. [Canonical correction](integrations/gp2040ce-xgo-test01/findings/2026-10-24-SF900-SF2000-KNOWN-GOOD-RF-VERSUS-XGO-HANDLE.md). No changes to protected XGO GOLD or controller transparent A, OLED B unflashed.

---

# NEW OFFLINE RESEARCH — SF900/SF2000 WIRELESS KNOWN-GOOD COMPARATOR (2026-10-24)

User owns SF900 controllers that work reliably with SF2000 and switch P1/P2. Completed focused comparative archaeology **without changing controller project goals**: archived original XGO `bisrv.asd` contains all five exact SF900/SF2000 XN297L channel/address/calibration fingerprints and receiver MIPS tests for 2-byte RF packets, ready=0x40 and pipe bit 0x02. Current UniFrog and a working third-party ESP32/XN297L SF900 receiver independently agree on same twelve pressed-button bitmap. RF receives complete packets with separate P1/P2 pipes; **XGO GP2040 Handle remains a different 12-clock physical wire protocol**. Current UniFrog's *replacement wired scanner* adds **4us DATA settle between host LOAD release and first R bit**, unlike original XGO's immediate R0 sampling; a specific plausible first-slot sensitivity clue, not a verified fix, not proof of the stock SF2000 timing. XGO physical radio population unproven, so no wireless compatibility HW claim. Read-only original BIN verifier and 4096 masks × 2 ports logical boundary MODEL passed. Neither protected XGO BIOS nor user-tested transparent GP2040 firmware modified; OLED page B still unflashed.

[Full comparison with pinned external sources](integrations/gp2040ce-xgo-test01/findings/2026-10-24-SF900-SF2000-KNOWN-GOOD-RF-VERSUS-XGO-HANDLE.md). Continue original first-slot phantom R vs held-button acquisition investigation; this is contextual evidence, NOT a change of direction.

---

# NEW DIAGNOSTIC EVIDENCE — RECONCILED TEST48/TEST49 OLED ERR COUNTERS (2026-10-24)

User recalls persistent errors on earlier diagnostic OLED firmware. Historical records confirm **Test48** final ERR628=CLK597+REL31, S12=421; **Test49 controlled run** CLK320 with S12=226, while uncommanded Contra JUMP and PAUSE were observed. In both, ~70.5% of CLOCK errors labeled S12, but **S12 covers terminal falling-edge or trailing high timeout after 12 bits were emitted** and does NOT prove wrong host bits. At least 304 Test48 and 165 Test49 terminal fall errors from LO/HI arithmetic; **nonterminal CLOCK classifications** Test48=176, Test49=94. These are local RP2040 wait timeouts, **NOT decoded frame error rate**. Current transparent A has no measured comparable rate and its final-high accounting differs. Historic transport sync faults are credible but precise cause for current spontaneous P2 JUMP/held A/B appearance OPEN.

[Diagnostic retrospective](integrations/gp2040ce-xgo-test01/findings/2026-10-24-OLED-ERROR-COUNTERS-RETROSPECTIVE.md). No firmware changed, XGO GOLD and GP2040 A protected, paged OLED B unflashed.

---

# NEW CONTRA P2 HW OBSERVATION — HELD A/B ACTIONS INTERMITTENT (2026-10-24)

User compared the external controller in **GOLD Handle=P2** versus P1: P2 feels worse, character **jumps randomly**, and holding physical **A or B** yields jumping/shooting actions **intermittently**, informally around **1–2 seconds apart**, rather than continuously responsive. Not a measured serial output period, not proof of repeated button edges, and not a fresh report of built-in P1 gameplay while in P2 mode. Earlier **Handle=P1**, built-in P1 play + untouched connected external also produced phantom jumps. Thus Handle-to-P1 merge is **not necessary** for observed P2 phantom JUMP; physical serial L0 still used in BOTH logical modes. GP2040 `emit_frame` source waits for DATA HIGH when R0 released before driving later A/B slots; slow/abnormal recovery could conditionally allow false first bit and lost/misphased later held bits, **MODEL/INF only**. Role-specific game mapping/port behavior remains OPEN. Keep working transparent controller A, XGO GOLD, and offline unflashed OLED B statuses unchanged.

[Exact observation and revised fault-tree findings](integrations/gp2040ce-xgo-test01/findings/2026-10-24-CORRECTION-HANDLE-P1-ACTUAL-TEST-CONFIGURATION.md).

---

# CRITICAL NEW HW FACT — CONTRA GHOSTS ON BUILT-IN P1 WITH HANDLE CONNECTED, UNTOUCHED (2026-10-24)

In **GOLD XGO Handle=P1 mode**, user plays Contra with built-in controls, leaves GP2040 connected **without touching it**, and still sees uncommanded logical P1 JUMP. The external does NOT have exclusive takeover of P1: the GOLD helper ORs built-in physical P1/B15 and Handle physical P2/L0 pressed masks. Untouched external buttons do not prove XGO decoded all-zero Handle bits at every scan. An intermittent false bit from idle external or local serial state can become a P1 action; routing OR alone cannot invent one. No P2-mode comparison has yet been reported. The [precise HW addendum](integrations/gp2040ce-xgo-test01/findings/2026-10-24-CORRECTION-HANDLE-P1-ACTUAL-TEST-CONFIGURATION.md) and [model](integrations/gp2040ce-xgo-test01/tests/test_handle_as_p1_fault_isolation.py) constrain the next fault tree. Preserve both protected firmware images, keep paged OLED B unflashed, and do not perform a speculative electrical or keymap fix.

---

# CRITICAL USER HW CLARIFICATION — HANDLE=P1 IN CURRENT CONTROLLER TESTS (2026-10-24)

User reports latest transparent GP2040-CE SFII and Contra testing was done in **XGO GOLD Setup Handle=P1 mode**, so game-visible actions are **logical Player 1**, NOT stock Player 2. The physical RP2040 still drives the **external P2/L0 serial line**, while XGO's native normalizer merges its raw active-high pressed word with **built-in P1/B15** into logical P1 (normal RF P1 preserved). This creates **two physical sources** for P1. A correct OR cannot invent an input bit, so physical false R from EITHER source or later P1 mapping remains possible. The previous P2-only fault attribution must be revised without discarding historical P2 passive sessions. See [actual-P1 configuration correction](integrations/gp2040ce-xgo-test01/findings/2026-10-24-CORRECTION-HANDLE-P1-ACTUAL-TEST-CONFIGURATION.md) and the [updated master handoff](integrations/gp2040ce-xgo-test01/HANDOFF-2026-10-24-TRANSPARENT-BASELINE-AND-INPUT-FAULTS.md).

**Protected separately:** XGO GOLD host BIOS SHA `75f858b6d9a1eb81235ae9e9c9b449a6a3052ad4365e5411b8ce041075e99d6b`; user-tested GP2040 transparent UF2 A SHA `94ea7228c774a67e8252e7e09d94938530e5d74572d985332e6840ae09fe8b84`; paged-OLED GP2040 UF2 B SHA `5dcc28132ca54293a3d27dc2a452269bc47a1e7f141bd49c2c7e296918071b5b` STILL UNFLASHED. Neither firmware has been modified. Do not request repeat hardware tests at this point.

---

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
