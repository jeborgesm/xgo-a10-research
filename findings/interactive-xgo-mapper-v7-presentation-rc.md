# Interactive XGO mapper v7 presentation-only release candidate

## Scope

v7 intentionally leaves the hardware-proven v6 firmware unchanged. Only `Resources/gpapi.bvs` is replaced.

## Changes

- Remove the artificial solid blue/purple left pane introduced by the experimental mapper resource.
- Restore the original XGO `gpapi.bvs` artwork on the left side, so the pause-menu area no longer sits on a large synthetic block.
- Lower the `Button Mapper` title box and text while preserving the physical/map-to tables and bottom control legend.
- Keep the v6 native pause-menu label `Mapper` and all mapper input/persistence code unchanged.

## Identity

```text
firmware SHA-256 (unchanged from v6):
caf42f072563d5ddc805f2d353f0eb2ec64d8631bedb1da11415abcf655caf51

v7 gpapi.bvs SHA-256:
40c88b4d605d5e215a19fb938e81906262197efffb4c13c28086cb7b83a86808

v7 card ZIP SHA-256:
bf7f961c610690c710a371810b8091f24b798cf9da4ab951b355b701d68ef8a9
```

## Final hardware check

1. Open pause menu and confirm the large synthetic blue/purple block is gone.
2. Confirm `Mapper` still appears once and is navigable.
3. Enter Mapper and confirm `Button Mapper` is fully visible lower in its header.
4. Perform one quick remap and confirm behavior/persistence are unchanged.

If this passes, merge/close the mapper branch; further emulator/audio work should continue on separate branches.