# Hardware Test 03 result — CPS1 gameplay pass, heavy-scene drops, pause QUIT freeze

Status: **GAMEPLAY PASS / PERFORMANCE PARTIAL / EXIT REGRESSION**

## Physical result

Street Fighter II and other CPS1 content launch and play through the external FB Alpha 2012 CPS-1 core.

Observed:

- gameplay works;
- mapper remains present;
- SNES/NES baseline remains intact;
- SFII is still somewhat laggy/choppy;
- frame drops become visible when the screen is busy;
- choosing QUIT from the pause menu freezes the device.

## Performance classification

Core #3 is not yet a decisive SFII performance win.

The external FBA2012 CPS1 core is functional, but heavy-scene frame pacing still degrades enough to be visible. Performance optimization remains open after exit stability is restored.

## Exit root-cause narrowing

Pinned FBA2012 CPS1 implements:

```c
void retro_unload_game(void) {}
```

All heavy teardown is concentrated in:

```c
retro_deinit()
 -> BurnDrvExit()
 -> GameInpExit()
 -> BurnLibExit()
 -> free(g_fba_frame)
 -> free(g_fba_rotate_buf)
```

Test 03 external frontend called `retro_deinit()` immediately after stock `run_emulator()` returned from the pause/QUIT path.

The freeze therefore occurs at a post-loop teardown boundary that is unique to FBA2012; gameplay/runtime transport is already proven working.

## Test 04 strategy

Do not change firmware or shared runtime.

Change only the CPS1 external image so that, after stock `run_emulator()` returns, the frontend restores stock callback/session state and returns to the injected loader **without calling FBA2012 `retro_deinit()`**.

Rationale:

- `retro_unload_game()` is intentionally empty;
- the XGOC image and private newlib/sbrk arena are disposable and reloaded on every launch;
- the stock ROM arena is reused by the next launch;
- avoiding FBA global teardown eliminates the hardware-failing transaction without weakening mapper/SNES/NES state.

## Test 04 identity

Build commit:

```text
afcaa0f5dd25a92f2cc8991d1dbe1b5057532c1b
```

Successful workflow:

```text
run      33841063910
artifact 9924938417
```

New CPS1 XGOC:

```text
SHA-256
4bff2b6cfa6cb6ae7140e39e60cc19b747167075801d3a6456df8e9eb3aadf20

payload  2,202,424 bytes
runtime  3,086,048 bytes
headroom 10,393,376 bytes
undefined symbols 0
```

Test 04 package:

```text
xgo-core3-cps1-test04-exitfix-v19-snes.zip
SHA-256
a8073822cd69df1654475ad8734df1a0ee1ce1e0cf5f6e4dbc2a9ba3120b6a1d
```

## Regression invariant

Test 04 is Test 03 with **only CPS1 core.xgc replaced**.

Unchanged:

```text
combined firmware
dfa9898368b697e91b2aff8cf83f819660c3e29fa9a4d3b2bd12f8614faf9b55

mapper-v19 gpapi.bvs
759cc078816e6b865ac177ca39a37bb542ae5f64bbfbf0c0cb10f230532950c8

Snes9x2005 core.xgc
ee694b5989e1d056f73de99a47588f124caa2df9b5e8c751862c92adb7a543bf
```

No loader/JAL/LCFG changes occur in Test 04.

## Hardware gate

1. Launch SFII.
2. Play long enough to confirm behavior matches Test 03.
3. Open pause menu and choose QUIT.
4. Expected: clean return to stock browser, no freeze.
5. Relaunch SFII to prove a second CPS1 session works.
6. Verify Mapper remains available.

Only after exit is stable should performance tuning continue.
