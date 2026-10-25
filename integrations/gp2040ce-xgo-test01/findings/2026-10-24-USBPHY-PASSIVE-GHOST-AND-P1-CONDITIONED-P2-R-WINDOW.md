# XGO ghost input forensic checkpoint: native USB-PHY passive loading and P1-conditioned external R sample

**Date:** 2026-10-24 (local). Branch `research-gp2040ce-xgo-integration`. **Status:** actual original XGO image **BIN**, actual RP2040 sources/SDK **SRC**, prior XGO electrical/gameplay **HW**, narrowly bounded causal hypotheses **INF/OPEN**. No firmware modification, no new hardware experiment. User request: **continue investigating controller ghost inputs** from protected transparent GP2040 baseline, not redesign or migrate to RF.

## 1. New verified original XGO binary property: P1 R alters P2 R0 read latency [BIN]

Tested **locally** against the actual user archive `/mnt/data/XGoAnalisis.zip`:
- `bios/bisrv.asd` SHA-256 `869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf`, little-endian MIPS `0x80000000 + file_offset`.
- Exact opcode/hash-pinned script: [`tests/verify_xgo_p1_r_conditioned_p2_first_sample.py`](../tests/verify_xgo_p1_r_conditioned_p2_first_sample.py), **PASS locally** (runs on original user ZIP; no original binary stored in repository).
- `0x8035D844`: release native/B15 DATA output driver.
- `0x8035D864`: release external/L0 DATA output driver.
- `0x8035D868`: call helper after external release.
- `0x8035D870`: read native B15 physical bit, `0x8035D874`: mask `0x8000` (native first button R).
- `0x8035D878`: `bne t1,zero,+5`, target `0x8035D890`. MIPS instruction at `0x8035D87C` is its unconditional branch-delay slot.
- `0x8035D880`–`0x8035D88C`: **four extra instructions execute only when native P1 R is physically LOW/pressed**.
- `0x8035D890`: `lw t9,0(s1)`, samples **external physical L0** first/R bit, `0x8035D894` masks `0x1`.

This yields a perhaps counterintuitive **timing direction**:

| Native physical P1 R | B15 sample | P1-dependent path before P2 read | Consequence |
|---|---|---|---|
| **Released** (usual) | HIGH, masked bit nonzero | Branch TAKEN, only 1 common delay-slot instruction | External R0 sampled **earlier** |
| **Pressed** | LOW, mask zero | Branch NOT taken, same delay slot PLUS 4 instructions | External R0 sampled **later** |

The delay in wall-clock time is **not measured**; one of the extra instructions is a memory store, so assigning a fabricated number of microseconds would be inappropriate. This is stronger than merely noting that first-sample timing is branch-dependent: the **polarity/physical held condition** is now verified.

**Conditional physical interpretation [INF]:** If external DATA's rising transition is near the host's slot0 logic threshold, the native-R-released shorter path has less margin and could interpret external R as pressed, whereas the native-R-pressed path has relatively more settling time. Because the external serial R0 bit is `0x1000` at the host normalizer and can map to NES jump in stock fallback, the effect could be gameplay-relevant. **Nothing here demonstrates that GPIO DATA actually crosses its threshold in that instruction window on current Frankie V2 Jr.** No new user test requested.

### Family comparison, correctly bounded

UniFrog's newer SF2000/GB300 **replacement firmware** inserts an explicit `KEY_SHIFTER_SETTLE_US=4` between DATA GPIO return-to-input and R0 sampling. The original XGO host decoder has no comparable unconditional post-release 4us wait. UniFrog is not the stock SF2000 firmware and **this finding does not authorize patching XGO GOLD timing** or assuming adding four microseconds fits the stock XGO dual-data scan. The user's SF900 wireless controllers operate their separate SF2000; **XGO has no wireless capability**.

## 2. Native RP2040 USB PHY: source contract versus actual electrical transparency [SRC/HW]

Compared:
- [Current hardware-approved GP2040 transparent A](../candidates/offline-test44-transparent-controller/XGODriver.cpp) with immutable Git blob `cccb985a05baa8bb9078b6e336eb5f991c1a7a8f`.
- [Earlier **receive-only** P3 native PHY experiment](../../../tools/rp2040-xgo-p3-usbphy/main.c), run over an ordinary physical Micro-USB cable.
- Original user [P3 hardware observations](../../../experiments/rp2040-usbphy-p3-passive.md).
- RP2040 **Pico SDK 2.3.1** `hardware/regs/usb.h`, upstream Git blob `d475bed66dc32867b3034304fa68c7528e798825`, and `hardware/structs/usb.h` blob `514940a3fbf1a05db1ff67e8d9a5b0ac24afe55c`. Exact source register definitions, not assumed ordinary USB HID behavior.

The current transparent and earlier passive P3 have **the same ten** `USB_USBPHY_DIRECT_OVERRIDE` control-enable flags; both set `main_ctrl=0`, `sie_ctrl=0`, `phy_direct=0`, and `TO_PHY | SOFTCON`. Native `USBPHY_DIRECT.RX_DP` and `.RX_DM` are specified **read-only physical DPP/DPM pin states**. With `TX_DIFFMODE=0` from `phy_direct=0`, the USB PHY is in **single-ended output mode** per SDK; DP/DM output enable is independent. P3 disables both DP and DM TX output enables and **never calls `data_sink`**. Current A instead reads RX_DP/RX_DM, releases DATA by clearing `TX_DP_OE`, and asserts only LOW by setting `TX_DP_OE` while `TX_DP=0`. It never deliberately drives a HIGH.

**Critical user-observed HW fact:** P3 connected via an *ordinary* cable with **no active DATA transmission** still caused intermittent unsolicited XGO Player-2 JUMP. P3-v4 after restoring previous pull override remained non-freezing but jump persisted; P3-v5 explicitly zeroed SIE and jumps persisted. Therefore serial publication, turbo software, the transparent candidate's output bit map, and native GOLD Handle=P1 OR routing are **not necessary preconditions** for *that older passive physical jump phenomenon*. This is a causal exclusion for passive P3, **not proof the present Frankie active controller has exactly the same electrical mechanism**.

### Incomplete DM pull-up override is deliberate historical evidence, not a recommended change

Both P3 and A override **DP pull-up** and DP/DM pull-down controls and TX output enables, but do NOT enable `USB_USBPHY_DIRECT_OVERRIDE_DM_PULLUP_OVERRIDE_EN`. The SDK documents that DM pull-up override bit as `0x1000`; register default value alone does **not** establish the actual analog line state when USB PHY/mux controls are active. When older P3-v3 added that override-enable with zero pull request, the **actual XGO froze** [HW]; restoring prior configuration un-froze it but ghost jumping persisted [HW]. Therefore **do not add DM_PULLUP_OVERRIDE_EN** or blindly change pull-up/receiver ownership to “quiet” the bus. The failure's electrical explanation remains unknown.

New [current-versus-passive source guard](../tests/test_current_phy_passive_ghost_comparator.py) confirms these specifics and is integrated in the existing fast-serial CI.

## 3. Historical electrical timing is exceptionally tight [HW]

The earlier passive RP2040 GPIO/PIO observation using breakout GREEN DATA and YELLOW CLOCK (RED used as **measured scope reference**, not conventional USB wire-color ground assumption) captured:
- **Exactly 12 CLOCK pulses** per approximately **16.03ms** scan.
- DATA host-driven-low/load intervals of **6.8, 7.3, 7.5us** in an extended three-transaction capture; other separate complete transaction ~**7.8us**.
- The digital DATA HIGH transition preceded the first CLOCK FALL by only **0.9, 1.2, 1.3us** in the three-transaction capture; another transaction **1.2us**.
- The original XGO firmware samples R0 **before** that first CLOCK FALL. The capture is a **digital threshold transition**, not an analog impedance/slew curve. It cannot place the actual P2 R0 read within the 0.9–1.3us window because the host's MMIO sample strobes were not captured.

Previous real probe contact on GREEN caused repeatable **jump-only P2** gameplay. A short unintended direct GREEN/RED contact caused multiple different P2 actions [HW], supporting serial active-low timing sensitivity, but **do not repeat those shorts**. The decisive analog settling time/capacitance remains unmeasured.

### Important cabling confounder

Working **Frankie V2 Jr** deliberately **bridges physical solder pads 2 and 4 through WHITE** on its replacement Micro-B connector; this is required for the hardware-proven working controller. Earlier passive P3 was attached with an **ordinary Micro-USB cable**, not that bridge. The owner's documented pad-number diagram explicitly warns that these are physical **pad positions**, not verified conventional USB pin numbering: we must not claim the bridge is specifically ID-to-DATA or connects named USB signal pins without orientation/continuity evidence. The two hardware setups cannot be treated as identical impedance, load, or analog recovery circuits. This difference remains an **OPEN explanatory variable**.

## 4. Fault-tree consequences

**Higher confidence than before:**
1. An external port's **first R sample is software-timing-sensitive to an entirely different physical stream**, P1 R. That is confirmed original XGO BIN; logical player routing after scanning cannot remove it.
2. The native RP2040 PHY in a transmit-disabled configuration previously caused the same **class of unsolicited P2 jumping**. This strengthens early-turnaround electrical interaction as a serious hypothesis. It does not pinpoint analog load or guarantee same cause on Frankie.
3. A responder can report a complete CLK transaction while the host has sampled false R, as prior source-extracted synthetic tests showed. Therefore OLED error totals alone cannot disprove first-bit DATA misread.
4. The physical DATA HIGH→first CLK FALL gap is roughly **one microsecond** [HW], with R0 sampled somewhere before first CLOCK. There is no basis to assume a generous fixed post-release settling margin.

**Still open:**
- Whether XGO host's R0 read occurs before or after DATA's actual analog threshold crossing on Frankie V2 Jr.
- Whether the current cable's pad-2/4 bridge changes analog loading/ground/reference compared with P3.
- Whether native P1 R-conditioned timing materially changes *real* external R false-positive rate.
- Whether the irregular held A/B actions reflect repeated clock observation faults or game/ROM keymap; no measured current per-frame host raw word.

## 5. Engineering conclusion and protected boundaries

No software-only modification to the RP2040's *later* slot1–11 CLOCK waits can retrospectively make the host's already-completed first R sample read HIGH. Under the **specific unproven hypothesis that DATA is still electrically LOW when XGO reads it**, possibilities would concern host first-sample timing, actual line bias/loading/settling, or faithful safe signal buffering. None is authorized until measured and reversible, and the protected XGO GOLD BIOS remains unmodified.

Do **not** test the previous HW-failed DM-pullup override, drive DATA actively HIGH against XGO host-owned load, remove the working Frankie bridge, replay/pulse fake attacks, reuse HW-rejected Test35 strict clock guard, or make an XGO native GOLD timing change based solely on the hypothesized analog mechanism.

**Current branch state:** protected XGO GOLD and user-tested transparent controller A unchanged, paged OLED B candidate unflashed. This checkpoint advances diagnosis by determining the **P1-R polarity of physical P2 sample latency** and auditing native-PHY passive loading, while leaving the physical root cause honestly OPEN.

## Pinned and executable provenance

- [Original user XGO binary-level branch verifier](../tests/verify_xgo_p1_r_conditioned_p2_first_sample.py): run on `XGoAnalisis.zip`; locally passed.
- [Passive/current USB-PHY source comparison CI guard](../tests/test_current_phy_passive_ghost_comparator.py).
- [Prior first-clock C++ model](2026-10-24-EXACT-CPP-RESPONDER-CHRONOLOGICAL-HOST-DIFFERENTIAL.md).
- [Prior two-frame recovery and S12 ambiguity](2026-10-24-TWO-FRAME-RECOVERY-AND-SLOT12-ERROR-AMBIGUITY.md).
- [P0 original passive captures](../../../experiments/rp2040-passive-probe-p0.md), [P3 passive physical jump and DM override reversal](../../../experiments/rp2040-usbphy-p3-passive.md), [Frankie physical bridge](../../../tools/rp2040-xgo-live-controller/README.md).
- [Pico SDK 2.3.1 native USB PHY register definitions](https://github.com/raspberrypi/pico-sdk/blob/2.3.1/src/rp2040/hardware_regs/include/hardware/regs/usb.h).
