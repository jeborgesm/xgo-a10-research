# Test 12 timing diagnosis — missing XGO adaptive frameskip seam

Status: **STATIC RUNTIME CONTRACT CLOSED; TEST 13 JUSTIFIED**

## Hardware symptom

Test 12 is playable and does not visibly drop many frames, but CPS1 gameplay is globally much too slow ("underwater").

Audio is also choppy/out of sync.

## MAME2000 CPU backend evidence

The pinned MAME2000 source supports optional fast CPU backends:

```text
Cyclone 68000
DrZ80
```

and its per-game frontend table marks:

```text
sf2  cores=3  -> Cyclone + DrZ80
dino cores=1  -> Cyclone
```

However the actual `platform=sf2000` Makefile does not enable `USE_CYCLONE` or `USE_DRZ80`.

Those optimized backends are ARM-oriented and are enabled on targets such as Miyoo, not the MIPS32 SF2000/XGO build.

The linked XGO MAME2000 image confirms portable CPU cores are present:

```text
z80_execute
m68k_op_...
```

with no Cyclone/DrZ80 symbols.

This makes full-frame CPS1 rendering expensive on HC15xx.

## More important XGO-specific finding

The stock arcade wrapper at `0x80360848` installs:

```text
0x80c33ae0 = stock arcade frameskip callback @ 0x8036bdc0
0x80c33ae4 = stock arcade retro_run
```

Our external MAME2000 frontend has been setting:

```text
GFN_FRAMESKIP = 0
```

thereby disabling a stock XGO runtime service.

## run_emulator behavior

Inside stock `run_emulator()`, XGO continuously measures timing drift.

When the optional frameskip callback is non-null, it calls that callback with a frontend-generated skip/lag state before the next frame.

The relevant flow is around:

```text
0x8035ef54  load gfn_frameskip
...
0x8035ef74  if non-null -> 0x8035f0d4
0x8035f0d4  call gfn_frameskip(skip_state)
...
             continue to active retro_run
```

This is an adaptive rendering-control seam controlled by the stock frontend's own wall-clock logic.

## MAME2000 rendering cost

MAME2000's `updatescreen()` does:

```c
if (osd_skip_this_frame() == 0)
    draw_screen(...);
```

so a skipped frame avoids the expensive CPS1 `vh_update` rendering work while still:

- updating sound;
- processing the UI/input path;
- advancing emulated CPUs/devices;
- reaching the next frame boundary.

That is exactly the behavior needed to recover real-time emulation when rendering is the bottleneck.

## Test 13 design

Do not enable MAME2000's RetroArch audio-buffer-based auto-frameskip; XGO does not implement that frontend callback contract.

Instead bridge XGO's own stock frameskip callback slot into MAME2000:

```text
run_emulator lag detector
 -> xgo_mame2000_set_frameskip(skip)
 -> MAME2000 osd_skip_this_frame()
 -> skip CPS1 draw when XGO says the emulator is behind
```

Also suppress video submission for skipped frames.

This preserves emulated CPU/audio progression and lets the stock XGO frontend remain the timing authority.

## Baseline preserved

Test 13 keeps:

- Test 11 input isolation;
- Test 12 clean state namespace;
- mapper v19;
- NES;
- Snes9x2005;
- CPS2/IGS/Neo Geo stock paths;
- corrected CPS1 runtime hook/content path;
- MAME2000 CPU/libco/audio implementation.

Only the MAME2000 frameskip adapter changes.
