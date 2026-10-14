# HK slot-0: original XGO host scanner instruction evidence

Source: user-supplied `XGoAnalisis.zip` -> `bios/bisrv.asd`. MIPS32 little-endian words at file offset `0x35d770`, mapped virtual address `0x8035d770`. Decoded offline from original words; no firmware changed.

## Release and first sample, original words

```text
8035d834 8e2f0000 lw   t7,0(s1)         ; B direction register 0xb8800358
8035d838 3c19ffff lui  t9,0xffff
8035d83c 37387fff ori  t8,t9,0x7fff
8035d840 01f87024 and  t6,t7,t8
8035d844 ae2e0000 sw   t6,0(s1)         ; B15 DATA0 -> input
8035d848 0c0b81de jal  0x802e0778      ; call (uncategorized here)
8035d84c 00000000 nop
8035d850 0c0b81d4 jal  0x802e0750      ; call (uncategorized here)
8035d854 00000000 nop
8035d858 8e0c0000 lw   t4,0(s0)         ; L direction register 0xb8800058
8035d85c 240dfffe addiu t5,zero,-2
8035d860 018d5824 and  t3,t4,t5
8035d864 ae0b0000 sw   t3,0(s0)         ; L0 DATA1 -> input
8035d868 0c0b81de jal  0x802e0778
8035d86c 00000000 nop
8035d870 8e8a0000 lw   t2,0(s4)         ; B15 DATA0 first read, 0xb8800350
8035d874 31498000 andi t1,t2,0x8000
8035d878 15200005 bne  t1,zero,...      ; zero => pressed
...
8035d890 8e390000 lw   t9,0(s1)         ; L0 DATA1 first read, 0xb8800050
8035d894 33330001 andi s3,t9,0x0001
```

Addresses in jal lines above include high PC region; 26-bit target encoding alone displays 0x002e..., full MIPS jump address is 0x802e....

## Consequences

1. The previous description 'immediately samples' means **no explicit multi-microsecond settle delay**; it does NOT mean zero instructions between release and sample. DATA0 (B15) is released first and has two helper calls and the L0 direction update before its sample. DATA1 (L0) is released last and has one helper call before the B15 sample, and additional instructions before its own sample.
2. The two DATA streams have **different release-to-first-sample windows**. Therefore identifying which line the RP2040 actually emulates is critical before selecting a timing fix.
3. Existing Test16-derived `wait_data(true)` then `data_sink()` remains a plausible turnaround race, especially for the stream released last, but the exact time budget cannot be stated until helper call 0x802e0778 is classified and CPU/bus timing is known.
4. These instructions establish no mapping from serial R to SFII Medium Punch. Do not conflate missing HK with MP substitution.

## Next
Disassemble helper 0x802e0778 and 0x802e0750, then trace stream-to-player mapping; only then design a minimal controller-only test.
