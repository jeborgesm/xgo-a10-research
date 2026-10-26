#!/usr/bin/env python3
"""Read-only XGO FC per-ROM .kmp mapping audit.

48 bytes: six physical X,Y,L,A,B,R records for P1, then six for P2.
low16 = target libretro joypad ID; bit16 = turbo. Physical SELECT/START
are separate fixed serial slots, but a remappable button may TARGET
logical SELECT (ID2) or START (ID3) through a custom .kmp.

An actual loaded game profile is only proved by matching the exact
ROM filename, FC/save path, and runtime selection; this tool reads files,
not running XGO memory. No firmware, ROM, or .kmp is written.
"""
import argparse
import json
import struct
from pathlib import Path

BUTTONS=("X","Y","L","A","B","R")
TARGETS={0:"NES B / FIRE",2:"SELECT",3:"START",8:"NES A / JUMP"}

def decode(blob, provenance):
    if len(blob)!=48:
        raise ValueError(f".kmp requires exactly 48 bytes; got {len(blob)}")
    words=struct.unpack("<12I",blob)
    players={}
    for player in (1,2):
        rows=[]
        for physical, raw in zip(BUTTONS,words[(player-1)*6:player*6]):
            selector=raw&0xffff
            rows.append(dict(physical=physical,raw=f"0x{raw:08x}",
                selector=selector,target=TARGETS.get(selector,f"OTHER({selector})"),
                turbo=bool(raw&0x10000),
                unknown_high_bits=bool(raw&0xfffe0000)))
        players[str(player)]=rows
    p2=players["2"]
    find=lambda target:[r["physical"] for r in p2 if r["selector"]==target]
    return dict(evidence="PROFILE_BYTES",provenance=provenance,players=players,
        p2_jump_candidates=find(8),p2_fire_candidates=find(0),
        p2_start_targets=find(3),p2_select_targets=find(2),
        limits=[
            "Profile bytes do not prove the running XGO loaded this profile.",
            "Physical START and SELECT serial bits are not remapped by these records.",
            "Custom face/shoulder mappings may target logical START/SELECT; whether "
            "that reaches a particular frontend pause path requires separate proof.",
            "This decoder does not capture any live host-received serial bit."])

def expected_path(fc_root,rom_filename):
    if not rom_filename or Path(rom_filename).name!=rom_filename or "/" in rom_filename or "\\" in rom_filename:
        raise ValueError("ROM name must be the exact basename including extension")
    return fc_root/"save"/(rom_filename+".kmp")

def read_profile(path):
    path=Path(path)
    if not path.is_file():
        return dict(evidence="NO_FILE_AT_SPECIFIED_PATH",expected=str(path),
            mapping="UNKNOWN unless exact FC root and active ROM basename are verified",
            conditional="If the launcher actually checks this exact path and there "
            "is no profile, its FC embedded fallback table is used.")
    return decode(path.read_bytes(),str(path))

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    group=p.add_mutually_exclusive_group(required=True)
    group.add_argument("--kmp",type=Path,help="existing exact profile (read only)")
    group.add_argument("--fc-root",type=Path,help="FC system root on mounted SD")
    p.add_argument("--rom-filename",help="exact selected filename, extension included")
    p.add_argument("--json",action="store_true")
    a=p.parse_args(argv)
    if a.kmp:
        if a.rom_filename:p.error("--rom-filename only applies to --fc-root")
        path=a.kmp
    else:
        if not a.rom_filename:p.error("--fc-root requires --rom-filename")
        path=expected_path(a.fc_root,a.rom_filename)
    result=read_profile(path)
    if a.json:
        print(json.dumps(result,indent=2))
    elif "players" not in result:
        print(result["evidence"],result["expected"])
        print(result["mapping"])
        print(result["conditional"])
    else:
        print("Profile:",result["provenance"])
        for player,rows in result["players"].items():
            print("PLAYER",player)
            for row in rows:
                print(f"  {row['physical']:6} -> {row['target']:16} "
                      f"turbo={row['turbo']} raw={row['raw']}")
        for key in ("p2_jump_candidates","p2_fire_candidates",
                    "p2_start_targets","p2_select_targets"):
            print(key+":",",".join(result[key]) or "(none)")
        print("CAUTION: profile content does not prove it was loaded at runtime.")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
