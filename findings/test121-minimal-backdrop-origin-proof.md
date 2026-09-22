# Test121 minimal full-screen backdrop candidate

Date: 2026-09-21
Base: exact HW-proven Test119
Status: STATIC CANDIDATE; hardware pending

## Geometry closure

The Test119 backdrop loop is a conventional RGB565 rectangle after all.

Independent XGO executable evidence already proves the frontend surface is:
- width 640
- height 480
- RGB565 = 2 bytes/pixel
- pitch 0x500 = 1280 bytes

Therefore Test119:
- inner count 560 = rectangle width 560 pixels;
- outer count 360 = rectangle height 360 rows;
- base step 0x500 = exactly one framebuffer row;
- start offset 0xFA50 = 128080 bytes = 100*1280 + 80*2, therefore x=80, y=100;
- sampled color offset 0xFA14 = 128020 bytes = 100*1280 + 20*2, therefore x=20, y=100.

So the proven selector backdrop is exactly x=80..639, y=100..459: 560x360. That explains the exposed Setup content at the top and left. The fill color is sampled from x=20,y=100 before the rectangle is overwritten.

## Minimal Test121 delta

Do not change loop counts, pitch, function calls, hooks, stack/register behavior, text calls, or selector lifecycle.

Change only the initial write pointer from framebuffer+0xFA50 to framebuffer+0x0000 while preserving the existing 560x360 loop. **This is intentionally NOT yet full screen**; it is a one-immediate geometry proof that the existing loop can be repositioned without lifecycle regression.

Rationale: converting directly to 640x480 requires three independent changes (start, width, height). The continuity protocol calls for bounding the unknown. Test121 changes only origin. If HW remains responsive and the black/background region visibly moves to the top-left, the address interpretation is proven on hardware. Test122 can then change width/height to 640/480 with no new execution mechanism.

No footer is included.
