# Audio OSD v3 — sparse main-menu repaint candidate

Date: 2026-09-05
Branch: `research-audio-osd`

Status: **STATICALLY BUILT; HARDWARE TEST PENDING**

## Why v2 appears stale in main menus

The 640x480 frontend uses the same shared framebuffer globals and the same `run_screen_write @ 0x8035c398` presentation helper as the rest of the stock UI.

Confirmed frontend call contract repeatedly appears as:

```text
a0 = *(gp-5136)  framebuffer @ 0x80c33364
a1 = *(gp-3608)  width       @ 0x80c3395c
a2 = *(gp-3612)  height      @ 0x80c33958
a3 = a1 << 1     byte pitch
jal run_screen_write
```

The main menu, however, only submits a frame when its own UI changes. A volume-button press changes `g_volume` and audio immediately but does not itself trigger one of those menu redraw paths.

That exactly explains the hardware symptom.

## Controller task provides a safe low-frequency service point

The controller task contains an existing:

```text
8035d6c0  jal dly_tsk
8035d6c4  li  a0,4
```

on its polling path.

V3 replaces only that JAL with a wrapper. The wrapper first performs the original `dly_tsk(4)`, preserving controller cadence, then services menu OSD timing.

Because the original call already clobbers caller-saved registers by ABI, wrapping this call is much safer than inserting an arbitrary call in live controller-state arithmetic.

## Menu-only policy

The helper acts only when current frontend geometry is exactly:

```text
640 x 480
```

That is the stock frontend canvas.

On volume change:

1. update private `menu_last_volume`;
2. set the existing OSD visible state;
3. set a wall-time deadline to `now + 1000 ms`;
4. call the ordinary `run_screen_write` once.

On each later controller poll:

- if no deadline is active: no display work;
- before deadline: no display work;
- after deadline: clear OSD visible state and call `run_screen_write` exactly once to repaint without the bar.

Repeated volume changes restart the 1000 ms deadline.

Therefore the desired menu behavior is:

```text
idle                 -> no bar
volume change        -> one immediate redraw, bar visible
more volume changes  -> immediate updates, timeout restarts
1 s inactivity       -> one clearing redraw
idle again           -> no redraw traffic
```

## Patch surface

Base = hardware-confirmed v2:

```text
firmware SHA-256
6b3261a9871c2b5678428ae1985176718c140178564ea924241bf6889ec714ac
```

The original OSD v1/v2 backup area ends at `0x80002d8b`.

V3 uses the remaining verified cave:

```text
helper runtime 0x80002d90
helper size    304 bytes
```

Controller hook:

```text
0x8035d6c0
jal 0x8030f480  -> jal 0x80002d90
```

The wrapper itself calls the original `dly_tsk(4)` first.

Candidate firmware:

```text
SHA-256 67e8474db2c0a85e230517adb2a699877b046b74fceddc0a2e2bb59fc9145dec
LCFG CRC 0xd54bff0d
```

Candidate ZIP:

```text
xgo-audio-osd-v3-menu-refresh-test.zip
SHA-256 15edc2b239cc9c7f9fed09ff0c3363ded2bc7fb10bd1345072abfc144bfad8bc
```

The candidate ZIP is archived immediately in the private artifact repository root. It must not be copied to `golden/` until hardware passes.
