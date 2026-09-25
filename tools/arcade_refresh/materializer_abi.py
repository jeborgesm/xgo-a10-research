#!/usr/bin/env python3
"""Extract/audit the exact Test75 materializer ABI used by Arcade specialization."""
from __future__ import annotations
PARENT_SHA="8b9607e51e4ad24cf19b92dc356f065d57081eaf93d722ccd9c65c00156fbd4e"
PARENT_SIZE=0x101F08
LOAD_BASE=0x87000000
DECODER_OFF=0x100000
ARCADE_CODE_OFF=0x1100
CALLBACKS={
 "fopen":0x802B3524,
 "fclose":0x802B2F40,
 "fread":0x802B3698,
 "fwrite":0x802B42AC,
 "dir_open":0x807D40C4,
 "dir_next":0x807D4124,
 "dir_close":0x807D41F4,
 "unlink":0x807D40A8,
 "format":0x802946D8,
}
# Existing parent splice: preview is complete at +0x09B4.
PREVIEW_DONE=0x09B4
# Decoder call is direct through 0x87100000 at +0x0730/+0x0734.
DECODER_ENTRY=0x87100000

if __name__=="__main__":
    for k,v in CALLBACKS.items():print(f"{k:10s} 0x{v:08X}")
