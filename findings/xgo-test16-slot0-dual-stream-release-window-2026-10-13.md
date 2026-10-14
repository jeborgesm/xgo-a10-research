# Test16 slot-0 dual-stream release window — binary audit

## Evidence
BIN: XGoAnalisis.zip, bios/bisrv.asd, little-endian MIPS32 at file offsets 0x35D804–0x35D894. SRC: Test16 XGODriver.cpp. No hardware inference promoted to proof.

## Host sequence, confirmed from instruction words
- 0x35D804–0x35D818: host prepares +0x54 register and drives DATA LOAD low (bit0).
- 0x35D824–0x35D828: call CP0 Count-based delay helper with argument 4.
- 0x35D834–0x35D844: release stream 1 via output-enable bit15 clear.
- 0x35D848–0x35D854: two intervening helper calls.
- 0x35D858–0x35D864: release stream 2 via output-enable bit0 clear.
- 0x35D868–0x35D86C: one intervening helper call.
- 0x35D870–0x35D874: sample stream 1 slot0 DATA bit15.
- 0x35D890–0x35D894: sample stream 2 slot0 DATA bit0.
- 0x35D8B0–0x35D8BC: CLOCK low for next slot; subsequent slots sampled after CLOCK high.

## Implication
The two streams have different release-to-sample instruction windows. Stream 1 releases earlier and is sampled first; stream 2 releases later and is sampled later. These facts do **not** establish which stream is physically wired to GP2040-CE or the actual elapsed microseconds; the intervening helper durations and physical wiring must be resolved.

Test16 waits for DATA high after host LOAD release before asserting slot0 (physical 3P/R1/RB / HK). Test23 only moved timestamp bookkeeping after that assertion and HW did not improve. The first-bit timing margin remains open, but moving more arbitrary instructions is not a justified fix.

## Next offline gates
1. Resolve physical external connector DATA to stream1 (B15) vs stream2 (L0) from wiring evidence.
2. Decode the three helper calls in the slot0 window to bound time.
3. Obtain Test16 compiled ARM Thumb disassembly and count detection-to-OE-write instructions.
4. Only then design a single-slot change, preserving Test16's successful directional clock train.

No UF2 built. Test16 untouched.
