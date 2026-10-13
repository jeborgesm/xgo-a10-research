# XGO host serial timing: CP0 delay helper audit (2026-10-12)

Evidence: supplied `XGoAnalisis.zip` member `bios/bisrv.asd`, 12,768,452 bytes; raw little-endian MIPS32 instructions at offsets below. No firmware changes.

## BIN: repeated-slot phase
- `0x35D8B0` GPIO read; `0x35D8B8` AND with `0xff7f`; `0x35D8BC` GPIO write: CLOCK bit 7 LOW.
- `0x35D8C8` `jal 0x30fed0`, delay slot `addiu a0,zero,2`.
- `0x35D8D0` helper `jal 0x2e0750`.
- `0x35D8D8` GPIO read; `0x35D8DC` mask with `0xff7f`; `0x35D8E0` OR `0x80`; `0x35D8E4` GPIO write: CLOCK HIGH.
- `0x35D8F0` GPIO read and `0x35D8F4` mask `0x8000`: DATA stream 1.
- `0x35D908` GPIO read and `0x35D90C` mask `0x0001`: DATA stream 2.
- Repeated-slot sample thus occurs **after rising CLOCK**, not during low. Slot0 has distinct initialization and delay argument 4.

## BIN: delay helper structure, new result
- `0x30FEE0` `jal 0x49fc8` with `a0` saved to `s0` in delay slot.
- `0x49FC8` instruction `0x40024800` is `mfc0 v0,$9` (MIPS CP0 Count).
- `0x30FEF0` `lui v0,0x001e`; `0x30FEF4` `ori v0,v0,0x8480` -> constant **2,000,000**.
- `0x30FEF8` unsigned divide of gp-relative value (from `lw v1,-4000(gp)`) by 2,000,000; `0x30FF00` `mflo v1`; `0x30FF0C` multiply quotient by delay argument; `0x30FF14` obtains CP0 Count again; `0x30FF20`–`0x30FF48` loop until sufficient Count delta.
- This is a **counter-based delay**, not a fixed number of NOPs. Actual unit depends on the gp-relative clock-frequency value and CP0 Count scaling; the argument `2` alone is insufficient to establish a measured 2us low period.

## Engineering implication (INF)
The RP2040 must detect CLOCK-low, change native PHY DATA output-enable and settle before the host CLOCK-high DATA reads. This host order disproves the earlier hypothesis of DATA sampled early within low phase. However, there may still be insufficient setup margin if RP2040 update is delayed by polling, bus latency or scheduling. Actual host Count clock, GPIO access latency, and compiled RP2040 response latency remain OPEN.

## Immediate next gates
1. Recover the gp-relative frequency value and CP0 Count scale for the 2,000,000 divisor.
2. Audit first-slot LOAD-to-read ordering separately.
3. Independently validate all twelve GP2040 physical-button-to-serial-slot mappings.
4. Disassemble compiled Caveman and Test16 to compare worst-case CLOCK falling edge to DATA OE write, without substituting source-code similarity for cycle measurement.

Protected Test14 unchanged; no UF2 authorized.
