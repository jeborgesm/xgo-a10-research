# Arcade catalog parent — exact reference and capacity closure

Date: 2026-09-25
Branch: research-arcade-refresh-four-family
Status: BIN CLOSED; important size constraint discovered

Exact parent:
GBA/catalog.xgc
size 2642 (0x0A52)
SHA-256 db7c1173f5b98adb3506b2676a035ba6e54b35a4391709cbbcd7ad92b983cbc6

## Exact literal references

slot0 +0x09E4 / 0x870009E4:
- +0x0050 LUI at=0x8700, +0x0054 ADDIU a0,at,0x09E4
- +0x0628 LUI at=0x8700, +0x062C ADDIU a0,at,0x09E4

slot1 +0x0A02 / 0x87000A02:
- +0x00B8/+0x00BC
- +0x0684/+0x0688

slot2 +0x0A20 / 0x87000A20:
- +0x0120/+0x0124
- +0x06DC/+0x06E0

root +0x0A3E / 0x87000A3E:
- +0x02E8 LUI at=0x8700
- +0x02F8 ADDIU a0,at,0x0A3E

GBA cache invalidation:
- +0x0730 LUI at,0x80D2
- +0x0734 ORI at,at,0x8974
- +0x0738 SW zero,0(at)

The cache write is isolated and can be neutralized by NOPing only +0x0730..+0x0738 in the first Arcade proof while preserving the return path at +0x073C.

## Tail capacity

The parent ends at +0x0A52. The complete string table begins at +0x09E4 and is
only 0x6E (110) bytes long:

- three 30-byte catalog path slots
- root /mnt/sda1/GBA
- rb
- wb

There is no >=16-byte zero run anywhere in the 2642-byte image.

The four-family staging specialization needs, including NULs and rb/wb:
- CPS1 131 bytes
- CPS2 131 bytes
- IGS 130 bytes
- NEOGEO 133 bytes

Therefore none can fit in the existing 110-byte tail.

## Consequence

A safe Arcade helper cannot remain 2642 bytes if it uses the staging-directory
roots. This is not a generic-runner limitation: command 6 is a new route and
can request a larger external-helper byte count without touching the protected
GBA command/helper size.

The safest construction is to append a new literal table after +0x0A52,
increase only the command-6 Arcade catalog-helper load size, and retarget the
seven catalog/root references listed above. Existing code body remains the
HW-proven GBA body except:
- .zgb middle suffix character g -> f;
- seven literal references;
- isolated GBA cache invalidation NOPs.

No in-place string overlap or code cave is required.
