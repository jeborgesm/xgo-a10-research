#!/usr/bin/env bash
set -euo pipefail
CLANG=${CLANG:-clang}
LD_LLD=${LD_LLD:-ld.lld}
OBJCOPY=${OBJCOPY:-llvm-objcopy}
OBJDUMP=${OBJDUMP:-llvm-objdump}
READELF=${READELF:-readelf}
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)

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

cd "$SCRIPT_DIR"
rm -f xgo_cps1_loader.o xgo_cps1_init.o xgo_cps1_loader.elf xgo_cps1_loader.bin
"$CLANG" "${CFLAGS[@]}" -c xgo_cps1_loader.c -o xgo_cps1_loader.o
"$CLANG" "${CFLAGS[@]}" -c xgo_cps1_init.s -o xgo_cps1_init.o
"$LD_LLD" -m elf32ltsmip -T xgo_cps1_loader.ld   xgo_cps1_init.o xgo_cps1_loader.o -o xgo_cps1_loader.elf

if "$OBJDUMP" -d --no-show-raw-insn xgo_cps1_loader.elf | grep -q '\$gp'; then
  echo 'ERROR: native CPS1 loader contains $gp-relative code' >&2
  exit 1
fi
if "$READELF" -S xgo_cps1_loader.elf | grep -Eq '[[:space:]]\.(got|sdata|sbss)([[:space:]]|$)'; then
  echo 'ERROR: native CPS1 loader contains GOT/small-data sections' >&2
  exit 1
fi
"$OBJCOPY" -O binary -j .text -j .rodata -j .data xgo_cps1_loader.elf xgo_cps1_loader.bin
size=$(stat -c %s xgo_cps1_loader.bin)
cap=$((0x3000 - 0x2780))
printf 'native CPS1 loader: %d bytes / %d available\n' "$size" "$cap"
(( size <= cap ))
printf 'entry address: 0x80002780\n'
printf 'fallback:      stock run_fba @ 0x8035e4b4\n'
printf 'patch site:    0x80360e00 / ASD 0x00360e00\n'
printf 'gp refs:       0\n'
