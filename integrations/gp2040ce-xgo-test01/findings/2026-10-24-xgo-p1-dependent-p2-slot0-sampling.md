# Original XGO P2 slot-0 sampling is conditional on P1 first-bit state

**2026-10-24 • BIN result from the original attached XGO executable • no firmware modified**

## Scope and input provenance

Original user-supplied `XGoAnalisis.zip`, member `bios/bisrv.asd`, size 12,768,452 bytes, SHA-256 `869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf`. Independently read byte-level instructions and verified the same opcode words with [the stdlib-only verifier](../tests/verify_original_xgo_slot0_p1_path.py). This is **BIN** for the original host scanner, not new XGO HW or an analog voltage capture.

The protected **user-tested transparent GP2040-CE firmware** SHA `94ea7228c774a67e8252e7e09d94938530e5d74572d985332e6840ae09fe8b84` remains the good controller baseline. The **paged-OLED trial** SHA `5dcc28132ca54293a3d27dc2a452269bc47a1e7f141bd49c2c7e296918071b5b` remains UNFLASHED.

## Exact decoded conditional path

| Original runtime address | MIPS32 instruction/role |
|---|---|
| `0x8035D870` | `lw t2,0(s4)`: sample P1 first serial bit GPIO B15 |
| `0x8035D874` | `andi t1,t2,0x8000`: test active-low P1 slot0 |
| `0x8035D878` | `bne t1,zero,0x8035D890`: P1 HIGH/released takes branch directly to P2 read |
| `0x8035D87C` | `ori s1,s3,0x50`: branch delay instruction always executes |
| `0x8035D880–0x8035D88C` | Four **additional** instructions when P1 LOW/pressed: load P1 raw state, OR P1 first bit, store state, restore address register |
| `0x8035D890` | `lw t9,0(s1)`: sample P2 slot0 GPIO L0 |
| `0x8035D894` | `andi s3,t9,1`: test active-low P2 slot0 |
| `0x8035D898–0x8035D8A4` | branch/store P2 first bit if LOW |
| `0x8035D8B0–0x8035D8BC` | prepare and write the first shared CLOCK LOW, **after** both slot0 GPIO reads |

**New structural result (BIN):** the host does **not** sample P1 and P2 first bits simultaneously. With P1 released (the typical idle case), it reads P2 on the shorter branch-taken path. If P1's first serial bit is LOW, the BNE falls through and **four additional MIPS instructions**, including a load/store, execute before P2 is sampled. The branch delay slot executes in both paths. This changes the host's P2 first-bit sampling *instruction path* depending on P1's level. Actual elapsed cycles are NOT measured.

This augments the already-established finding that P2 slot0 is sampled *before* any first CLOCK LOW. It does not change the established twelve-slot format, controller-transparency requirement or source mapping.

## Why this matters — bounded inference, NOT proof of root cause

The historical P0 digital trace places DATA/load release only approximately 0.9–1.3 microseconds before first CLOCK falling. Under a **hypothetical** slowly recovering P2 DATA voltage (unmeasured on current Frankie V2 Jr), the shorter P1-idle route could sample P2 before it reaches a valid HIGH. The longer P1-pressed route could sample later and therefore potentially see HIGH. This is a **falsifiable timing discriminator**, but the extra 4 instructions have no established nanosecond duration and are not sufficient evidence that this is causing intermittent Contra JUMP.

The observed Contra jump **does not uniquely identify P2 slot0**: the embedded FC default can map R/slot0, X/slot2 and A/slot4 to JUMP and user per-ROM `.kmp` overrides are not yet established. P3 passive observations used a different cable. SFII LP triple-hit and missed-hit may have different causes. No claim of causality is promoted beyond BIN/INF.

## Follow-up boundaries

1. Keep transparent driver/OLED, user SD `bisrv.asd`, Frankie, physical mappings and protected hashes unchanged.
2. A future timing model can include **both P1-first-bit branch paths** and a parameterized P2 DATA transition. It must label transition/rise-time and MIPS instruction-cycle assumptions as MODEL, not captured hardware.
3. If a safe, justified physical discriminator is eventually needed, vary P1 slot0 state while observing P2 false R behavior, with P1 gameplay side effects controlled. **No new hardware test is requested or authorized by this report.**
4. Continue independent clock/frame and Core0-sampling investigations; do not roll this BIN finding into an unproven universal ghost-jump fix.

**Verification command**, using private/local original archive only:

```bash
python3 integrations/gp2040ce-xgo-test01/tests/verify_original_xgo_slot0_p1_path.py /path/to/XGoAnalisis.zip
```

**No firmware candidate, hardware flash, PHY pull-up change, keymap change, or wire modification was produced in this checkpoint.**
