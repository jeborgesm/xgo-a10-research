# Ghost controller — best next evidence gate: native-R-conditional Handle P2 observation

**Date:** 2026-10-25. Branch: `research-gp2040ce-xgo-integration`. **Status:** verified XGO-original [BIN], verified GOLD mode semantics [SRC/MODEL], old passive spontaneous P2 jumps [HW], new reversible single-session diagnostic [PROPOSED HW]. No firmware or wiring changes.

## 1. Stop designing synthetic timeouts and target the known idle ghost

The hardware root cause of ghost Contra jumps remains OPEN. In earlier independent electrical tests, merely attaching a passive native-USB-PHY Pico via ordinary Micro-USB cable caused P2 spontaneous JUMP with no transmitted button bits; connecting a scope probe to GREEN P2 DATA also produced unsolicited P2 jump. Protected GP2040 transparent A is playable (including SFII); live held-button faults and idle ghost action remain OPEN. The current Frankie V2 Jr has its own special physical pad bridge and is **not** electrically identical to the P3 cable.

Previous successful synthetic regressions distinguished:
- host false R0 when DATA rises too late (can produce Jump with **zero responder CLK errors**);
- missed RP-observed CLOCK edges (may shift a genuinely held button and present S12 timeout);
- host CPU IRQ-stretched CLOCK (can cause LOW/HIGH timeout without missing an edge);
- short-clock-HIGH waveform (P0 captured ~1.36us **mean** HIGH, but linked ARM seven-instruction SRAM polling code is comparatively efficient; no measured current polling-latency defect).

These explanations have hit a practical diagnostic boundary: **only actual physical behavior, not another invented timing increment, can choose among them.**

## 2. The useful built-in XGO controlled variable [BIN]

On the actual original `XGoAnalisis.zip` `bios/bisrv.asd`, SHA256 `869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf`, the assistant **re-ran a direct `zipfile`/little-endian MIPS instruction check this turn** and verified these exact words:

```
35D864  AE0B0000   release physical L0 Handle DATA
35D868  0C0B81DE   IRQ-enable helper after release
35D870  8E8A0000   read physical native B15 DATA
35D874  31498000   mask first native R bit
35D878  15200005   bne R_bit,zero,35D890
35D87C  36710050   common MIPS branch delay slot
35D880..35D88C    four extra instructions only if native R LOW/pressed
35D890  8E390000   read physical external L0 DATA first R bit
35D894  33330001   mask Handle R0
```

**Native built-in R released:** B15 HIGH => BNE taken, short source path to external L0 R0 sample. **Native R held:** B15 LOW => BNE not taken, **four additional instructions before L0 R0 read**. The interval difference exists in the original firmware but its numerical wall-clock time is UNKNOWN. Protected GOLD Handle toggle changes **logical routing after the physical scanner**, not this hardware read ordering (GOLD host source verified separately by existing archaeology). The original scanner's branch is dependent on physical **native R**, not the logical player mode.

This creates a controlled timing perturbation with **no additional electrical probe or RP2040 firmware change**.

## 3. One reversible A-B-A hardware observation (NOT yet executed)

Setup used in earlier P2 Contra observations and designed not to conflate P1 logical OR:
- Leave **the existing user-tested transparent RP2040 A UF2** and **Frankie V2 Jr** attached exactly as is.
- Leave **XGO GOLD Setup** installed, select **Handle=P2** (important: NOT P1; otherwise both real and external R enter logical P1 and native-R action masks the distinction).
- Start a two-player Contra session so **P2 is independently observable**. Do not touch the external GP2040 buttons. Keep the controller/cable physically stationary throughout.
- **A:** native XGO R released, watch whether the P2 character jumps without GP2040 input.
- **B:** physically hold **native XGO R** while continuing to watch P2. The P1 character will likely execute its own mapped turbo/jump action; **do not count P1 jumps as P2 events**. The external GP2040 remains untouched. The MIPS scanner now executes four more instructions before sampling external R.
- **A again:** release native R and observe the external P2 once more. If the intermittent event rate is low, longer/repeated blocks are more useful than a single event. A rough 20–30s observation for each block is a starting duration rather than a controlled measurement.

Keep the exact same game, same logical mode, cable placement and external controller physical state. This is **not** a request to reflash or alter connector wiring. Pressing XGO native R is an ordinary reversible game input, not an electrical modification. Stop if P2 is unobservable, the console behaves abnormally, or the result is ambiguous.

### Interpretation matrix (predictions [INF], not results)

| Outcome in P2 when native R changes | What it would suggest | What it would NOT prove |
|---|---|---|
| Spontaneous P2 jumps drop with native R HELD, return when RELEASED | Sensitivity to native-R-dependent early external first-bit sampling window; favors DATA recovery timing and possibly clock entry timing | Not direct measurement of voltage, exact four-instruction delay, or proof the RP USB receiver is the only source |
| P2 jumping unchanged throughout | Four-instruction path change not a strong lever for this symptom under tested conditions | Does not rule out first-bit DATA loading; extra instructions may be too short, or fault may be downstream |
| P2 jumping increases on native R HELD | Interaction differs from simple monotone slow-DATA-rise model | Not a specific new mechanism by itself |
| Ghost stops for the entire session under either condition | No positive control, so comparison inconclusive | Not a verified fix |
| Only P1 jumps during native R held, P2 idle | Expected P1 action; ignore for P2 fault classification | No inference about idle P2 signal |

**Critical alternative:** even if A/B toggling correlates with P2 ghost rate, native R executes extra memory instructions and can modify wider scanner timing, not only the DATA recovery aperture. Therefore an A-B-A result would narrow the fault but not uniquely identify analog RC.

## 4. Why not immediately install a DMA-based native PHY capture?

Pico SDK 2.3.1 source exposes `dma_timer_set_fraction(timer,numerator,denominator)`, `dma_get_timer_dreq(timer)`, `channel_config_set_ring(config,write,size_bits)` and native USB PHY physical RX bits `RX_DP`/`RX_DM` read-only in one `USBPHY_DIRECT` 32-bit register. **Source-level possibility:** one paced 32-bit DMA MMIO read per sample could record both native PHY line states in SRAM with no new electrical probe.

However, **this is not yet a validated noninterfering instrument**, for five reasons:

1. At a *hypothetical* 10 MHz sampling rate the DMA would consume **40 MB/s of MMIO reads plus 40 MB/s of SRAM writes, approximately 80 MB/s aggregate data movement**. The exact protected RP Core1 seven-Thumb-instruction polling loops ALSO read that USB PHY register and a timer; shared bus arbitration can alter the event being measured.
2. A 16 KiB write-wrapping ring holds about **409.6us** at 10Msamples/s (4096 32-bit samples), enough for an ~50us burst **only if DMA is actually paced evenly and frozen promptly**.
3. DMA request pacing does not prove that reads complete at evenly spaced instants when MMIO/AXI/APB fabric is contended. The RP2040 bus/PHY access and chosen timer need independent timing qualification.
4. Capturing a host DATA/CLOCK waveform still cannot read the actual XGO MIPS instruction/sample register; **false R0 can be decoded in an otherwise responder-successful frame**, so triggering a buffer only on RP CLK timeout misses crucial ghosts.
5. A diagnostic would require a separate ELF/UF2, RAM/stack ownership and no-regression acceptance, with carefully controlled freeze/export to OLED/USB. The user-tested transparent controller must NOT be silently replaced or burdened.

**Decision:** DMA register-stream acquisition is an **OPEN future diagnostic design option**, not a safe automatic alternative to a high-impedance external probe and not a root-cause fix. Do not create a user hardware candidate from it until bus-interference and timebase correctness are proven offline and acceptance tests can isolate its perturbation.

## 5. Research checkpoint

No GP2040 or GOLD `bisrv.asd` patches, no change to phy pull-up, no cable mods, no repeated high-cost firmware candidates. The **immediate low-risk experimental discriminator is native R released/held/released while the external controller remains idle and connected in Handle=P2 mode**. This directly exploits an original-bin verified timing branch and is less intrusive than adding instrumentation. If hardware result demonstrates a meaningful relationship, use it to decide what and where to measure next; if not, return to the physical PHY loading evidence and avoid assigning current fault to this branch.

**Preserved:** XGO GOLD BIOS SHA256 `75f858b6d9a1eb81235ae9e9c9b449a6a3052ad4365e5411b8ce041075e99d6b`; transparent A UF2 SHA256 `94ea7228c774a67e8252e7e09d94938530e5d74572d985332e6840ae09fe8b84`, Git source blob `cccb985a05baa8bb9078b6e336eb5f991c1a7a8f`; OLED B UF2 SHA256 `5dcc28132ca54293a3d27dc2a452269bc47a1e7f141bd49c2c7e296918071b5b` unflashed.

## Source provenance

- [Original binary branch verifier](../tests/verify_xgo_p1_r_conditioned_p2_first_sample.py).
- [GOLD P1/P2 logical routing source-derived cases](../tests/test_handle_as_p1_fault_isolation.py).
- [Earlier native PHY/passive phantom Jump evidence](2026-10-24-USBPHY-PASSIVE-GHOST-AND-P1-CONDITIONED-P2-R-WINDOW.md).
- [RP2040 source-pinned CLOCK loop disassembly](2026-10-24-P0-CLOCK-HIGH-DUTY-CYCLE-AND-LINKED-RP-POLL-LATENCY.md).
- [P0 waveform analyzer](../../../tools/rp2040-xgo-p0/analyze_frames.py).
- [Pico SDK 2.3.1 DMA SDK](https://github.com/raspberrypi/pico-sdk/blob/2.3.1/src/rp2_common/hardware_dma/include/hardware/dma.h).
