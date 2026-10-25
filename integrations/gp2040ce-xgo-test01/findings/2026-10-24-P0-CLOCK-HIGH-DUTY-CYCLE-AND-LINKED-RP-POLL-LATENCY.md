# XGO Controller Ghost-Input Archaeology — P0 Measured CLOCK Duty Cycle vs protected RP2040 linked polling

**Evidence date:** 2026-10-24 local. **Research branch:** `research-gp2040ce-xgo-integration`. Classes: **HW** original P0 10 MHz passive capture; **SRC/BIN** original pinned firmware, exact *linked ARM assembly* of user-tested transparent A; **MODEL** synthetic C++ host with a chosen PHY-observation latency; **CI** executed. **OPEN** actual timing on Frankie V2 Jr. **No firmware or wiring changes.**

## Why this follow-up matters

Previous successful source-extracted C++ models treated the XGO 12-clock burst as **2µs LOW / 2µs HIGH**, approximately 4µs between consecutive falling edges, consistent with the nominal XGO MIPS delay immediate `2` and early scope's approximate 50% duty waveform. But that is not the best *recorded physical timing evidence*. The actual 10 MHz digital P0 passive acquisition from October 3 captured one **fully timestamped idle transaction** with individual LOW durations. We revisited it and reconstructed the aggregate HIGH window.

## 1. Actual measured P0 scan: LOW phases consume 69% of full 12-pulse span [HW]

Original [P0 passive capture chronology](../../../experiments/rp2040-passive-probe-p0.md), specifically its **complete 16,384-word, 10 MHz** run (P0 input-only, GREEN physical DATA, YELLOW physical CLOCK, RED used only as measured reference). Recorded:

- YELLOW first CLOCK FALL **13,675.5 µs**, final CLOCK RISE **13,723.6 µs** (relative to capture start); **full first-FALL→last-RISE burst = 48.1 µs**.
- The twelve individual CLOCK LOW durations (µs): **2.7, 2.8, 2.7, 3.0, 2.8, 2.5, 2.5, 3.0, 2.7, 2.7, 2.9, 2.8**.
- Sum of LOW = **33.1 µs**; mean LOW = **2.7583 µs**.
- The burst has **eleven** intervening HIGH intervals (not twelve: it begins at the first FALL and ends at the twelfth RISE).
- Sum intervening HIGH = **48.1 − 33.1 = 15.0 µs**; mean HIGH = **15/11 ≈ 1.3636 µs**.
- Arithmetic ratio LOW/burst = **68.8%**.
- Mean FALL→next FALL period inferred from aggregate = `(48.1 - 2.7583)/11 ≈ 4.122 µs`. **Do not** divide the total burst by 12 to estimate FALL period because there are eleven complete intervals plus the terminal LOW.
- The GREEN DATA host LOAD-low was 7.8µs; GREEN returned HIGH 1.2µs before first FALL in that capture.

**Substantive correction:** The older models' uniform 2µs LOW/2µs HIGH waveform is an engineering simplification, not the physically observed duty cycle of this captured scan. *A 1.36µs average HIGH* is a narrower observation window than previously assumed.

**Limit:** These timestamps describe **one archived 10 MHz P0 capture, not every XGO game state or the current GP2040/Frankie V2 Jr line**, and the P0 report does not include the individual durations of the eleven HIGH windows. Their arithmetic mean is 1.36µs; actual minimum may be smaller. We cannot turn the mean into a guaranteed HIGH pulse width nor measure current RP2040 detection from P0 alone.

## 2. Exact user-tested transparent A ELF audit: seven Thumb operations per poll [SRC, linked firmware]

Recovered the **original protected transparent GP2040-CE linked ELF audit** built in [Actions #40071967532](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40071967532), artifact **12551597007**, name `XGO-TRANSPARENT-CONTROLLER-LINKED-ELF-AUDIT`. It includes linked disassembly (17,352,767 bytes, SHA-256 `482031f65ae7d58f50174d6c4842a83794a9b216c0eb9845bca8dcb734b0564d`) and symbols (SHA-256 `b7614094a0af45e6b90230aef04341da7d08e3ca9b97ffff64fb40c364d45ee1`). Verified this is the hardware-approved transparent controller source Git blob `cccb985a05baa8bb9078b6e336eb5f991c1a7a8f` and controller A UF2 SHA `94ea7228c774a67e8252e7e09d94938530e5d74572d985332e6840ae09fe8b84`, already recorded in its build manifest and later confirmed on device.

The linked `(anonymous namespace)::emit_frame()` starts in **SRAM at 0x200000F0**, size `0x2D8` bytes. The clock wait code is **inlined and stored in SRAM**; there is **no separate C++ `wait_clock()` function call on each poll**. Exact Thumb disassembly:

```asm
; CLOCK FALL/LOW wait, compare time_us_32() difference > 18
200001d6: ldr   r3,[r2,#40]       ; timer MMIO (0x40054028)
200001d8: subs  r3,r3,r4
200001da: cmp   r3,#18
200001dc: bhi   20000286          ; timeout
200001de: ldr   r3,[r0,#124]      ; USB PHY DIRECT MMIO (0x5011007c)
200001e0: tst   r3,r1             ; RX_DM = 0x40000
200001e2: bne   200001d6         ; keep waiting for LOW

; CLOCK RISE/HIGH wait, compare time_us_32() difference > 18
200001f8: ldr   r3,[r2,#40]
200001fa: subs  r3,r3,r4
200001fc: cmp   r3,#18
200001fe: bhi   20000286
20000200: ldr   r3,[r0,#124]
20000202: tst   r3,r1
20000204: beq   200001f8         ; keep waiting for HIGH
```

Each repeated wait iteration has **seven Thumb instructions including two peripheral MMIO reads and one conditional branch**; this verifies why the source C++ can, in principle, monitor narrow host CLOCK transitions at a rapid rate. Interrupt masking on Core1 is genuine in this linked image: `mrs PRIMASK` at `0x20000152`, `cpsid i` at `0x20000156`, restored via `msr PRIMASK` `0x20000296`. Thus RP Core1 *normal interrupts* do not ordinarily preempt its active 12-slot loop; it can still suffer MMIO/arbitration delays, receiver threshold noise, or a gap it never observes.

**Do NOT assign an actual microsecond duration to seven instructions:** the CPU frequency/runtime clock config, APB/AHB peripheral load wait states, arbitration with Core0, and peripheral crossing costs are not established by the disassembly. The machine code proves the instruction sequence and SRAM location, **not a guaranteed maximum poll interval**.

A new [SHA-pinned linked disassembly verifier](../tests/verify_transparent_a_linked_clock_waits.py) was executed locally against that exact downloaded artifact (the local copy used identical byte/Thumb assertions). It is not silently replacing existing ELF/audit tests and needs the separate linked-disassembly input; the repo intentionally does not commit the 17MB artifact.

## 3. Exact protected C++ virtual timeline: P0 average HIGH versus old 2us assumption [MODEL/CI]

[New exact-source host waveform comparison](../tests/test_p0_measured_short_clock_high_exact_cpp.py) compiles actual `emit_frame()` by extracting the protected A function, changes ONLY virtual `clock_level()`, `time_us_32()`, and polling-time accounting in a temporary program (not firmware), and compares:

- **Old idealized:** uniform LOW=2µs, HIGH=2µs, period=4µs.
- **P0-constrained aggregate:** uniform LOW=33.1/12≈2.758µs, uniform HIGH=15/11≈1.364µs, resulting period≈4.122µs.
- Each synthetic USB PHY/timer observation call advances `modeled_step` by 0.035–1.5µs. A repeated wait loop contains *both* a timer read and a PHY read; therefore a label `0.70 µs step` does NOT mean that the real RP2040 samples CLOCK every 0.70µs. The stepping is a **virtual timing parameter**, not measured latency.
- Across 13 fake arming phases × six constant physical masks (78 independent runs per profile/step), each risky run gets a fresh process so static `require_idle_high` does not contaminate the next test.

[GREEN CI run #40161383012](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40161383012) verified **both source-extracted waveform profiles**:

| Modeled observation-call advance | Earlier 2/2 waveform (wrong-word / failed frames) | P0-derived 2.76/1.36 waveform (wrong-word / failed frames) |
|---|---|---|
| 0.035, 0.10, 0.20, 0.35, 0.50µs | 0 / 0 of 78 each | 0 / 0 of 78 each |
| 0.70µs | **15 / 12** | **11 / 12** |
| 1.00µs | **55 / 66** | **53 / 70** |
| 1.50µs | **65 / 78** | **65 / 78** |

**Critical interpretation:** Shorter average HIGH is plausible as part of a real clock-observation problem, but this *particular* uniform-average model **does not show that using the P0 duty cycle alone suddenly breaks a fast polling loop**. Both models begin exhibiting faults when fabricated observation work becomes much slower, and some cases differ by waveform/phase. No actual RP loop observation interval is measured. This experiment therefore **limits**, rather than closes, the high-phase explanation: do NOT attribute current phantom jumps or previous S12 counts solely to the 1.36µs average HIGH.

Current historical first-bit ghost evidence (passive P3 and GREEN probe causing Jump) remains more direct for unsolicited Contra R/JUMP; those experiments needed no transmitted serial bits at all. Short-HIGH/missed-RP-clock is more relevant to held A/B *identity* and terminal timeouts, conditional on actual edge observation failures. The latest XGO host IRQ-enabled CLOCK intervals remain a separate HOST-stretch possibility, also not measured.

## 4. Evidence consequences and next safe gate

**Confirmed:**
1. Older 2µs/2µs simulated duty assumption did not capture the measured P0 short HIGH budget [HW correction].
2. Protected RP Core1 source is actually linked in SRAM with a seven-Thumb-instruction direct USBPHY polling loop and IRQ masking [linked SRC].
3. Under both short-HIGH and older model clocks, artificially slow observation can lose an edge, shift a real held bit, and report a timeout [MODEL+CI].
4. At modeled small observation overhead, both profiles transmit clean masks in the tested 78 case set [MODEL+CI].

**Open:**
1. True distribution/minimum of P0 **individual** HIGH phases (only their sum is archived).
2. Current real Frankie V2 Jr CLOCK waveform as received by RP2040, timing cost of each linked MMIO loop, whether arbitration/PHY sampling causes missing edge.
3. Actual XGO external R0 DATA analog voltage at its host sample; still the strongest physical explanation for phantom R but **not proven**.
4. XGO host interrupts actually occurring during its nominal 2us phases; code permits but no realtime IRQ trace.

**Decision:** This finding **does not justify widening `EDGE_TIMEOUT_US=18`**, forcing a strict `if (!clock_level())` gate (Test35 was hardware REJECTED), adding synthetic press pulses, altering ROM keymaps or firmware GOLD, changing RP pull-up/PHY settings, or rewiring Frankie. Protect transparent A and GOLD hardware baselines and keep OLED-page B unflashed. Next evidence would need real signal timing or a measurement capable of distinguishing a silent host wrong R0 from a missed CLOCK edge; models alone are now near their explanatory limit. No new device flash/test requested in this research step.

## Provenance

- [P0 complete hardware capture and extended 16ms cadence](../../../experiments/rp2040-passive-probe-p0.md).
- [Linked ELF Audit artifact/run #40071967532](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40071967532), artifact ID 12551597007, disassembly SHA above.
- [Exact compiled-C++ P0-average short-HIGH versus earlier waveform](../tests/test_p0_measured_short_clock_high_exact_cpp.py) and [CI #40161383012](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40161383012).
- [SHA-pinned source linked-ELF clock-loop verifier](../tests/verify_transparent_a_linked_clock_waits.py).
- [Earlier XGO host IRQ scan analysis](2026-10-24-XGO-IRQ-GATED-SCANNER-AND-HOST-CLOCK-STRETCH-MODEL.md).
- [Earlier two-frame 11 clock-loss symptoms](2026-10-24-TWO-FRAME-RECOVERY-AND-SLOT12-ERROR-AMBIGUITY.md).
