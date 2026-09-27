#!/usr/bin/env python3
"""Generate an XGO Arcade game-ROM compatibility manifest from exact bisrv.asd.

The extractor is anchored at the BIN-closed stock FBA driver pointer table.
It records game-specific ROM descriptors only. Parent/board archive dependency
ownership remains metadata on each driver and is not flattened into the game ZIP.
"""
import argparse, hashlib, json, struct
from collections import Counter

DRIVER_TABLE_FILE = 0x00A3D7F8
DRIVER_COUNT = 1438
TARGET_SYSTEMS = {
    "CPS1": "CPS1",
    "CPS1 / QSound": "CPS1",
    "CPS2": "CPS2",
    "PGM": "IGS",
    "Neo Geo": "NEOGEO",
}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("firmware")
    ap.add_argument("output")
    a=ap.parse_args()
    b=open(a.firmware,"rb").read()
    u32=lambda o: struct.unpack_from("<I",b,o)[0]

    def cstr(addr):
        o=addr-0x80000000
        if o < 0 or o >= len(b): raise ValueError(f"bad string pointer {addr:#x}")
        e=b.find(b"\0",o,o+256)
        if e < 0: raise ValueError(f"unterminated string {addr:#x}")
        return b[o:e].decode("ascii")

    def roms(addr,count):
        o=addr-0x80000000; out=[]
        for i in range(count):
            r=b[o+i*44:o+(i+1)*44]
            if len(r)!=44: raise ValueError("ROM table outside firmware")
            name=r[:32].split(b"\0",1)[0].decode("ascii")
            size,crc,typ=struct.unpack_from("<III",r,32)
            # Empty descriptor slots are legitimate in stock FB Alpha tables.
            if not name and (size or crc or typ):
                raise ValueError(f"nameless non-empty ROM record {addr:#x}+{i}")
            out.append({"name":name,"size":size,"crc":crc,"type":typ,
                        "optional":bool(typ & (1<<27))})
        return out

    def constructed(ws,start=0):
        for i in range(start,len(ws)):
            w=ws[i]
            if w>>26 != 0x0f: continue
            rt=(w>>16)&31; hi=w&0xffff
            for x in ws[i+1:min(i+8,len(ws))]:
                if x>>26==0x09 and ((x>>21)&31)==rt:
                    imm=x&0xffff
                    if imm&0x8000: imm-=0x10000
                    yield ((hi<<16)+imm)&0xffffffff

    def direct(cb):
        o=cb-0x80000000; ws=[u32(o+i) for i in range(0,0x50,4)]
        counts=[w&0xffff for w in ws if w>>26==0x0b and (w&0xffff)!=0x80]
        if not counts: raise ValueError(f"no direct count at {cb:#x}")
        count=counts[0]
        for addr in constructed(ws):
            if 0x80A00000 <= addr < 0x80C40000:
                try:
                    rr=roms(addr,count)
                    if rr: return addr,count,rr
                except (ValueError,UnicodeDecodeError):
                    pass
        raise ValueError(f"no direct ROM table at {cb:#x}")

    def ext_game(cb):
        o=cb-0x80000000; ws=[u32(o+i) for i in range(0,0x90,4)]
        if not (ws[0]>>26==0x0b and (ws[0]&0xffff)==0x80):
            raise ValueError(f"not STDROMPICKEXT form {cb:#x}")
        # Pinned compiler form: normal/game count is sltiu at callback +0x28.
        count=ws[10]&0xffff
        for addr in constructed(ws,16):
            if 0x80A00000 <= addr < 0x80C40000:
                try:
                    rr=roms(addr,count)
                    if rr: return addr,count,rr
                except (ValueError,UnicodeDecodeError):
                    pass
        raise ValueError(f"no EXT game ROM table at {cb:#x}")

    drivers=[]
    for index in range(DRIVER_COUNT):
        dp=u32(DRIVER_TABLE_FILE+index*4)
        if not dp: raise ValueError(f"early null driver pointer at {index}")
        o=dp-0x80000000
        system=cstr(u32(o+0x1c))
        if system not in TARGET_SYSTEMS: continue
        name=cstr(u32(o))
        parent=cstr(u32(o+4)) if u32(o+4) else None
        board=cstr(u32(o+8)) if u32(o+8) else None
        cb=u32(o+0x40)
        first=u32(cb-0x80000000)
        addr,count,rr = ext_game(cb) if (first>>26==0x0b and (first&0xffff)==0x80) else direct(cb)
        drivers.append({
            "index":index,"family":TARGET_SYSTEMS[system],"system":system,
            "name":name,"parent":parent,"board":board,
            "rom_info_callback":f"0x{cb:08X}",
            "game_rom_table":f"0x{addr:08X}","roms":rr,
        })

    counts=Counter(x["family"] for x in drivers)
    if not drivers:
        raise ValueError("no target Arcade drivers discovered")
    missing=[family for family in set(TARGET_SYSTEMS.values()) if counts[family] == 0]
    if missing:
        raise ValueError(f"target families missing from extraction: {sorted(missing)}")
    identities=[(x["family"],x["name"]) for x in drivers]
    if len(identities) != len(set(identities)):
        raise ValueError("duplicate family+driver identity in extraction")

    out={
        "schema":1,
        "firmware_sha256":hashlib.sha256(b).hexdigest(),
        "driver_table_runtime":"0x80A3D7F8",
        "driver_count":DRIVER_COUNT,
        "scope":"game-specific ROM descriptors; parent/board dependencies retained as metadata",
        "drivers":drivers,
    }
    raw=json.dumps(out,separators=(",",":"),sort_keys=True).encode()
    open(a.output,"wb").write(raw)
    print(f"drivers={len(drivers)} counts={dict(counts)}")
    print(f"firmware_sha256={out['firmware_sha256']}")
    print(f"manifest_sha256={hashlib.sha256(raw).hexdigest()} bytes={len(raw)}")

if __name__=="__main__":
    main()
