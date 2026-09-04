#!/usr/bin/env bash
set -euo pipefail

CLANG=${CLANG:-clang}
LD_LLD=${LD_LLD:-ld.lld}
OBJCOPY=${OBJCOPY:-llvm-objcopy}
OBJDUMP=${OBJDUMP:-llvm-objdump}
READELF=${READELF:-readelf}

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
PROBE_DIR="$SCRIPT_DIR/../probe"

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
rm -f xgo_snes_loader.o xgo_snes_init.o xgo_snes_loader.elf xgo_snes_loader.bin

"$CLANG" "${CFLAGS[@]}" -c xgo_snes_loader.c -o xgo_snes_loader.o
"$CLANG" "${CFLAGS[@]}" -c "$PROBE_DIR/xgo_probe_init.s" -o xgo_snes_init.o

"$LD_LLD" -m elf32ltsmip -T "$PROBE_DIR/xgo_probe_loader.ld" \
  xgo_snes_init.o xgo_snes_loader.o -o xgo_snes_loader.elf

# Injected loader code has no private MIPS $gp initialization. Treat any GP
# reference or surviving GOT/small-data section as a hard build failure.
if "$OBJDUMP" -d --no-show-raw-insn xgo_snes_loader.elf | grep -q '\$gp'; then
  echo 'ERROR: native SNES loader contains $gp-relative code' >&2
  exit 1
fi

if "$READELF" -S xgo_snes_loader.elf | \
   grep -Eq '[[:space:]]\.(got|sdata|sbss)([[:space:]]|$)'; then
  echo 'ERROR: native SNES loader contains GOT/small-data sections' >&2
  exit 1
fi

"$OBJCOPY" -O binary -j .text -j .rodata -j .data \
  xgo_snes_loader.elf xgo_snes_loader.bin

loader_size=$(stat -c %s xgo_snes_loader.bin)
loader_capacity=$((0x2180 - 0x1500))

printf 'native SNES loader: %d bytes / %d available\n' \
  "$loader_size" "$loader_capacity"

if (( loader_size > loader_capacity )); then
  echo 'ERROR: native SNES loader exceeds XGO injection cave' >&2
  exit 1
fi

printf 'entry address: 0x80001500\n'
printf 'fallback:      stock run_snes @ 0x8035f9d8\n'
printf 'patch site:    0x80360e40 / ASD 0x00360e40\n'
printf 'gp refs:       0\n'
