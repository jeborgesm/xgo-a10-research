#!/usr/bin/env python3
from pathlib import Path

libretro = Path("/tmp/mame2000/src/libretro/libretro.c")
video = Path("/tmp/mame2000/src/libretro/video.c")

s = libretro.read_text()
anchor = "static retro_input_state_t input_state_cb;\n"
insert = """static retro_input_state_t input_state_cb;

extern volatile int xgo_mame2000_skip_render;
"""
if anchor not in s:
    raise SystemExit("libretro input callback anchor not found")
s = s.replace(anchor, insert, 1)

old = """   if (should_skip_frame)
      video_cb(NULL, gfx_width, gfx_height, gfx_width * 2);
   else
      video_cb(gp2x_screen15, gfx_width, gfx_height, gfx_width * 2);
"""
new = """   if (xgo_mame2000_skip_render)
      video_cb(NULL, gfx_width, gfx_height, gfx_width * 2);
   else
      video_cb(gp2x_screen15, gfx_width, gfx_height, gfx_width * 2);
"""
if old not in s:
    raise SystemExit("retro_run video submission block not found")
s = s.replace(old, new, 1)
libretro.write_text(s)

v = video.read_text()
anchor = "extern int should_skip_frame;\n"
insert = """extern int should_skip_frame;
extern volatile int xgo_mame2000_skip_render;
"""
if anchor not in v:
    raise SystemExit("video should_skip_frame anchor not found")
v = v.replace(anchor, insert, 1)

old = """int osd_skip_this_frame(void)
{
   return should_skip_frame;
}
"""
new = """int osd_skip_this_frame(void)
{
   return xgo_mame2000_skip_render;
}
"""
if old not in v:
    raise SystemExit("osd_skip_this_frame block not found")
v = v.replace(old, new, 1)
video.write_text(v)

print("patched MAME2000: XGO stock adaptive frameskip drives render skipping")
