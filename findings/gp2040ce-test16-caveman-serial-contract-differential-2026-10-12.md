# Test16 vs Caveman: serial contract differential (2026-10-12)

**No hardware candidate authorized.** Protected Test14 unchanged.

## Source comparison
Compared `tools/rp2040-xgo-native-contra/main.c` with `integrations/gp2040ce-xgo-test01/candidates/test16-offline/XGODriver.cpp` on branch `research-gp2040ce-xgo-integration`.

### Identical essential transmission order (SRC)
Both: release DATA; wait for host DATA-low LOAD; wait DATA-high release; drive slot 0; for slots 1–11 wait CLOCK-low, drive slot bit, wait CLOCK-high; consume trailing CLOCK-low and release DATA; wait final high. Both read RX_DM/RX_DP via native USB PHY and drive DP output enable via set/clear alias. Both use 12us edge timeouts and 20ms LOAD timeout.

### Differences that require causal discrimination (SRC)
- Caveman: script-supplied fixed mask; GP2040-CE: `map_mask(Gamepad*)` and atomic published mask, loaded after LOAD acquisition. This adds the separate mapping/state-publication failure domain.
- Caveman: no interrupts masked in emit_frame; GP2040-CE: disables local interrupts from LOAD-low acquisition through trailing clock and restores them after final rise.
- Caveman: no idle-high recovery latch; GP2040-CE: `require_idle_high` after a failed frame.
- Caveman: simple failure return and LED indication; GP2040-CE: extensive atomic diagnostics after each attempt and timeout bookkeeping.
- Caveman: final CLOCK-high wait ignored; GP2040-CE: final high must succeed for frame success.
- Caveman: no concurrent GP2040 app/OLED/USB-host workload; GP2040-CE: Core0 performs app tasks while Core1 responds.

### Key inference (NOT PROVEN)
Both change DATA *after observing CLOCK-low*. If XGO samples during the low pulse before DATA is updated, a preceding-slot value can be observed. The XGO host's precise read phase, RP2040 compiled instruction timing, and analog rise/fall margins remain OPEN. Moving cores cannot cure an intrinsic setup-time violation.

### Next discriminating evidence
1. Reconstruct exact load/clock/sample order and cycle separation from XGO scanner `bios/bisrv.asd` at ~0x35D770; distinguish initial read from later slot reads.
2. Verify map_mask slot-to-physical-button mapping independently of SF2 gameplay labels. Wrong mapping can produce stable wrong identity; slot phase error can produce adjacent/cross-slot identity.
3. Compare compiler-generated instructions and actual clocks for Caveman vs Test16 hot path; count from detection of falling CLOCK to DATA OE write.
4. Create offline serial state decoder test vectors for all 12 one-hot bits, holds, release and simultaneous combinations, including phase-delayed receiver sampling and timeout/rearm cases.
5. Only after causal evidence choose minimal fix; no more timing-guess UF2.

**Evidence:** HW Test16 wrong button identity and phantom Select; SRC source files above; INF setup-time/phase hazard; OPEN exact host read instant and actual timing.
