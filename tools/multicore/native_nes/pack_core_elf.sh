#!/usr/bin/env bash
set -euo pipefail

# Convert a fully linked XGO external-core ELF into the XGOC container consumed
# by xgo_nes_loader.c. The ELF remains the authoritative source for entry and
# runtime extents; the raw payload may be shorter than __file_end because
# objcopy is allowed to trim trailing alignment bytes.

if [[ $# -lt 2 || $# -gt 3 ]]; then
  echo "usage: $0 <core.elf> <core.xgc> [pack_xgoc.py]" >&2
  exit 2
fi

ELF=$1
OUT=$2
PACKER=${3:-../probe/pack_xgoc.py}

NM=${NM:-mipsel-linux-gnu-nm}
READELF=${READELF:-mipsel-linux-gnu-readelf}
OBJCOPY=${OBJCOPY:-mipsel-linux-gnu-objcopy}
PYTHON=${PYTHON:-python3}

CORE_BASE=$((0x87000000))
CORE_LIMIT=$((0x87cdae00))
RAW=$(mktemp)
trap 'rm -f "$RAW"' EXIT

sym_addr() {
  local name=$1
  local value
  value=$("$NM" -n "$ELF" | awk -v n="$name" '$3 == n { print "0x" $1; exit }')
  if [[ -z "$value" ]]; then
    echo "ERROR: missing ELF symbol $name" >&2
    exit 1
  fi
  printf '%s' "$value"
}

entry=$(sym_addr __core_entry__)
image_start=$(sym_addr __image_start)
file_end=$(sym_addr __file_end)
image_end=$(sym_addr __image_end)

if (( entry != CORE_BASE || image_start != CORE_BASE )); then
  printf 'ERROR: core entry/image start must be 0x%08x (entry=%#x start=%#x)\n' \
    "$CORE_BASE" "$entry" "$image_start" >&2
  exit 1
fi
if (( file_end < image_start || image_end < file_end || image_end > CORE_LIMIT )); then
  echo 'ERROR: inconsistent or out-of-range XGO core ELF extents' >&2
  exit 1
fi

# A production external core must be static. Reject dynamic loader/relocation
# sections rather than relying on the XGO loader to understand them.
if "$READELF" -S "$ELF" | grep -Eq '\.(interp|dynamic|dynsym|dynstr|rel\.dyn|rela\.dyn)([[:space:]]|$)'; then
  echo 'ERROR: dynamic-linker sections found in XGO external core' >&2
  exit 1
fi

if "$NM" -u "$ELF" | grep -q .; then
  echo 'ERROR: unresolved symbols remain in XGO external core:' >&2
  "$NM" -u "$ELF" >&2
  exit 1
fi

"$OBJCOPY" -O binary \
  -j .init -j .text -j .fini -j .rodata \
  -j .eh_frame_hdr -j .eh_frame -j .gcc_except_table \
  -j .init_array -j .fini_array -j .ctors -j .dtors \
  -j .data -j .got.plt -j .got -j .sdata \
  "$ELF" "$RAW"

payload_size=$(stat -c %s "$RAW")
file_span=$((file_end - image_start))
memory_size=$((image_end - image_start))

if (( payload_size == 0 || payload_size > file_span )); then
  printf 'ERROR: raw payload %d is outside linker file span %d\n' \
    "$payload_size" "$file_span" >&2
  exit 1
fi

"$PYTHON" "$PACKER" "$RAW" "$OUT" \
  --entry-offset 0 \
  --memory-size "$memory_size"

printf 'XGO production core packed\n'
printf '  ELF entry:      0x%08x\n' "$entry"
printf '  payload:        %d bytes\n' "$payload_size"
printf '  file span:      %d bytes\n' "$file_span"
printf '  runtime image:  %d bytes\n' "$memory_size"
printf '  BSS/zero tail:  %d bytes\n' "$((memory_size - payload_size))"
printf '  upper end:      0x%08x\n' "$image_end"
printf '  output:         %s\n' "$OUT"
