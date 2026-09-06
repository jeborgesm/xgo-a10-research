# Audio OSD v3 hardware regression and v4 correction

Date: 2026-09-05
Branch: `research-audio-osd`

## V3 hardware result: FAIL

V3 successfully refreshed the volume OSD in the main frontend menu, but its frontend/game discrimination was wrong.

Observed hardware behavior during any running game when Volume was pressed:

```text
game
 -> loading screen
 -> OSD bar changes
 -> black screen
 -> loading screen
 -> game resumes
```

This effectively interrupted gameplay on every volume press.

The previous Audio OSD v2 implementation remained perfect inside games.

## Root cause

V3 treated the native 640x480 framebuffer geometry as a proxy for "main menu".

That assumption is false.

The frontend's 640x480 framebuffer remains allocated/available while a game session is active. Forcing `run_screen_write` from the controller task therefore presented stale frontend/loading buffers over the emulator-owned display.

The regression was caused by the forced menu repaint, not by the fine-volume policy or the original gameplay OSD hook.

## Correct architectural boundary

The common `run_emulator() @ 0x8035ed48` has a single common session entry and a single common return at `0x8035f2ac`.

V4 introduces a private `game_active` flag in the existing verified OSD cave:

```text
run_emulator entry -> game_active = 1
run_emulator return -> game_active = 0
```

The controller-task menu-refresh wrapper then follows:

```text
always perform stock dly_tsk(4)

if game_active:
    synchronize private menu last-volume state
    NEVER force run_screen_write
else:
    on volume change:
        force one normal frontend repaint
        restart ~1 second deadline
    on deadline:
        force one final repaint with bar disabled
```

This keeps the exact proven v2 gameplay OSD path untouched.

## V4 exact input

Hardware-confirmed v2 firmware:

```text
SHA-256
6b3261a9871c2b5678428ae1985176718c140178564ea924241bf6889ec714ac
```

## V4 patch surfaces

Relative to v2:

```text
0x0000018c..0x0000018f  LCFG CRC
0x00002d8c..            menu/game-session helper blob
0x0035d6c0              controller dly_tsk(4) call -> wrapper
0x0035ed6c              run_emulator entry -> game_enter_helper
0x0035f2ac              run_emulator return -> game_exit_helper
```

The stock delay-slot instructions at the hooked sites are preserved.

Candidate firmware:

```text
e6a36eb50a0dfb270a979d5f7650e6f374a8f2b885233e56be36770c48fa7ba2
```

Candidate ZIP:

```text
xgo-audio-osd-v4-frontend-only-refresh-test.zip
56210bea2240ab1fb5df5d56ed0390e43658dfe9d5388db5f71e5b7ffafa04cd
```

V3 must not be promoted to golden.
V4 remains a hardware candidate until regression-tested.
