# Interactive XGO mapper v6 final refinement

## Hardware status entering v6

The interactive mapper architecture is hardware proven across CPS1, NES, and SNES test cases. The following behavior has been confirmed on device:

- real pause-menu Mapper entry is navigable;
- mapper editor opens and is usable;
- all six ordinary physical controls can be remapped;
- arbitrary remaps such as A<->B work;
- per-ROM `.kmp` persistence survives game restart;
- corrected writer filename path is effective.

The remaining issues entering v6 are presentation-only.

## v6 presentation cleanup

v6 intentionally leaves the proven mapper/input/save implementation unchanged and makes only these presentation refinements:

1. Native pause-menu label changes from `MAPPER` to `Mapper`.
2. The obsolete static `MAPPER` text baked into the mapper RGB565 background is removed.
3. The page title is changed to `Button Mapper` and centered/lowered inside the top title box so it is fully visible on hardware.
4. Bottom control instructions are moved upward for better visibility.

## v6 identity

```text
firmware SHA-256:
caf42f072563d5ddc805f2d353f0eb2ec64d8631bedb1da11415abcf655caf51

LCFG CRC-32/MPEG-2:
0xfbd1bb6a

gpapi.bvs SHA-256:
309ce7d9486079a8ae63e1c282028ea3aeec1ef249ed24d487fc38822b56d415

card ZIP SHA-256:
e88b3ee1e29560c84d340cf5f569692f8a62e853bec013198fce30c8ba7dd35b
```

## Branch-close criterion

A final hardware visual check should confirm:

- `Mapper` appears once in the pause list;
- `Button Mapper` is fully visible;
- no obsolete ghost label remains;
- one quick remap still behaves and persists as before.

After that, the mapper branch can be treated as complete and merged/closed. Further enhancements should be tracked separately rather than expanding this branch.