# Arcade Refresh — GBA helper direct binary audit

Date: 2026-09-24
Branch: research-arcade-refresh-four-family
Status: BIN-CLOSED DISCOVERY FRONT END

Exact audited binary:
- final HW-proven GBA catalog.xgc
- size 2642
- SHA-256 db7c1173f5b98adb3506b2676a035ba6e54b35a4391709cbbcd7ad92b983cbc6

## Literal table

+0x09E4 /mnt/sda1/Resources/vfnet.tax
+0x0A02 /mnt/sda1/Resources/htuiw.nec
+0x0A20 /mnt/sda1/Resources/sppnp.bvs
+0x0A3E /mnt/sda1/GBA

## Discovery front end

The final GBA helper still uses the Test74/Test75 directory-enumeration grammar.

- +0x02EC loads DIR_OPEN callback 0x807D40C4
- +0x02F8 passes root literal +0x0A3E
- +0x0304 loads DIR_NEXT callback 0x807D4124
- directory workspace begins in 0x872A....
- +0x03D8..+0x0478 performs the case-insensitive four-character .zgb suffix test
- +0x047C onward enters exact slot0 comparison/stable missing-item collection.

Exact suffix immediates:
+0x03E4 '.' 0x2E
+0x0414 'z' 0x7A
+0x0444 'g' 0x67
+0x0470 'b' 0x62

This proves the current GBA helper cannot be specialized to four Arcade
families by changing only root/triplet strings: scanning /ARCADE would mix all
.zfb families.

## Implementation consequence

Preserve the helper from +0x047C onward as the semantic catalog ancestor.
Replace only +0x02E4..+0x0478 discovery/enumeration with a bounded transient
family-list reader that presents exact .zfb names to the existing comparison
and append path.

This is substantially narrower than replacing the catalog engine.

The new discovery code may be source-built because the original directory
enumerator cannot express family identity on the shared /ARCADE namespace.
All catalog parse/compare/append semantics after the handoff remain inherited
from the HW-proven GBA helper.

No cache write is authorized for Arcade until its exact target is proven.
