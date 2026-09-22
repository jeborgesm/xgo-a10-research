#!/usr/bin/env python3
"""Build Test125 2642-byte Stage1 loaders from exact HW-passed Test106 Stage1.

Only two semantic changes are allowed:
1. replace the MD Stage2 path with the selected handheld catalog-saf.xgc path;
2. bypass the MD-specific transaction-marker finalizer after Stage2 and jump to
   the existing Stage1 epilogue, preserving Stage2 v0.

The 2642-byte generic-runner load contract is never changed.
"""
from __future__ import annotations
import argparse,base64,hashlib,struct,zlib
from pathlib import Path
TEMPLATE_SHA="e4c21a94055a6aec817494d2f69450f12fbba3244a91c1b74e73de2a4e91b338"
TEMPLATE_SIZE=2642
TEMPLATE_ZB64="eNrtk0Fo02AYht+kaUmhsqBFO9dDAn9ooXaZUOuEgGnrDoJ6kCE7GuvcRTdYC7qTOQjdyeykPXqYeBHSqYcdttmD7Lyjx9302ONgh/j9aYqxbKN68tAXQpKf7//yPm/+78DfzV3BVy+PPY/hi6fis5fFJy+DLS+Njqf33sXQEkxFYIzfC84Fk11bKyeP1Ni0oLM8LMX3FaavW2iX18oLU2mWaUmmgDhbmEowXqfPWtA3LFhGf5+uquJlzF8EyX8pmj2/WoITM3s36yUFVQZUdvhVkGs49tU0r5s4tdba4Ve0NtOaNPl3+LPuWJCFbpI/E49LXC7xucTpEq9L3C7xuzIOYzPYzRnPlptG47F91bh7y6jbTfvpylKxYT9ZnH6xVMfqI5wsB/+o75Q/o/xVyjpLmWcoe1B+jvSqhFbc3JTelwrOJGV+4/qASaPMgztnw2aOZ51AgmmzEHltuxyppf+iqf11y/i9Doi0R2AT0IL/IFM2aJ03t6X7Zcr+dRJCsJ5C562Eypt4+C7Qvg308+Q9yC/luUV5dijPfo55ynHAd0h8WeLLEF+a+LR1iirC9+EEvksRPo3OyjDfx+rofPGQj/vei/gmL3QWOuS971kNPR+RX4n8co8d8thG9xxfl8I6OcI2XL/9F/UPw7o4rODMtsX94P1H6JH7Pa1HVD3ql6J+KWl/0C/I7lvY/zjCnAr7KWf0GxaFmeD3g7CfpkDUfnZjo8zSKP3/mDd7tWnQnK0UafCKjabdXAxqaOqeDwavUpu//WAOqN2Zq9zTMNZYY4011n+jX5N+7rU="
OLD_PATH=b"/mnt/sda1/MD/catalog-safe.xgc\0"
PATH_OFF=0x110
MODE_OFF=0x12E
FINALIZER_J_OFF=0xE4
OLD_FINALIZER_J=0x09C00108
EPILOGUE_J=0x09C0003B # j 0x870000EC
PATHS={
 "gb":b"/mnt/sda1/GB/catalog-saf.xgc\0",
 "gbc":b"/mnt/sda1/GBC/catalog-saf.xgc\0",
 "gba":b"/mnt/sda1/GBA/catalog-saf.xgc\0",
}
def sha(b):return hashlib.sha256(b).hexdigest()
def build(system):
 b=bytearray(zlib.decompress(base64.b64decode(TEMPLATE_ZB64)))
 assert len(b)==TEMPLATE_SIZE and sha(b)==TEMPLATE_SHA
 assert bytes(b[PATH_OFF:PATH_OFF+len(OLD_PATH)])==OLD_PATH
 assert bytes(b[MODE_OFF:MODE_OFF+3])==b"rb\0"
 assert struct.unpack_from("<I",b,FINALIZER_J_OFF)[0]==OLD_FINALIZER_J
 p=PATHS[system]; assert len(p)<=MODE_OFF-PATH_OFF
 b[PATH_OFF:MODE_OFF]=b"\0"*(MODE_OFF-PATH_OFF); b[PATH_OFF:PATH_OFF+len(p)]=p
 struct.pack_into("<I",b,FINALIZER_J_OFF,EPILOGUE_J)
 assert bytes(b[MODE_OFF:MODE_OFF+3])==b"rb\0"
 assert len(b)==TEMPLATE_SIZE
 return bytes(b)
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--outdir",type=Path,required=True);a=ap.parse_args();a.outdir.mkdir(parents=True,exist_ok=True)
 for s in PATHS:
  b=build(s);p=a.outdir/(s+"-catalog.xgc");p.write_bytes(b);print(s,len(b),sha(b))
if __name__=="__main__":main()
