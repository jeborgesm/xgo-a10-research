# Original bisrv.asd scanner evidence — HP/MK follow-up (2026-10-14)

Offline source: user-supplied `XGoAnalisis.zip` -> `bios/bisrv.asd`, 12,768,452 bytes. No modifications. MIPS32 little-endian code window at file offset 0x35d770, virtual 0x8035d770.

## Newly revisited instruction evidence

- 0x8035d844 `sw t6,0(s1)`: B15 direction release (s1 = 0xb8800358).
- 0x8035d848 `jal 0x802e0778`, 0x8035d850 `jal 0x802e0750`.
- 0x8035d864 `sw t3,0(s0)`: L0 direction release (s0 = 0xb8800058).
- 0x8035d868 `jal 0x802e0778`.
- 0x8035d870 `lw t2,0(s4)`: B15 DATA0 first sample (s4 = 0xb8800350).
- 0x8035d874 `andi t1,t2,0x8000`: pressed if zero.
- 0x8035d890 `lw t9,0(s1)`: L0 DATA1 first sample (s1 updated to 0xb8800050).
- 0x8035d894 `andi s3,t9,0x0001`.
- 0x8035d8a8 `jal 0x802e0750`; 0x8035d8b0 `lw t1,0(s2)`; 0x8035d8bc `sw t0,0(s2)` (subsequent GPIO transition); 0x8035d8c0 `jal 0x802e0778`; 0x8035d8c8 `jal 0x8030fed0` (requires separate classification); 0x8035d8d0 `jal 0x802e0750`.
- 0x8035d8f0 `lw v0,0(s4)`, 0x8035d8f4 `andi a1,v0,0x8000`: later B15 sample.
- 0x8035d908 `lw t5,0(s1)`, 0x8035d90c `andi t4,t5,0x0001`: later L0 sample.

The B15 and L0 input reads are interleaved, with multiple helper calls and GPIO operations. **Do not equate a simple CLOCK falling edge with a proven immediate sample**, and do not infer HP or MK serial slot identities from game attack labels.

## Hypotheses and next checks

1. Determine exact adapter stream (B15 versus L0) and the host scanner's full per-slot GPIO/sample sequence.
2. Resolve helper calls at 0x802e0778, 0x802e0750 and any clock-related calls before claiming timing margins.
3. Ground actual SFII HP/MK -> GP2040-CE physical input -> serial slot mapping using validated mapping evidence.
4. Distinguish wrong sampled bit from game-side repeat semantics; Test29 slowed repeats but did not change mixing.

**Hardware state:** Test28 protected HW PASS for HK, no Ken bot, LED menu; Test29 HW negative for held punch mixing and slowed repeat (~2s vs ~1s). No Test30 candidate authorized by this evidence yet. Original firmware unchanged.
