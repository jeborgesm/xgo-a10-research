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
