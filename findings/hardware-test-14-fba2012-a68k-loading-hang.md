# Hardware Test 14 — FBA2012 native-MIPS A68K hangs during loading

Status: **HARDWARE FAIL / A68K DOES NOT RESCUE FBA2012**

Observed on physical XGO:

```text
select CPS1 game
 -> stock "Loading....."
 -> device remains frozen there
```

No CPS1 self-test or game video appears.

## Comparison with prior FBA2012 behavior

Previous FBA2012/Musashi candidate:

```text
ROM load / init progressed far enough to show SFII RAM/self-test
 -> then froze around first frame execution
```

Test 14 A68K candidate:

```text
never clears stock Loading overlay
 -> no CPS1 video
 -> therefore failure occurs earlier than the Musashi first-frame stall
```

## Conclusion

The dormant MIPS A68K backend is not a drop-in fix for the XGO FBA2012 runtime.

The failure moved earlier into load/CPU-init/reset/context setup, which means the next investigation should focus on:

- `SekInitCPUA68K()`;
- A68K context allocation/initialization;
- `M68000_RESET` behavior;
- A68K memory-interface ownership/layout;
- A68K callback ABI against the current FBA2012 interface;
- whether the old Allegrex backend expects PSP-specific runtime assumptions beyond instruction set.

Do not spend more hardware cycles on performance tuning until load_game/init can return.

## Current CPS1 core status

MAME2000:
- boots and plays;
- controls fixed;
- too slow, even with adaptive frameskip.

FBA2012 Musashi:
- reaches CPS1 self-test;
- freezes on/under first frame.

FBA2012 A68K:
- freezes during loading/init before first CPS1 video.

Stock XGO arcade core remains the only functional CPS1 baseline.

## Baseline protection

Mapper v19, NES, Snes9x2005, and stock CPS2/IGS/Neo Geo remain unchanged.
