# XGO transparent controller — two-clock input loss / false-positive discriminator

**2026-10-24 — offline follow-up to the user's ONLY transparent-controller hardware report.**

## Preserved HW facts

User-tested transparent controller UF2 SHA-256 `94ea7228c774a67e8252e7e09d94938530e5d74572d985332e6840ae09fe8b84` correctly sends holds as holds and taps as taps; SFII playable (Dhalsim defeated), Contra playable with and without X/Y native XGO turbo. Remaining: **spontaneous Contra JUMP**, **SFII intermittent missed LP and one 3-punch LP hold**. These are separate observed symptoms with no captured corresponding DATA frame. Do not add tests or results.

The **paged-OLED** UF2 `5dcc28132ca54293a3d27dc2a452269bc47a1e7f141bd49c2c7e296918071b5b` remains **unflashed**. CI 40107598214 passed; this was an isolated OLED change and did not modify the transparent serializer.

## SRC + MODEL: two independent input sampling clocks, not one

1. GP2040/Core0 reads physical controls, and on its next process pass publishes the coherent 12-bit mask. The current normal OLED blocking path then spends nominally **23.0625 ms** sending 1025 I2C bytes at 400kHz (SSD1306), or 23.58ms in eight SH1106 pages. These are *calculated I2C data transmission* durations, not measured end-to-end Core0 polling periods.
2. Core1 sends the **latest** published mask upon native XGO LOAD. The XGO host scans independently at approximately **16.03 ms** according to historical P0 hardware timing (not a guaranteed constant interval).
3. Under a fully transparent controller, there is **no synthetic edge queue**; a tap that begins and ends between Core0 samples cannot be known to the published mask. Even when Core0 detects a tap, the XGO host can miss it if its entire *published-held interval* falls between two XGO LOADs. A display improvement cannot abolish that second sampling limit without changing physical-hold/tap semantics.

Reproducible deterministic **MODEL-only** grid: [two-sampler + P1-conditional first-slot test](../tests/test_xgo_sampling_and_slot0_discriminators.py). It sweeps 40 uniformly spaced Core0 phases times 40 host phases with assumed nominal **Core0 period = I2C data time only**. This assumption is deliberately optimistic about CPU overhead and is NOT an observed actual Core0 scan rate. For each synthetic tap, records whether any host poll received the last Core0 physical pressed state:

| Synthetic physical tap | Full OLED 23.063ms Core0 nominal | Paged OLED 2.903ms Core0 nominal |
|---|---:|---:|
| 4 ms | 280/1600 (17.5% phase coverage) | 408/1600 (25.5%) |
| 8 ms | 560/1600 (35.0%) | 805/1600 (50.3%) |
| 12 ms | 840/1600 (52.5%) | 1204/1600 (75.2%) |
| 16 ms | 1120/1600 (70.0%) | 1530/1600 (95.6%) |
| 20 ms | 1400/1600 (87.5%) | 1600/1600 (100%) |
| 24 ms | 1600/1600 (100%) | 1600/1600 (100%) |
| 40 ms | 1600/1600 (100%) | 1600/1600 (100%) |

**These percentages are phase-grid coverage, NOT measured failure probabilities, OLED frame-rates, physical press durations, or promises about B.** The model asserts zero ghost buttons when input is never physically pressed. For a 250ms hold, both nominal periodic scenarios eventually deliver it, assuming no bus fault. This is important: persistent complete missed *long* LP holds, if later established as such, would require causes beyond the naive OLED-sampling gap.

### Interpretation

The paged OLED fixes one **source-demonstrated blocking architecture risk**, and might improve short-press capture. But the XGO's roughly 16ms scan remains the host acceptance bound. The model does **not** justify extending all physical taps into fake 18ms pulses: this would violate the permanent controller-transparency contract, change real held/released semantics and recreate Test44's defect. It also cannot explain physical-state-correct Contra ghost JUMP.

## BIN + INF: P1-dependent short P2 slot0 read and hypothetical false JUMP

The exact original XGO `bisrv.asd` SHA `869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf` has P1 GPIO read `0x8035D870`, conditional `bne` `0x8035D878`, P2 GPIO read `0x8035D890`, and FIRST shared CLOCK LOW at `0x8035D8BC`. P1 first bit LOW makes **four extra MIPS instructions** run before P2 first bit; P1 released skips them. This newly decoded **BIN** path is pinned in [binary verifier/finding](2026-10-24-xgo-p1-dependent-p2-slot0-sampling.md). It supplies a falsifiable relative path-time discriminator, not actual microseconds.

The two-sampler script has a *separate optional* synthetic P2 electrical-tail scenario. With explicitly assumed 0.20µs DATA recovery to a valid digital HIGH, 0.10µs fast P2 sample offset, and 0.20µs extra P1-LOW instruction path, the model asserts a false R/slot0 for the fast P1-idle path but not P1-LOW. **ALL three submicrosecond values are invented model parameters**, NOT instrument captures or CPU cycle measurements; they cannot establish a current Frankie V2 Jr analog defect. Existing passive P0 and P3 hardware histories make the path worth checking, but were taken in different cable/probe contexts.

Under the embedded FC default map, **R0, X2 or A4** may cause Contra jump. No live host word, loaded `.kmp`, or precise SFII LP logical binding has been captured for the reported faults. A ghost jump does not uniquely identify R0. No button-specific suppression or remapping is permitted as a false electrical fix.

## Engineering outcome and hard decision boundary

- **Maintained:** source, hash and hardware credibility of the user-tested transparent controller; current normal OLED; native XGO firmware and Frankie cable unchanged.
- **Scoped fix already available:** paged-OLED candidate B source/ELF/CI pass, hardware open. This addresses candidate short-tap/press-onset losses only.
- **No evidence yet for a serial-physical correction:** no active-Frankie analog P2 DATA rise curve; no matching host-decoded 12-bit word during a ghost; no measured IRQ/clock timing violating the completed linked SRAM audit. A pull-up tweak, force-HIGH output, pulse generator, speculative rearm change, or arbitrary timeouts would be unjustified.
- **Next offline discrimination:** separate double-sampler detection failures, incorrect produced mask, and incorrect sampled bus word; use observed P1-conditional host first-bit timing as a bounded hypothesis, and identify the earliest necessary **new measurement**, not new blind firmware variants. The user has explicitly requested no repeated gratuitous hardware tests.
- **Hardware trial sequence when justified:** one reversible paged-OLED B flash using preserved A rollback; separately evaluate short LP, held LP, OLED, and whether Contra still ghosts. This will not isolate the false-JUMP wire bit, and is NOT described as a proven complete correction.

No new UF2 was built, flashed, offered as a ghost-jump fix, or labeled HW PASS by this report. Evidence: HW actual user testimony; BIN original XGO read/disassembly and linked prior ARM archive; SRC controller/I2C source; MODEL phase grids/synthetic settling; INF conditional electrical explanation; OPEN real root cause.
