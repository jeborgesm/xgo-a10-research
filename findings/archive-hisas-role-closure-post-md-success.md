# Archive.sys and Hisas.boa role closure after successful MD Refresh

Evidence source: post-success Resources.zip, prior 20260919 forensic Resources, pristine XGoAnalisis, and Test97 firmware.

## Archive.sys

Firmware contains literal path format:
%s/Resources/Archive.sys
at 0x809A2E04.

Code at 0x8034C6D8 constructs that path, waits for access, opens it with mode "rb" through stock fopen 0x802B3524, then performs exactly three fread calls:
- 4 bytes into gp-3452
- 4 bytes into gp-24384
- 4 bytes into gp-3360
then fclose.

All three captured Archive.sys files are exactly 12 bytes / three uint32 values:
- pristine: 0,0,33
- prior forensic: 0,0,54
- post-success: 0,0,51

The third value is subsequently range-checked (<33 and <66 tests are visible immediately after load) and participates in frontend/runtime initialization logic.

Conclusion: Archive.sys is native frontend/runtime state, not an MD catalog member and not a Refresh transaction marker. Its changing third word is expected mutable state. Exact semantic label of that value remains OPEN.

## Hisas.boa

Hisas.boa is not an isolated ad-hoc file. Its filename pointer occurs three consecutive times in the firmware resource table at:
0x80A3C3D4
0x80A3C3D8
0x80A3C3DC.

This table follows the same triplet-oriented resource mapping region that contains the stock TAX/NEC/BVS catalog names. Nearby special slots include:
- None x3
- Falas.clk x3
- Hisas.boa x3
- None x3
followed by other resource filenames.

Therefore Hisas.boa is a native resource-table slot used uniformly for a special list/page/category, not evidence of partial MD catalog persistence.

Captured size is always 804 bytes. Between prior forensic and post-success captures, 200 of 201 32-bit words changed while size remained constant. This is consistent with a dense mutable runtime/list-state structure. Exact list identity and record semantics remain OPEN.

## Resources integrity after successful Refresh

All six stock catalog families are count-consistent:
FC 771/771/771
SFC 1070/1070/1070
MD 839/839/839
GB 891/891/891
GBC 958/958/958
GBA 626/626/626

Only three of 113 Resources files changed versus prior forensic capture:
- Archive.sys
- Hisas.boa
- wmiui.bvs

TAX and NEC MD files are byte-identical to their prior 839 versions. New wmiui.bvs completes the deterministic 839 triplet.

## Root-cause impact

Neither Archive.sys nor Hisas.boa currently supports the hypothesis that MD Refresh requires an omitted custom persistence/finalization step.

The successful hardware run demonstrates that the existing selective Refresh/custom catalog path can create a coherent immediately consumable 839/839/839 MD catalog when starting from a coherent baseline.

The earlier hard-lock/corruption episode should therefore be treated as an interrupted/damaged filesystem/catalog event until contrary evidence appears, not as a deterministic native-scanner-lifecycle failure.

Test103 direct scanner substitution remains independently invalid because its patched firmware did not boot.
