# SF900 on SF2000: known-good wireless controller versus XGO's wired Handle — forensic comparison

**2026-10-24. Research branch:** `research-gp2040ce-xgo-integration`. User's direct HW comparator + pinned XGO original BIN + upstream live SRC + bounded MODEL. **No binary changes, no new user hardware trial or request.**

## OWNER CORRECTION — THIS XGO A10 HAS NO WIRELESS-CONTROLLER CAPABILITY (2026-10-24)

**USER HW/product fact, controlling for this project:** The owner explicitly confirmed the XGO A10 does **not** have wireless-controller capability; the external controller is connected via the **wired proprietary Micro-USB-shaped Handle Interface**. Treat the XGO as **wired-only** for engineering, testing and recommendations. The earlier suggestion that the user's SF900 controllers might work wirelessly with the XGO based on common firmware RF code was **unwarranted** and is withdrawn. **Never request a wireless controller test or suggest wireless pairing with the user's XGO as an alternative solution.**

**Evidence discipline:** Original XGO firmware still contains genuine SF2000-family RF driver routines and matching calibration/packet constants [BIN], and the SF900 controllers work with the user's separate SF2000 [HW]. These are shared-software-lineage findings, **not evidence of XGO wireless capability, a populated receiver, or an RF path in the user's actual controller use**. Board component-level population was not verified in this investigation, but it does not reopen the owner's explicit functional constraint. The comparison's useful part is the common decoded button map and differences in transport; **the working GP2040 XGO path remains wired DATA/CLOCK on L0, irrespective of RF code**. The XGO GOLD post-scan P1/P2 toggle is unrelated to the wireless SF900 hardware switch.

**Supersedes** the speculative “XGO radio population OPEN / future SF900-on-XGO test” passages below where they could be read as suggesting a viable wireless accessory or follow-up. Those passages are retained only as historical archaeology, not an active option.

---

## Motivation and hardware context [HW]

The user owns **SF900 controllers that control an SF2000 flawlessly** and can switch P1/P2 with their physical switch. They suggest studying that working family system while investigating XGO/GP2040-CE unexpected Contra jumps, SFII intermittent inputs, and particularly the worse external-P2 perceived A/B holds. This is a useful comparator, **not a request to change the GP2040 hardware or abandon our transparent-controller baseline**.

Do not conflate:
- **SF900 ↔ SF2000:** proprietary 2.4-GHz **XN297L RF packet transport**, RF pipe P1/P2.
- **GP2040-CE ↔ XGO A10 Handle:** wired, micro-USB-shaped proprietary **12-bit active-low DATA/CLOCK physical serialization**, host-driven DATA LOAD low, first-bit turnaround.
- **XGO native Setup Handle=P1/P2 toggle:** post-scan logical role selection for wired Handle, *not* XN297L RF pipe switching.

## New direct original-XGO BIN re-verification [BIN]

Verified /mnt/data/XGoAnalisis.zip entry `bios/bisrv.asd`, **SHA-256 `869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf`**, 12,768,452 bytes. The RF fingerprints each appeared **exactly once**, with these XGO original-image file offsets:

| Family RF parameter | Hex bytes (XGO, UniFrog, SF900 receiver) | XGO file offset |
|---|---|---|
| Four hopping channels | `04 1D 31 4F` | `0xC2D0E8` |
| RF RX address / P2 pipe | `B2 9D 59 4F E3` | `0xC2D0EC` |
| RF RX address / P1 pipe | `DC A8 F3 6B 74` | `0xC2D0F4` |
| Radio calibration | `F6 37 5D` | `0xC2D108` |
| Baseband calibration | `0A 6D 67 9C 46` | `0xC2D10C` |

Independently checked 4 actual MIPS instruction words:
- `0x8035D6E8: 0x30430040` — RX packet-ready bit `0x40`;
- `0x8035DE44: 0x24040061` — payload-read command `0x61`;
- `0x8035DE4C: 0x24050002` — packet length **2 bytes**;
- `0x8035DE7C: 0x32080002` — receiver status bit `0x02` distinguishes RF P1 versus P2.

These findings are independently compatible with the earlier detailed [RF bit-for-bit SF2000 comparison](../../../findings/rf-bit-for-bit-sf2000-comparison.md), and current external code below. New executable read-only verifier `tests/test_sf900_sf2000_rf_lineage_original_xgo.py` **PASS on original user ZIP**.

**This proves firmware-level protocol ancestry, NOT presence of a radio receiver IC/antenna on this XGO specimen.** An RF driver and its tables in the firmware can exist on an unpopulated board; no SF900-on-XGO test is reported.

## Current primary source comparison [SRC, exact upstream revisions]

1. [UniFrog SF2000 wireless receiver](https://github.com/axgdev/UniFrog/blob/fe0d3acd202d7fbd396dbfac90d7a29f8ee2a961/foundation/src/platform/sf2000/input/unifrog_input_wireless.c), fetched 2026-10-24, blob SHA `e0bd41ea5ae5315c93a656c459b8ce2572e8c36c`;
2. [UniFrog SF2000-family local wired scanner](https://github.com/axgdev/UniFrog/blob/fe0d3acd202d7fbd396dbfac90d7a29f8ee2a961/foundation/src/platform/sf2000/input/unifrog_input.c), blob SHA `1041b06ab906d58b4159cc64927d113564a02c35`;
3. [Independent functional SF900 ESP32/XN297L receiver protocol specification](https://github.com/fernandoalves25/sf900-esp32-dongle/blob/f8b14366bc2218d49b03e06e6afac7f079772628/docs/PROTOCOL.md), blob SHA `90a552c84672a12d9b42e0a515d24dad9651b446`. This explicitly credits UniFrog; it is a **working independent implementation**, not independent discovery of all packet parameters.

### SF900 receiver actually handles buttons and P1/P2 how?

**Complete RF payload, not 12 bit-clocks from the game console.** The receiver reads XN297L STATUS register `0x07`, tests RX-ready `0x40`, fetches **2 payload bytes** via `0x61` and converts:

```c
raw = (pkt[0] << 8) | (~pkt[1] & 0xFF);
port = ((status >> 1) & 7) == 1 ? 1 : 0; // for normal pipe 0/1
```

UniFrog's actual `rf_decode_stock_port()` handles pipe 0→P1, pipe 1→P2 and has a **fallback** to raw-bit `0x8000` for non-0/1 pipe values. The XGO stock MIPS checks status bit `0x02`: RF status `0x40`→P1; `0x42`→P2. The RF radio supports hardware **2-byte CRC** and scrambling; packet integrity mechanism is intrinsically different from a host directly sampling successive bits of an attached wired DATA line.

**The button bitmap is the same after decoding:** R=`0x1000`, Y=`0x2000`, X=`0x4000`, L=`0x0800`, A=`0x0080`, B=`0x0040`, SELECT=`0x0020`, START=`0x0010`, UP=`0x0008`, DOWN=`0x0004`, LEFT=`0x0002`, RIGHT=`0x0001`. XGO's wired 12-clock shift order maps to exactly these masks. The game-input layer ORs **pressed masks**, regardless of RF or wired transport.

**What happens when there is no RF packet:** current UniFrog receiver retains the last per-player `wireless_state[port]`, increments a timeout per unsuccessful *poll_once*, and clears the state after more than **90 empty polls**. It advances channel after two empty polls. It is not a direct statement about stock SF2000 firmware's identical timeout constant and NOT a guaranteed wall-clock millisecond interval (multiple polls occur per caller update). The independent SF900 receiver documentation notes the controller may sleep quickly when idle. Receiver timeouts ensure absent packets do not indefinitely imply a held state, while complete received packets overwrite a per-player mask.

**Key conclusion:** no first-slot RELEASE→sample race exists inside this *RF decoding* path; an unreadable RF packet can be lost or leave temporarily stale state, but it does not produce an arbitrarily low wired R/slot0 voltage at the XGO. These are different failure modes.

### Critical family wired scanner comparison — 4us post-LOAD settle

The modern *community UniFrog* local scanner explicitly configures a DATA GPIO as output, drives it LOW for **`KEY_SHIFTER_LOAD_US=4`**, returns it to input, **waits `KEY_SHIFTER_SETTLE_US=4`**, then samples R/slot0. This is present both for its SF2000 single-DATA and GB300 dual-DATA paths; low and high CLOCK phase waits are each nominally **3us** in its source.

The protected **stock XGO original scanner** drives B15 and L0 LOW in a load phase, releases those lines to inputs, and samples R/slot0 immediately (original MIPS P1 sample `0x8035D870`, P2 `0x8035D890`) before the first B7 clock transition. Our prior original BIN analysis showed **P1 first-bit state controls a small conditional instruction-path delay before P2 is sampled**. The passive user P0 observed external DATA HIGH only about **1.2us** ahead of first CLOCK falling. This is a coherent physical hypothesis for a false first-slot R (NES Jump) as DATA recovers from host-driven LOW.

**Scope caution:** UniFrog is a newer replacement community firmware, not a recorded disassembly of the user-owned SF900 controller or the precise SF2000 stock firmware running on the user's successful unit. **4us is a SOURCE choice in UniFrog and not a measured minimal settling requirement.** The SF900 RF path does not even use this wired keypad scanner. Therefore the user's flawless SF900 wireless gameplay does NOT by itself prove its original SF2000 host waits 4us.

A safe candidate to add 4us to XGO `bisrv.asd` **does not follow**: it modifies hardware-proven GOLD host timings and interacts with two physical DATA channels. Attempt to improve the controller-side DATA release / input phase only after source and waveform evidence; do not blindly delay RP2040 output after host first sample.

### Another useful UniFrog source caution

UniFrog explicitly comments that its RF receive poll may temporarily take ownership of L23–L29 shared GPIO bank; it restores the local shifter GPIO configuration and merges pre/post RF physical samples before updating debounce once. Otherwise processing the same poll twice could create alternating pressed/released states during GPIO settling. **This is a source-proven pitfall on that SF2000 implementation, not proof of an analogous RP2040 or XGO bug.** XGO's known GPIO lines and native GOLD software routing differ.

## Offline state-boundary differential [MODEL; executed PASS]

The new `tests/test_sf900_xgo_button_state_boundary.py` exhaustively tests **all 4096 physical 12-button subsets in both RF pipe roles**, packs/unpacks the stock RF 2-byte inverted-low-byte representation, and verifies the *decoded* mask equals a correctly assembled wired serial word. It also injects a **hypothetical** host first-bit low while physical A alone is held:

```text
physical held A = 0x0080
correct decoded packet (RF) = 0x0080
wired XGO decoded if slot0 R falsely LOW = 0x1080
```

The MODEL confirms role and common representation don't **need** to create an extra R; corruption would be introduced before convergence (or by a separate later bug). It does not simulate the RF transmitter, wired analog rise time, CRC loss, emulator, actual XGO stock runtime arbitration or any physical run. The test passed locally.

## What transfers to the current reliability problem

| Finding | Evidential value for our wired GP2040 |
| --- | --- |
| Same 12 button bits across RF and wire | **High, BIN/SRC:** same decoded semantic contract |
| SF900 P1/P2 switch uses RF pipe identity | **High, SRC and XGO BIN:** different from wired logical selector |
| SF2000 community wired code waits 4us before bit0 | **Useful design clue:** sensitivity of LOAD release and early R sample; not a validated XGO timing fix |
| Wireless RF packets are CRC-protected and received complete | **High, SRC:** reliability model avoids wired bit-level host sampling; not usable as drop-in protocol |
| UniFrog RF reader retains last state with missing-packet expiry | **Useful contrast:** missed RF packet and missed wired scan have different handling; don't inject a fake pulse into transparent source |
| XGO firmware RF path matches SF2000/SF900 | **High, original BIN:** permits cautious board-population study only |
| SF900 controller flawless on SF2000 according to user | **HW for SF2000, not XGO:** comparator, not proof of current XGO PHY cause |

## Decision, without changing original investigation direction

1. **Continue the original two-fault investigation:** first-bit R false positives versus interrupted/misaligned later held-bit scans. The new RF comparison supports the hypothesis that an upstream acquisition boundary is worth attention, not that the standard post-decoded 12-button word or P1/P2 merge semantics need redesign.
2. Keep known-good XGO GOLD host BIOS SHA `75f858b6d9a1eb81235ae9e9c9b449a6a3052ad4365e5411b8ce041075e99d6b` and GP2040 transparent A UF2 SHA `94ea7228c774a67e8252e7e09d94938530e5d74572d985332e6840ae09fe8b84`; paged OLED B remains unflashed. Do not change RF pins, XGO console timing or RP2040 output parameters by analogy alone.
3. A future SF900-on-XGO receiver test requires evidence of a populated, healthy XN297L-compatible RF IC on *this XGO board*, which is currently OPEN. Do not assume antenna or RF receiver exists merely because its firmware supports that hardware.
4. Preserve the user's invitation to investigate clues as clues, not a request to replace our wired controller with a radio project. No new hardware tests requested.

**Code/data provenance:** [XGO RF BIN versus SF2000 analysis](../../../findings/rf-bit-for-bit-sf2000-comparison.md), exact original user `XGoAnalisis.zip`, pinned upstream GitHub sources above, dedicated read-only `tests/test_sf900_sf2000_rf_lineage_original_xgo.py` and `tests/test_sf900_xgo_button_state_boundary.py`.
