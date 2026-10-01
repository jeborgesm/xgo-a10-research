# Arcade Refresh - exact preview packaging boundary

Date: 2026-09-24
Branch: research-arcade-refresh-four-family
Status: DIRECT BIN CLOSURE FROM GOLDEN TEST75

Source golden FC/refresh.xgc SHA-256:
8b9607e51e4ad24cf19b92dc356f065d57081eaf93d722ccd9c65c00156fbd4e

## Exact artwork copy boundary

The destination wrapper file handle is stored at frame +0x44 and the transfer
buffer is s4.

After JPEG decode, if the RGB565 scratch output opens successfully, code
+0x08EC through +0x0954 copies exactly 0xEA00 bytes to the destination in
chunks no larger than 0x2000. Reads and writes are checked for the exact
requested count, then the RGB565 input is closed.

If artwork is unavailable, +0x0960 through +0x09B0 writes exactly 0xEA00 zero
bytes instead.

Both paths therefore converge at helper +0x09B4, runtime 0x870009B4, with the
destination positioned exactly at offset 0xEA00.

## Console-specific packaging begins there

At +0x09B4 Test75 begins constructing its console archive local header and
subsequent stored ROM archive structures.

Therefore +0x09B4 is the exact replacement boundary for Arcade.

Everything before it that prepares and copies the preview can be retained.
The console archive packaging after it is not needed by Arcade.

## Arcade replacement

At destination offset 0xEA00, Arcade needs:
- four zero bytes
- ASCII runtime ZIP basename such as dino.zip
- two zero bytes

Resulting size is 59910 + strlen(driver.zip).

This layout is independently BIN-proven against all four supplied stock ZFB
fixtures by tools/arcade_refresh/zfb_codec.py.

The reusable golden region is now sharply bounded:
source/art/meta discovery -> JPEG preparation -> exact 0xEA00 preview ->
boundary at +0x09B4 -> Arcade trailer.
