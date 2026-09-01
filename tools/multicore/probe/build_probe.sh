#!/usr/bin/env bash
set -euo pipefail

CLANG=${CLANG:-clang}
LD_LLD=${LD_LLD:-ld.lld}
OBJCOPY=${OBJCOPY:-llvm-objcopy}

CFLAGS=(
  --target=mipsel-none-elf
  -march=mips32
  -msoft-float
  -G0
  -mno-abicalls
  -fno-pic
  -ffreestanding
  -fno-builtin
  -Os
)

rm -f xgo_probe_loader.o xgo_probe_init.o xgo_probe_loader.elf xgo_probe_loader.bin
rm -f xgo_probe_core.o xgo_probe_core.elf core_87000000

"$CLANG" "${CFLAGS[@]}" -c xgo_probe_loader.c -o xgo_probe_loader.o
"$CLANG" "${CFLAGS[@]}" -c xgo_probe_init.s -o xgo_probe_init.o
"$LD_LLD" -m elf32ltsmip -T xgo_probe_loader.ld \
  xgo_probe_init.o xgo_probe_loader.o -o xgo_probe_loader.elf
"$OBJCOPY" -O binary -j .text -j .rodata -j .data \
  xgo_probe_loader.elf xgo_probe_loader.bin

"$CLANG" "${CFLAGS[@]}" -c xgo_probe_core.c -o xgo_probe_core.o
"$LD_LLD" -m elf32ltsmip -T xgo_probe_core.ld \
  xgo_probe_core.o -o xgo_probe_core.elf
"$OBJCOPY" -O binary -j .text -j .rodata -j .data \
  xgo_probe_core.elf core_87000000

loader_size=$(stat -c %s xgo_probe_loader.bin)
core_size=$(stat -c %s core_87000000)
loader_capacity=$((0x2180 - 0x1500))

printf 'loader: %d bytes / %d available\n' "$loader_size" "$loader_capacity"
printf 'probe core: %d bytes\n' "$core_size"

if (( loader_size > loader_capacity )); then
  echo 'ERROR: loader exceeds XGO 0x1500..0x217f injection window' >&2
  exit 1
fi

# Current known-good reference sizes with LLVM 17 in the research environment:
#   loader ~= 402 bytes
#   probe  ~= 472 bytes
# Exact size may vary slightly by compiler version; the address/window checks
# are the authoritative constraints.
