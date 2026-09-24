# Test124 hardware result — GB/GBC/GBA native selective scanner does not discover new ROMs

Date: 2026-09-22
Branch: `research-refresh-gb-gbc-gba`
Status: **HW FAIL for intended discovery behavior; device/status lifecycle remains responsive**

## Hardware observation

Test124 was installed and exercised on the XGO A10.

Pre-existing `.gb` files were already present in `/GB` and had been added to the visible list by an earlier Refresh implementation/test.

For this test the user additionally placed:
- one Mario game in `/GBC`;
- one Mario game in `/GBA`.

Selecting the corresponding Refresh Games rows repeatedly returned:

`No New Games`

The newly added GBC/GBA games were not detected.

## What this means

HW:
- Test124 does **not** satisfy the branch goal of discovering new GB/GBC/GBA ROMs.
- Do not promote Test124.
- The native status return path is at least non-crashing/responsive enough to report `No New Games`.

It does **not** prove that commands 3/4/5 were misrouted: all three may be reaching `0x807DAE4C` and receiving zero. It also does not prove that the scanner ABI/list IDs are wrong.

The important contradiction is historical: GB files already on this card were successfully added by an earlier implementation, while Test124's direct selective native-scanner route does not discover equivalent new content.

## Next investigation

Do not patch another candidate yet.

Recover the exact earlier implementation that successfully added GB/GBC/GBA entries, especially:
- Test08 all-console scanner and any later HW result/promoted derivative;
- Test45/Test47-era generalized Refresh lineage if applicable;
- extension classifier/list-ID conventions (note Test08 custom scanner used one-based IDs 4/5/6 for GB/GBC/GBA while the native scanner table ABI is zero-based 3/4/5);
- directory/path construction inside native `0x807DAE4C`;
- whether the native scanner is intended to consume wrappers/catalog-ready files rather than the raw files currently being placed in these directories;
- whether the earlier successful addition came from the custom generalized scanner rather than the native scanner.

The next candidate must reuse the hardware-proven discovery mechanism rather than assuming the native scanner is sufficient merely because its catalog ABI is known.
