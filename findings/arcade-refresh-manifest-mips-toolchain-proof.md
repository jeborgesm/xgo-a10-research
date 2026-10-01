# Arcade manifest iterator — compiler/toolchain proof

Date: 2026-09-24
Branch: research-arcade-refresh-four-family
Status: TOOLCHAIN CLOSED / SOURCE BUILD VIABLE

The local construction environment was tested directly with the manifest
validator logic.

Compiler:
clang --target=mipsel-none-elf -march=mips32 -mabi=32 -mno-abicalls
-fno-pic -ffreestanding -fno-builtin -Os

Result:
- emitted ELF32 little-endian MIPS object successfully;
- llvm-objdump decoded the generated MIPS32 instructions successfully;
- generated validator is position-independent with respect to external data
  because it has no GOT/$gp dependency;
- no libc dependency was introduced.

The first validator-only build is 0x120 bytes of text before any file-reader
state machine is added. This leaves ample room for a bounded reader without
requiring firmware cave expansion because the Arcade catalog helper is an
external executable.

Important: this proves the build path, not the final iterator ABI. The final
object must still bind only stock file callbacks already proven in the golden
helper and must be linked/audited for the chosen helper address before use.
