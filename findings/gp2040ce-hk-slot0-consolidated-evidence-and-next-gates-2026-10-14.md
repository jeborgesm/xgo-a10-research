# HK slot0 consolidated checkpoint — 2026-10-14

## Purpose
Preserve verified progress and prevent another ungrounded firmware candidate. Protected hardware baseline **Test16**; Tests17,21,22,23,24 did not fix HK and introduced or retained failures. No new UF2 from this checkpoint.

## Direct re-verification (BIN)
Source: user-supplied `/mnt/data/XGoAnalisis.zip`, `bios/bisrv.asd`; little-endian MIPS32 words extracted with `struct.unpack_from('<I', ...)`.

| Offset | Word | Meaning |
|---|---|---|
| 0x35D844 | 0xae2e0000 | `sw t6,0(s1)`: first stream output-enable release |
| 0x35D848 | 0x0c0b81de | `jal 0x2e0778` |
| 0x35D850 | 0x0c0b81d4 | `jal 0x2e0750` |
| 0x35D864 | 0xae0b0000 | `sw t3,0(s0)`: second stream output-enable release |
| 0x35D868 | 0x0c0b81de | `jal 0x2e0778` |
| 0x35D870 | 0x8e8a0000 | first stream DATA read |
| 0x35D874 | 0x31498000 | first stream bit15 test |
| 0x35D878 | 0x15200005 | `bne t1,zero,+5`: branch to 0x35D890 |
| 0x35D87C | 0x36710050 | branch delay slot, executes either way |
| 0x35D880–0x35D88C | four words | execute on branch-not-taken path only |
| 0x35D890 | 0x8e390000 | second stream DATA read |
| 0x35D894 | 0x33330001 | second stream bit0 test |

**Correction to earlier characterization:** `0x2e0778` and `0x2e0750` are NOT established as microsecond delay helpers. Prior `findings/xgo-scanner-clock-phase-binary-confirmed-2026-10-12.md` identifies them as gp-counter/resource routines. The actual 2-unit delay routine is `0x30fed0`, used in the CLOCK train. Thus do not claim stream1 has 'three delays' or that stream2 has 'one delay'. These are *calls*, not proven time waits. Actual sample windows remain unmeasured.

## HW and SRC observations
- GP2040 OLED correctly shows physical HK as RB.
- Test16 maps `pressedR1()` to bit0; XGO sometimes produces HK from taps and produces HK when held, so the mapping is functionally reachable.
- Fast HK taps often missed; holding HK initially produces MP then repeated HK. Other held buttons also show glitch/repeat. SFII does not auto-repeat held attacks as normal behavior.
- Tests23/24 changed slot0 software response order/polling but did not solve.
- RP2040 USB PHY direct mode observes host DATA release on same shared DATA wire before asserting slot0 LOW. This is a potential bus-turnaround race, not yet electrically measured.

## Hypotheses / confidence
1. **Leading INF:** slot0 bus-turnaround/setup timing or frame alignment; consistent with intermittent recognition and wrong attacks, but not proven.
2. **OPEN:** exact external controller port maps to B15 versus L0; this affects first-sample deadline and branch dependency.
3. **OPEN:** compiled Test16 cycles from LOAD release to DATA sink and electrical pull-up rise/fall settling.
4. **OPEN:** MP-on-HK origin (cross-slot contamination vs stale state vs game mapping); no evidence to assign a particular shifted bit.
5. **BIN:** original stock Arcade default map has no turbo bits. Current SD per-game override still unverified.

## Recommended investigation gates (offline before new hardware request)
A. Trace board wiring or OEM schematic/PCB photographs to identify which GPIO DATA stream serves external controller.
B. Inspect built Test16 disassembly for critical path, especially `wait_data(true)`, `data_level()`, `data_sink()` and `time_us_32()`; compare CPU instruction/call costs but do not equate CPU cycles with total bus latency.
C. Review original controller electrical interface: pull-up value, whether DATA is open drain, and whether a distinct LOAD/STROBE wire exists. Do not assume external LOAD without evidence.
D. Only then propose a single discriminating experiment with expected outcomes and rollback to Test16.

## Progress state
No source modifications to Test16. No new firmware. Research is at the electrical/host timing evidence gate.
