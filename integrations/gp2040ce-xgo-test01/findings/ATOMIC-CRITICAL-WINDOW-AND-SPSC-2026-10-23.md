# XGO GP2040-CE — Test49 atomic/XIP serial critical-window closure

**Date:** 2026-10-23  
**Branch:** `research-gp2040ce-xgo-integration`  
**Disposition:** isolated offline investigation; no hardware build approved, no XGO firmware or Frankie changes.

## 1. Confirmed binary finding (BIN)

The corrected GCC ARM linked-ELF audit in [Actions run 39971706120](https://github.com/jeborgesm/xgo-a10-research/actions/runs/39971706120) **failed for a valid reason**: moving Test49 `emit_frame()` to SRAM does NOT move its out-of-line atomic helper routines out of XIP FLASH.

The compiled RAM-resident `emit_frame()` starts at `0x200000F0`. The linked Cortex-M0+ disassembly shows:

| Code event | Linked address | Interpretation |
|---|---|---|
| `cpsid i` | `0x2000015A` | Core1 masks IRQ |
| `BL ____atomic_exchange_2_veneer` | `0x2000018C` | Pending press exchange while IRQ-masked |
| `BL ____atomic_fetch_or_2_veneer` | `0x200003BE` | Conditional requeue on a branch reachable before IRQ restore |
| `msr PRIMASK, sl` | `0x2000029A`, `0x2000032E` | Normal/alternate IRQ restore paths |

**Important:** the conditional requeue helper has a later *linear* instruction address than the first IRQ restoration. It is nevertheless executed on a branch from earlier in the masked region. The correct binary audit must traverse Thumb conditional branches, not divide the file at the first `msr PRIMASK`.

Resolved actual helper destinations (BIN):

- `____atomic_exchange_2_veneer` at `0x20005A38` forwards to `__atomic_exchange_2` at **`0x100829E0` (XIP)**.
- `____atomic_fetch_or_2_veneer` at `0x20005BB8` forwards to `__atomic_fetch_or_2` at **`0x10082A38` (XIP)**.
- Numerous `____atomic_fetch_add_4_veneer` calls forward to **`0x10082A0C` (XIP)**; their main diagnostic paths run after IRQ restore rather than between LOAD and serial CLOCK.

Actual emitted `__atomic_exchange_2` and `__atomic_fetch_or_2` code saves PRIMASK, runs `cpsid i`, loops reading **`0xD0000134` (RP2040 SIO hardware spinlock 13)** until it becomes available, applies a DMB, updates the shared value, releases the spinlock and restores PRIMASK. This is a concrete opportunity for variable latency and multicore contention. The duration was NOT measured, and a particular Contra phantom input cannot yet be attributed to it.

Evidence retained in Actions artifact **`xgo-gp2040ce-RAM-ELF-EVIDENCE-NOT-FLASHABLE`**, ID **12509287881**, including complete linked `nm` and `objdump` text. No UF2 distributed. The linked code above is pinned to the experimental RAM-only Test49 overlay and the repository's existing upstream/toolchain pins.

## 2. Exact source implication (SRC)

In Test49 `emit_frame()`, after `wait_data(false, LOAD_TIMEOUT_US)` detects XGO LOAD low, the code disables Core1 IRQs, reads `published_mask`, and performs `pending_press_edges.exchange(0, acq_rel)`. During rapid taps when a previous 18ms attack pulse is still active, the code may also execute `pending_press_edges.fetch_or(pending, release)` **before the first CLOCK bit**.

The actual host's LOAD-low duration is only approximately 6.8–7.5µs, with DATA release about 0.9–1.3µs before first CLOCK-low (P0 hardware capture). These calls could consume important response margin. Unlike an IRQ handler, flash/XIP fetch delay or shared spinlock competition remains possible even after `save_and_disable_interrupts()`.

**Not established:** that spinlock wait reached several microseconds on the user's Test49 unit, or that it alone explains an erroneous START/PAUSE. Test49 didn't count processed START edges. The earlier false R/JUMP hypothesis also depends on DATA level at the immediate first-slot host sample and remains OPEN.

## 3. Isolated corrective experiment (SRC / MODEL)

Candidate: `candidates/offline-spsc-ram-hotpath/XGODriver.cpp`.

It inherits SRAM placement from the preceding RAM-only candidate, but replaces the two-way atomic pending-bit exchange/requeue protocol with six **single-producer, single-consumer event-generation counters**:

- Core0 increments the corresponding 32-bit counter for each **actual rising edge**; the same existing attack diagnostics remain intact.
- Core1 takes six aligned 32-bit `load(acquire)` snapshots, comparing each with its own last-consumed counter. This avoids a lock-taking read-modify-write in the LOAD-to-first-bit window.
- Core1 advances its private consumed generation only **when the pending attack is actually admitted to the pulse window**. If a prior pulse is active, later presses remain pending across scans. A Core0 event arriving after a Core1 load has a newer generation and remains eligible on the next scan.
- GPIO/HK slot0, serial 12-bit ordering, 18µs CLOCK timeout, 18ms attack pulse, mask composition, refresh/OLED diagnostics and failure recovery remain unchanged.

**Limit:** Core0's generation increments still use atomic helper calls but are outside the Core1 serial hot path. Six Core1 `load(acquire)` operations cost instructions, so binary placement and early response timing must be audited before flashing. Test49 source and Test44 protected hardware remain untouched.

Offline Python source-exact-diff guards and seven behavioral tests compare original pending-bit queue with SPSC generations: rapid fire, held one-shot, deferred overlapping presses, simultaneous attack buttons, events after a scan snapshot, 32-bit wrap and **25,000 deterministic event operations**. [Fast CI run 39985359052](https://github.com/jeborgesm/xgo-a10-research/actions/runs/39985359052): **PASS**. This is *model equivalence*, not hardware input latency proof.

## 4. Mandatory binary gate

`tests/test_irq_window_elf.py` analyzes the **actual linked ELF machine code**, starts at the Core1 `cpsid i`, traverses conditional/unconditional Thumb branches until every reachable `msr PRIMASK` restore, collects all reachable `BL` calls, and follows each veneer through the ELF symbol table. Unresolved/XIP calls fail closed.

`.github/workflows/gp2040ce-xgo-spsc-ram-offline.yml` must:

1. Compile the SRAM-only original implementation, audit with `EXPECT_DIRTY`; confirm both helper hazards exist.
2. Substitute ONLY the isolated SPSC candidate into the same pinned protected GP2040-CE overlay, compile its complete RP2040 firmware and audit with `EXPECT_CLEAN`.
3. Preserve linked symbols and disassembly **without uploading UF2**. Only a successful step 2 confirms removal of flash calls from the IRQ-masked window in the compiled binary.

The outcome of this full linked-build gate must be recorded from CI, not inferred from Python source models. Even successful binary verification would not establish hardware reliability or authorization to flash.

## 5. Open questions and discipline

- Exact elapsed time from XGO LOAD assertion to first-slot DATA: neither GCC disassembly nor synthetic delay sweeps measure the physical line.
- Whether six lock-free Core1 loads satisfy the early first-bit deadline in all cases; bounded timing must be assessed offline as far as possible before physical use.
- Whether false START arose upstream from processed S2 rather than serial phase drift; Test50 hardware run remains on hold.
- No user hardware test, equipment purchase, PIO rewrite, XGO BIOS edit, or large unrelated controller feature change.

**Status rule:** CI results and actual hardware observations retain separate BIN/SRC/MODEL/HW/OPEN evidence labels. Avoid declaring a simulated false START a proven hardware root cause.

## 6. Full linked Cortex-M0+ comparison — verified result

**BIN VERIFIED PASS:** [GP2040-CE SPSC/IRQ-window build, run 39985794456](https://github.com/jeborgesm/xgo-a10-research/actions/runs/39985794456) at commit `6cd5acd4a7faa54638e80eb18a6ea175353c538f`. CI status `xgo-spsc-ram/offline-irq-audit = success`, with both baseline and candidate compiled from the same pinned GP2040-CE and Pico SDK checkout.

This build extracted two complete *linked* ELF disassemblies and nm tables into artifact **`xgo-gp2040ce-SPSC-IRQ-ELF-EVIDENCE-NOT-FLASHABLE`** (artifact ID **12516859458**, no UF2).

| Linked `emit_frame()` property | SRAM-only Test49 | Isolated SPSC + SRAM |
|---|---:|---:|
| Function SRAM entry | `0x200000F0` | `0x200000F0` |
| Function size | 1028 bytes (`0x404`) | 1148 bytes (`0x47C`) |
| IRQ-masked CFG reachable instructions* | 220 | 281 |
| IRQ restores reached in CFG | `0x2000029A`, `0x2000032E` | `0x20000324`, `0x200003AC` |
| Call sites reachable before IRQ restoration | **2** | **0** |
| XIP FLASH call targets before IRQ restoration | **2** | **0** |

\*Reachable unique code locations, **NOT instructions executed in one transaction** and not a cycle/timing measurement. SPSC's six-counter loop executes some locations repeatedly, so its runtime must not be estimated from the 281 count. The 120-byte size increase likewise does not prove a fixed-time delta.

The baseline CFG confirms `__atomic_exchange_2` and conditional `__atomic_fetch_or_2` target FLASH through RAM veneers. The candidate CFG confirms neither exchange/requeue nor any other subroutine call occurs while Core1 is interrupt-masked. The compiler inlines the six aligned 32-bit generation loads; the generated loop includes a `dmb ish` per acquire load. Thus the candidate replaces an unpredictable XIP/spinlock path with bounded source-level SRAM loop work, **but** we have not measured worst-case SRAM contention or the elapsed time before slot0 is presented.

**The compiler-check now definitively closes the originally stated *code-path* problem. It does NOT verify firmware/host behavior on hardware.**

### Further source-guided fast tests

At [fast regression 39986453935](https://github.com/jeborgesm/xgo-a10-research/actions/runs/39986453935), the actual SPSC C++ `emit_frame()`, extracted from the candidate, passed 4096/4096 ideal 12-bit masks, 22 mid-frame abort/recovery pairs, and the R/slot0 false-low injection, in addition to the original Test49 and postamble versions.

At [free-running-clock regression 39991908964](https://github.com/jeborgesm/xgo-a10-research/actions/runs/39991908964), actual extracted SPSC C++ also passed 4096 nominal masks under an independently advancing virtual XGO clock. The deliberately injected late-FIRE-to-START and DATA-rise-to-false-R failures are still reproducible for SPSC under **artificial timing faults**—the SPSC transformation does not modify the host electrical protocol.

At [preamble timing-sensitivity regression 39992215627](https://github.com/jeborgesm/xgo-a10-research/actions/runs/39992215627), all three source variants remained green. With the representative P0 LOAD/clock timing and **hypothetical** setup/CPU overhead, a +4.75µs injected delay after LOAD detection first caused an intentional R/slot0 to be missed. This is a **MODEL threshold**, not measured SPSC code runtime, and does not establish that its six-counter snapshot exceeds that limit. The test makes the remaining real-time constraint visible.

### Engineering disposition

- **Confirmed solved in linked code:** flash-resident spinlock-taking helper calls reachable between `cpsid i` and PRIMASK restore are eliminated.
- **Not yet proven:** absolute timing margin at the immediate host R/slot0 sample; absence of spontaneous JUMP or PAUSE under live Contra; whether the legacy S12 failures diminish.
- **Protected:** Test44, Test49 hardware witness, 18ms input pulse, all mappings, Frankie, and XGO firmware.
- **Candidate status:** source and binary offline verified; no UF2 distributed and no hardware validation. Do not represent the result as a fixed controller until a single targeted hardware session is justified and executed.
