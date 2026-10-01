# Arcade catalog helper — literal relocation gate

Date: 2026-09-24
Branch: research-arcade-refresh-four-family
Status: BUILD GUARD ACTIVE; no unsafe binary emitted

The first binary builder is now committed at
tools/arcade_refresh/build_arcade_catalog_helpers.py.

It requires the exact final GBA helper by both size (2642) and SHA-256
db7c1173f5b98adb3506b2676a035ba6e54b35a4391709cbbcd7ad92b983cbc6.

The direct specialization exposed a concrete layout constraint:

- the three GBA catalog literals occupy the known tail string table and can be
  specialized only within their existing capacities;
- the family staging root
  /mnt/sda1/ARCADE/<FAMILY>/.refresh-set
  cannot fit the original /mnt/sda1/GBA literal slot.

The builder therefore intentionally refuses to emit a partially patched helper.

This is not an architectural blocker. The GBC/GBA golden propagation already
established a proven pattern for relocating longer literals into unused helper
tail space and retargeting every code reference to the new addresses.

Next action:
1. map all references to +0x09E4/+0x0A02/+0x0A20/+0x0A3E;
2. map remaining zero/padding bytes in the 2642-byte image;
3. relocate only strings that exceed their slots;
4. retarget their LUI/low-half address construction;
5. patch suffix middle character g->f;
6. locate and suppress only the GBA cache invalidation;
7. assert no other instruction/data changes.

No helper should be packaged before that delta audit passes.
