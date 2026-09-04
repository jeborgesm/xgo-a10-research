# Test 07 follow-up — raw ZFB format arithmetic is correct; ROM_BUFFER assumption is wrong

Status: **STATIC/HARDWARE INTERPRETATION CLOSED; CONTENT-HANDOFF TRACE CONTINUES**

## Hardware result

Test 07 was copied twice and produced the same behavior both times:

- select CPS1 game;
- stock `Loading......`;
- immediate return to CPS1 list;
- no external core gameplay.

This rules out a stale package.

## Important correction

The preserved XGO card inventory proves the visible arcade wrapper sizes.

Example:

```text
D:\ARCADE\Street Fighter II- The World Warrior.zfb  59917 bytes
D:\ARCADE\bin\sf2.zip                              8903809 bytes
```

For `sf2.zip` (7 bytes), the wrapper size matches exactly:

```text
59904 thumbnail
+ 4 zero bytes
+ 7 bytes "sf2.zip"
+ 2 zero bytes
= 59917
```

Therefore the original 59904-byte ZFB layout assumption is arithmetically consistent with the actual XGO card.

The Test 06/07 parser failure does **not** mean the on-disk XGO ZFB format differs.

It means the stronger assumption was wrong:

> `ROM_BUFFER` at the corrected arcade runtime hook is not necessarily the untouched raw .zfb wrapper.

By the time execution reaches the stock arcade runtime wrapper, `run_game()` has already performed arcade-specific preprocessing. The selected wrapper may have been consumed, transformed, decompressed, or the shared buffer may have been repurposed.

## Firmware evidence

The preserved firmware contains the adjacent stock strings:

```text
%s/bin/%s
Loading %s
```

which strongly supports a stock preprocessing step that constructs the real arcade archive path itself.

The next task is therefore to trace the caller of this format string and identify the stock-produced ZIP basename/path or the post-preprocessing structure passed to the arcade runtime.

## Direction

Do not generate another hardware candidate by guessing ZFB byte offsets.

Instead:

1. locate machine-code references to `%s/bin/%s`;
2. recover the surrounding stock arcade preprocessing routine;
3. identify where the derived ZIP name/path is stored;
4. reuse that exact stock value from the CPS1-only frontend or hook earlier, before it is discarded;
5. preserve the corrected list-ID gate and runtime hook.

## Baseline protection

Keep unchanged:

- mapper v19;
- NES external core path;
- Snes9x2005;
- CPS2/IGS/Neo Geo stock fallback;
- corrected CPS1 runtime hook at 0x80360df8;
- stock arcade cleanup at 0x80360e00.

The next CPS1 candidate should be based on direct XGO preprocessing evidence, not related-device wrapper assumptions.
