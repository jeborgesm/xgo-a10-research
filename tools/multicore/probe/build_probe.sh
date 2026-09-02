#!/usr/bin/env bash
set -euo pipefail

CLANG=${CLANG:-clang}
LD_LLD=${LD_LLD:-ld.lld}
OBJCOPY=${OBJCOPY:-llvm-objcopy}
NM=${NM:-llvm-nm}
PYTHON=${PYTHON:-python3}

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
rm -f xgo_probe_core.o xgo_probe_core.elf core_87000000 core.xgc

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

sym_addr() {
  local name=$1
  local value
  value=$("$NM" -n xgo_probe_core.elf | awk -v n="$name" '$3 == n { print "0x" $1; exit }')
  if [[ -z "$value" ]]; then
    echo "ERROR: missing linker symbol $name" >&2
    exit 1
  fi
  printf '%s' "$value"
}

image_start=$(sym_addr __image_start)
file_end=$(sym_addr __file_end)
image_end=$(sym_addr __image_end)
entry=$(sym_addr __start)

payload_size=$(stat -c %s core_87000000)
expected_payload_size=$((file_end - image_start))
memory_size=$((image_end - image_start))
entry_offset=$((entry - image_start))

if (( payload_size != expected_payload_size )); then
  printf 'ERROR: raw payload size %d != linker file span %d\n' \
    "$payload_size" "$expected_payload_size" >&2
  exit 1
fi

"$PYTHON" pack_xgoc.py core_87000000 core.xgc \
  --entry-offset "$entry_offset" \
  --memory-size "$memory_size"

loader_size=$(stat -c %s xgo_probe_loader.bin)
container_size=$(stat -c %s core.xgc)
loader_capacity=$((0x2180 - 0x1500))

printf 'loader: %d bytes / %d available\n' "$loader_size" "$loader_capacity"
printf 'raw probe core: %d bytes\n' "$payload_size"
printf 'XGOC probe core: %d bytes\n' "$container_size"
printf 'runtime image: %d bytes (BSS/runtime-only %d)\n' \
  "$memory_size" "$((memory_size - payload_size))"

if (( loader_size > loader_capacity )); then
  echo 'ERROR: loader exceeds XGO 0x1500..0x217f injection window' >&2
  exit 1
fi

# The address/window checks are authoritative. Exact code size may vary with
# compiler version; the validated XGOC loader is intentionally allowed to grow
# beyond the original ~402-byte raw-blob probe while remaining below 3200 bytes.
