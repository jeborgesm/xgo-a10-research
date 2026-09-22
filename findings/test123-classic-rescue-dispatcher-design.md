# Test123 CLASSIC rescue — exact dispatcher patch design

Date: 2026-09-21
Status: BIN-closed patch design; implementation source next.

Protected parent: HW-positive Test122.

## Exact current dispatcher

At `0x80A386EC`, after explicit checks for command 0 and 1, Test122 unconditionally jumps to MD at `0x80A387AC`.

## Minimal repair

Replace only the current unconditional else-MD jump at `0x80A386EC` with a jump to a small dispatcher extension in the verified free tail at `0x80A38840`.

Extension semantics:

```
command 2 -> j 0x80A387AC          # preserve exact MD path
command 7 -> unwind selective-dispatch frame
             s5 = 0
             j 0x80A38000          # protected CLASSIC continuation
command 3..6 -> unwind selective-dispatch frame
                j 0x807DB6EC       # native No New Games / safe non-mutating return
```

The extension must restore the selective dispatcher prologue before leaving it:
`ra <- 0x1C(sp)`, `s0 <- 0x18(sp)`, `sp += 0x20`.

This is required because `0x80A38000` is a continuation under the native Refresh frame, not a callee of the selective dispatcher.

## Why commands 3..6 return No New Games for Test123

They are intentionally not implemented in this candidate. The purpose is to stop the dangerous/misleading alias to MD while changing only CLASSIC. Returning through the existing native no-change status path is non-mutating and keeps the frontend lifecycle valid. Their real GB/GBC/GBA/Arcade adapters follow after CLASSIC is hardware-restored.

## Protected surfaces

Test123 must leave byte-identical:
- Test122 selector renderer/input/B behavior;
- Test122 state-14 selector-compositor suppression;
- FC helper path at 0x80A386F4;
- SFC helper path at 0x80A38750;
- MD helper path at 0x80A387AC;
- CLASSIC bootstrap 0x80A38000..0x80A3823F;
- native Refresh frame/workspace creation through 0x807DB678;
- native status/epilogue.

Only dispatcher jump, new extension, and LCFG seal may differ.

## Runtime package gate

Canonical Test72 helper identity is known (`9f932f35...`), but the binary helper is not currently present in the working container. Do not fabricate it. Firmware candidate can be built deterministically now, but a self-contained hardware ZIP must either include the exact helper from the artifact vault/local Test72 package or explicitly rely on the already-installed matching SD helper after hash verification.

## Candidate emitted

Firmware-only Test123 candidate built from exact HW-positive Test122:
- firmware SHA-256: `7becafa3372e7b511bd8f05d0f378ca6397d72c6cc5c075f2e0d650cba2a86b5`
- LCFG CRC-32/MPEG-2: `0x91CA4950`
- ZIP SHA-256: `528347bd7e7005074ff9fc1b459d0f9ec7499f519fcecd02b0d9aa96c7a39dd2`

Exact firmware delta beyond LCFG seal:
- `0x80A386EC`: inherited else->MD jump replaced with extension jump;
- `0x80A38840`: 76-byte extension implementing command 2 -> unchanged MD, command 7 -> unwind + CLASSIC continuation, commands 3..6 -> unwind + native No New Games.

Assertions passed:
- exact Test122 parent SHA;
- helper cave zero/free;
- FC/SFC/MD bodies unchanged;
- `0x80A38000..0x80A3823F` CLASSIC bootstrap byte-identical;
- independent LCFG CRC recomputation matches stored CRC.

Packaging limitation is deliberate: ZIP contains firmware only because the canonical Test72 `CLASSIC/refresh.xgc` binary is not present in the current working container. Hardware test is valid only if SD already contains helper SHA `9f932f35b1627bb8a4a7427831454e3c5dd854972231c1062316a814ada8723f`, or after that exact helper is restored from the canonical Test72 artifact.
