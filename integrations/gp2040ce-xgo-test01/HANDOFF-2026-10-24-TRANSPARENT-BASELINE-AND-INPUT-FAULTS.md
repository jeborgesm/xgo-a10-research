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
