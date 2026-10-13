# DIY ELF instruction evidence / Test17 gate — 2026-10-12

Local evidence: uploaded `/mnt/data/xgo_live_controller.elf`, disassembled with `llvm-objdump -d --start-address=0x100004d0 --stop-address=0x10000580`.

## Proven instruction sequence

- `0x100004F2 ldr r3,[r0,#0x7c]`: sample USB PHY direct register.
- `0x100004F4 tst r3,r1`; `0x100004F6 bne 0x100004EA`: wait for CLOCK low, with loop timeout at `0x100004EA..F0`.
- `0x100004F8 mov r3,r12`; `0x100004FA lsrs r3,r5`; `0x100004FC tst r6,r3`; `0x100004FE beq 0x10000566`: select current slot bit.
- One DATA write: `0x10000504 str r4,[r3,#0x7c]`; alternative: `0x1000056A str r4,[r3,#0x7c]`. Different register base addresses and/or values must be established from preceding register setup before labeling either sink/release.
- `0x10000512..16` waits for CLOCK high, then `0x10000518 adds r5,#1` and `0x1000051A cmp r5,#12` loops for next slot.
- Timeout compares against `#12` at `0x100004EE` and `0x1000050E`; timer is a hardware register at `[r2,#0x28]`. **Do not infer this is a 12us wall-clock timeout without establishing timer register frequency.**

## Key implications

The uploaded DIY ELF proves a compact direct-PHY clock/bit/write loop; it does not prove the source GPIO wiring matches the user's Pico diagram, nor that this ELF is identical to the archived Caveman UF2. Test17's C++ loop may compile differently; compiled responder comparison is still a release gate.

Local environment: `llvm-objdump` and `clang` present, `arm-none-eabi-gcc` and Pico SDK absent, outbound GitHub clone unavailable. Test16 local ZIP includes `README-DO-NOT-FLASH.txt`. No Test17 build or hardware validation was performed.

## Caution on the direct-input proposal

The GPIO model proves 4096 logical combinations only. GP2040-CE's Web Config can expose mappings and turbo; bypassing the processed state may change intended functionality. Treat Test17 as a diagnostic variant until configuration semantics and GPIO electrical initialization are audited.
