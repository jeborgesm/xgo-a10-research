#!/usr/bin/env python3
"""Extract the exact HW-proven Test08 scanner blob from its reproducer source."""
from __future__ import annotations
import argparse, ast, base64, hashlib, re, zlib
from pathlib import Path
EXPECTED_LEN=3601
EXPECTED_SHA="a3f965d0ccabc2238da240a4b05b5f8027c968e40ede1831b51c42cff374c01d"
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--source",type=Path,default=Path(__file__).with_name("build_test08_all_console_scanner_candidate.py")); ap.add_argument("--output",type=Path,required=True); a=ap.parse_args()
 s=a.source.read_text(); m=re.search(r"SCANNER_ZB64='''([A-Za-z0-9+/=\n\r]+)'''",s); assert m
 b=zlib.decompress(base64.b64decode(m.group(1))); h=hashlib.sha256(b).hexdigest()
 assert len(b)==EXPECTED_LEN and h==EXPECTED_SHA,(len(b),h)
 a.output.write_bytes(b); print(len(b),h)
if __name__=="__main__": main()
