# Test120 — full-screen Refresh Games renderer

Date: 2026-09-21
Base: protected HW-positive Test119
Status: hardware candidate

## Root cause refined from exact Test119 renderer

The Test119 selector already attempted to hide the underlying Setup UI, but its backdrop loop was only a partial/strided fill. Exact renderer code at `0x80A38ABC`:
- loads the frontend framebuffer;
- samples a background pixel;
- starts from an interior framebuffer offset;
- fills 560 halfwords per inner loop;
- advances with an additional 0x500-byte stride;
- repeats 360 times.

That explains the hardware appearance: enough of the underlying Setup tile/highlight survives to look like a second selection behind REFRESH GAMES.

## Test120 renderer-only delta

Test120 replaces only that partial backdrop loop with a full logical-canvas clear:

```text
s0 = *(gp-5136)          # frontend framebuffer
a0 = s0
a1 = 0                   # byte fill; RGB565 black = 0x0000
a2 = 0x96000             # 640 * 480 * 2
jal memset               # 0x80294B9C
```

The existing Test119 title, eight rows, current-row treatment, stock font calls, A/B lifecycle, command dispatch and native Refresh path are retained.

A footer helper is placed in verified free tail beginning at `0x80A39000` and draws through the same stock text renderer:

`A Select        B Cancel`

The existing renderer transfers to the footer helper after row 7, then the helper returns to the original register-restore epilogue at `0x80A38E9C`.

## Protected invariants

Unchanged from HW-positive Test119:
- navigation terminal hooks;
- Test118 selector-aware B helper;
- inactive stock B behavior;
- unified A row0..7 command dispatcher;
- Game Boy command 3 behavior;
- caller state-14 normalization to 3 before native Refresh;
- native Refresh entry and status/return lifecycle;
- renderer restore epilogue;
- Volume OSD code.

## Candidate identity

Firmware SHA-256:
`9d3c6b42331f336a477b5dd5c8bbfed654b2a4c2c43a0a17ccc0d2aeb9670a2f`

LCFG CRC-32/MPEG-2:
`0xF4AC1B7A`

Candidate ZIP SHA-256:
`71fb85a7c5bbca8f62499796200920f0de1839255ccb299212ce47db13869074`

Hardware gate:
1. open Refresh Games;
2. verify no Setup tiles/blue border remain visible behind it;
3. verify footer is readable;
4. navigate all eight rows;
5. B closes to normal Setup;
6. reopen and run Classic/No New Games;
7. verify Refresh Games can reopen afterward.
