#!/usr/bin/env bash
set -euo pipefail

# Audit a linked XGO external-core ELF before it is converted to XGOC.
#
# This intentionally checks properties that are easy to lose when changing
# compiler/toolchain versions: fixed HC15xx ABI, fixed load entry, no dynamic
# loader dependency, no unresolved symbols, and visibility into any remaining
# $gp-relative code.

ELF=${1:?usage: audit_external_elf.sh <core.elf>}
READELF=${READELF:-llvm-readelf}
NM=${NM:-llvm-nm}
OBJDUMP=${OBJDUMP:-llvm-objdump}

fail() {
    echo "ERROR: $*" >&2
    exit 1
}

[[ -f "$ELF" ]] || fail "ELF not found: $ELF"

header=$("$READELF" -h "$ELF")

grep -q 'Class:.*ELF32' <<<"$header" || fail 'core is not ELF32'
grep -q 'Data:.*little endian' <<<"$header" || fail 'core is not little-endian'
grep -q 'Machine:.*MIPS' <<<"$header" || fail 'core is not MIPS'

entry_hex=$(awk '/Entry point address:/ { print $4 }' <<<"$header")
[[ "$entry_hex" == "0x87000000" ]] || \
    fail "ELF entry is $entry_hex, expected 0x87000000"

sections=$("$READELF" -S "$ELF")
for bad in '.interp' '.dynamic' '.dynsym' '.rel.dyn' '.rela.dyn' '.plt' '.got.plt'; do
    if grep -Eq "[[:space:]]${bad//./\\.}([[:space:]]|$)" <<<"$sections"; then
        fail "unexpected dynamic/PIC section present: $bad"
    fi
done

# A final static core must not leave unresolved symbols for a runtime loader.
undefined=$("$NM" -u "$ELF" || true)
if [[ -n "$undefined" ]]; then
    echo "$undefined" >&2
    fail 'linked core still contains undefined symbols'
fi

entry_sym=$("$NM" -n "$ELF" | awk '$3 == "__core_entry__" { print "0x" $1; exit }')
[[ "$entry_sym" == "0x87000000" ]] || \
    fail "__core_entry__ is ${entry_sym:-missing}, expected 0x87000000"

# -G0/-mno-abicalls/-fno-pic should make the XGO-specific bridge independent of
# a conventional small-data ABI. Prebuilt static runtime libraries may still
# contain legitimate $gp users, however, so this is reported rather than made
# fatal until the exact HC15xx newlib archive is under audit.
disasm=$("$OBJDUMP" -d --no-show-raw-insn "$ELF")
gp_refs=$(grep -Ec '\$gp|\(%gp\)' <<<"$disasm" || true)

sdata=$(grep -E '[[:space:]]\.sdata([[:space:]]|$)' <<<"$sections" || true)
sbss=$(grep -E '[[:space:]]\.sbss([[:space:]]|$)' <<<"$sections" || true)
got=$(grep -E '[[:space:]]\.got([[:space:]]|$)' <<<"$sections" || true)

printf 'XGO external-core ELF audit: PASS\n'
printf '  file:          %s\n' "$ELF"
printf '  entry:         %s\n' "$entry_hex"
printf '  unresolved:    0\n'
printf '  gp references: %s (review if non-zero)\n' "$gp_refs"
[[ -z "$sdata" ]] || printf '  note: .sdata present\n'
[[ -z "$sbss" ]] || printf '  note: .sbss present\n'
[[ -z "$got" ]] || printf '  note: .got present\n'
