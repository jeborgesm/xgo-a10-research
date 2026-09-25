# Arcade catalog helper — relocation mechanics closure

Date: 2026-09-24
Branch: research-arcade-refresh-four-family
Status: SRC relocation primitive closed; reference map still required

The Arcade catalog binary builder now has an explicit MIPS32 little-endian
address-relocation primitive in tools/arcade_refresh/catalog_relocation.py.

The generic runner loads catalog helpers at 0x87000000.  Relocated literal
references therefore use runtime address 0x87000000 + helper offset.

The builder must use the standard signed-low-half carry rule:

hi16 = (address + 0x8000) >> 16
lo16 = address & 0xffff

and encode LUI + ADDIU only after confirming the original reference uses that
construction. It must not patch a raw low half without auditing the producing
instruction pair.

For the original GBA literals:
slot0 +0x09E4 -> 0x870009E4
slot1 +0x0A02 -> 0x87000A02
slot2 +0x0A20 -> 0x87000A20
root  +0x0A3E -> 0x87000A3E

Because all are below the signed-low carry boundary, their current high half is
0x8700. A relocated string crossing +0x8000 would require high-half carry and
must be handled by the helper rather than assumed.

Next required BIN step remains exact reference discovery in the parent helper;
the relocation primitive is deliberately not allowed to guess instruction
locations.
