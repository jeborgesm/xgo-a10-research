# Test121 — full-screen backdrop using the exact Test119 fill loop

Date: 2026-09-21
Base: exact HW-proven Test119
Status: STATIC CANDIDATE; hardware pending

Test120 is rejected. This candidate does not use memset, a helper, an extra text call, or a new hook.

## User-visible target

Preserve the working centered REFRESH GAMES title/list and its sampled gray background color. Change only the coverage of the existing HW-proven backdrop so Setup content cannot remain visible behind it. No footer yet.

## Test119 mechanism retained

The Test119 renderer samples the existing gray RGB565 pixel at fb+0xFA14 into t1, then fills using:
- sh t1,0(t3)
- t3 += 2
- inner decrement/branch
- base += 0x500
- outer decrement/branch

That exact fill body is unchanged.

Independent BIN evidence proves the frontend is 640x480 RGB565 with 0x500-byte pitch. Therefore full-screen traversal with the same body is:
- initial write pointer = fb
- inner count = 640
- outer count = 480
- row pitch = 0x500

The gray sample remains unchanged at fb+0xFA14.

## Exact executable delta from Test119

Only four existing instructions/immediates change:

```text
80A38ACC  lui t0,0x0001       -> nop
80A38AD4  addiu t0,t0,-1456   -> nop
80A38AD8  li t2,360            -> li t2,480
80A38AE0  li t4,560            -> li t4,640
```

The intervening `addu t0,s0,t0` therefore computes the initial base as exactly framebuffer.

Everything else in the Test119 renderer and selector lifecycle is byte-identical except LCFG header size/CRC bookkeeping.

## Expected hashes

Firmware SHA-256:
`d60e5ba371bc2ccd4959b46d8dd9ae4a0c9fc78c5f6586129b796948a9ef1f62`

LCFG CRC32/MPEG-2:
`0x7853E486`

Generated ZIP SHA-256:
`33b22513bf4349dc67b97fabc82114e872b0cf770e7505f2b71e519db606569c`

## Hardware gate

Expected:
1. Refresh Games appears immediately and remains responsive.
2. Same centered title/list and same gray.
3. No Setup tiles/borders visible anywhere behind it.
4. B closes to normal Setup.
5. Re-enter works.
6. Classic/No New Games/re-enter remains Test119-compatible.

Do not add the A/B legend until this geometry-only candidate passes.
