# CLASSIC Refresh resurface — invocation-contract closure

Date: 2026-09-20
Branch: `research-classic-refresh-resurface`
Status: **offline archaeology; no firmware candidate yet**

## Objective

Get out of the temporary Settings-page selective Refresh UI without reopening the unsafe Test83-Test92 renderer experiments.

The first task is not to draw the final menu. It is to recover the exact hardware-proven CLASSIC module contract so the future selector can dispatch CLASSIC independently.

## Proven CLASSIC module

The cumulative hardware record closes the runtime component:

```text
/CLASSIC/refresh.xgc
SHA-256 (Test72 protected helper):
9f932f35b1627bb8a4a7427831454e3c5dd854972231c1062316a814ada8723f
```

Test60 proved the external-helper architecture and stable result semantics. Test64 added integrated JPEG handling. Test72 then validated the complete path with a 50-game batch and a second unchanged Refresh.

Protected steady-state layout:

```text
/CLASSIC/bin/       source ROM ZIPs
/CLASSIC/art/       JPG source + generated RGB565 cache
/CLASSIC/meta/      friendly-title TXT sidecars
/CLASSIC/*.zfb      generated wrappers
/CLASSIC/save/      save states
/CLASSIC/refresh.xgc
/cores/classic-mame2000/core.xgc
```

## Historical invocation path

The proven cumulative Test72-era Refresh lifecycle was:

```text
stock Refresh command
        |
        v
six-console generalized scanner / stock enrichment prework
        |
        v
0x807DB6B8
        |
        | branch after stock-list loop
        v
CLASSIC bootstrap
0x80A38000..0x80A3823F
        |
        | validates heap ceiling
        | fopen /CLASSIC/refresh.xgc
        | load helper at 0x87000000
        | temporarily lower RAMSIZE
        | cache maintenance
        | call helper
        | restore RAMSIZE
        v
helper return
        |
        +---- changed ----> Games Updated
        +---- no change --> No New Games
        +---- failure ----> Refresh Failed
```

The key distinction is **entry context**.

The address `0x80A38000` was hardware-proven when reached through the original Refresh lifecycle. Test92 later tried to treat it as a standalone callable function and hard-locked. Therefore:

```text
PROVEN:
native Refresh lifecycle -> post-stock-loop edge -> CLASSIC bootstrap

NOT PROVEN / REJECTED:
arbitrary UI callback -> jal 0x80A38000
```

This explains why "the CLASSIC bootstrap exists" does not mean "call its first byte from any menu."

## What the future selector must do

The final selector needs an adapter, not a direct bootstrap jump:

```text
native REFRESH GAMES selector
          |
          v
 CLASSIC module adapter
          |
          | establish the same Refresh workspace/lifecycle
          | expected by the post-stock-loop CLASSIC edge
          v
 proven CLASSIC bootstrap
          |
          v
 /CLASSIC/refresh.xgc
          |
          v
 common status UI
```

The adapter should reuse the native Refresh entry/workspace initialization and route execution to the CLASSIC post-loop edge, rather than synthesizing unknown globals by hand.

## Why this is the lowest-risk route

Binary archaeology already established that the original Refresh function initializes workspace before the selective hook at `0x807DB67C`. Later MD investigation showed that bypassing native lifecycle stages can have consequences. CLASSIC gives us an even stronger HW warning: direct invocation at `0x80A38000` hard-locked.

Therefore the resurface work should preserve native entry initialization and alter only the module-selection control flow.

## UI implications

The current Settings-page selector is a diagnostic mechanism only. It should not receive visual polish.

Rejected historical routes:

```text
Test83 selective Refresh UI       FAIL
Test84 mapper-style modal         HARD FREEZE
Test86 scalable pages + CLASSIC   NO BOOT
Test87 relocated scalable pages   NO BOOT
Test88 render-hook bisect         NO BOOT
Test89 guarded render hook        NO BOOT
Test90 first-class REFRESH shell  NO BOOT
Test91 dormant REFRESH assets     BOOT + frontend corruption
Test92 direct CLASSIC invocation  HARD LOCK
```

The next UI archaeology must find a native XGO selectable-list grammar rather than invent another renderer or adding guessed resource files.

## Protected CLASSIC behavior

Do not regress:

- Test47 generalized CLASSIC importer;
- Test52 Save/Load;
- Test57 12-slot CLASSIC logo atlas;
- Test58/Test60 add/remove reconciliation and stable no-change semantics;
- Test64 JPEG decode/scale path;
- Test72 50-game metadata/JPEG batch;
- normalized MAME2000 core SHA-256 `60a62e463fd6faf92744a7be666602dd1621b9fd706f90d20e3b55ee3382bb1e`;
- Mapper v19;
- Audio OSD v8;
- Test106 MD transaction hardening;
- stock FC/SFC/MD and stock Arcade.

## Next offline step

Map the native Refresh function around:
- its entry/workspace initialization;
- `0x807DB67C` selective-hook point;
- stock-list loop;
- `0x807DB6B8` CLASSIC transition;
- common status exits.

Then construct a CLASSIC-only lifecycle adapter that enters through native initialization and reaches the already-proven CLASSIC transition without scanning/mutating unrelated stock lists.

No hardware package is justified until that control-flow/ABI map closes.
