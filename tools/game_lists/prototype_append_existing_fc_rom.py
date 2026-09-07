#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib, struct

BASE = {
    'rdbui.tax': ('00a15acd702e97e25d4eb8420c1efbc645a377de928125248f1869dd06449325', 'Bomber Man 2.zfc'),
    'fhcfg.nec': ('984cc22a261c4d80f73193cd073789f03d8848afd07733adabd040cfb9332422', 'Bomber Man 2'),
    'nethn.bvs': ('00cb20e66653eed21b264079ad9c4a5c8915de47de0b4b054c3fbf73d2a3b436', 'Bomber Man 2'),
}

def sha256(data):
    return hashlib.sha256(data).hexdigest()

def append_exact(data, text):
    count = struct.unpack_from('<I', data, 0)[0]
    blob_start = 4 + count * 4
    offsets = data[4:blob_start]
    blob = data[blob_start:]
    encoded = text.encode('utf-8') + b'\0'
    out = struct.pack('<I', count + 1) + offsets + struct.pack('<I', len(blob)) + blob + encoded
    return out, count, blob_start

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('resources', type=Path)
    ap.add_argument('output', type=Path)
    args = ap.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    for name, (expected, text) in BASE.items():
        src = args.resources / name
        data = src.read_bytes()
        actual = sha256(data)
        if actual != expected:
            raise SystemExit(f'{name}: base SHA mismatch: {actual}')
        out, count, blob_start = append_exact(data, text)
        new_count = struct.unpack_from('<I', out, 0)[0]
        new_blob_start = 4 + new_count * 4
        assert new_count == count + 1
        assert out[4:4 + count * 4] == data[4:blob_start]
        assert out[new_blob_start:new_blob_start + len(data) - blob_start] == data[blob_start:]
        new_offset = struct.unpack_from('<I', out, 4 + count * 4)[0]
        assert new_offset == len(data) - blob_start
        dst = args.output / name
        dst.write_bytes(out)
        print(f'{name}: {count}->{new_count} size {len(data)}->{len(out)} sha256 {sha256(out)}')

if __name__ == '__main__':
    main()
