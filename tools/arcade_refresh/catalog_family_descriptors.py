#!/usr/bin/env python3
"""Build-time descriptor contract for the Arcade catalog front end.

This does not emit a firmware candidate. It defines the only family-dependent
inputs allowed into the manifest-reader specialization.
"""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Family:
    key: str
    list_id: int
    manifest: str
    slot0: str
    slot1: str
    slot2: str

FAMILIES=(
 Family("CPS1",7,"/mnt/sda1/ARCADE/CPS1/.refresh-list",
        "/mnt/sda1/Resources/mswb7.tax","/mnt/sda1/Resources/msdtc.nec","/mnt/sda1/Resources/mfpmp.bvs"),
 Family("CPS2",8,"/mnt/sda1/ARCADE/CPS2/.refresh-list",
        "/mnt/sda1/Resources/kjbyr.tax","/mnt/sda1/Resources/djoin.nec","/mnt/sda1/Resources/ke89a.bvs"),
 Family("IGS",9,"/mnt/sda1/ARCADE/IGS/.refresh-list",
        "/mnt/sda1/Resources/subst.tax","/mnt/sda1/Resources/aepic.nec","/mnt/sda1/Resources/sensc.bvs"),
 Family("NEOGEO",10,"/mnt/sda1/ARCADE/NEOGEO/.refresh-list",
        "/mnt/sda1/Resources/rmapi.tax","/mnt/sda1/Resources/pcadm.nec","/mnt/sda1/Resources/ntdll.bvs"),
)

def validate():
    assert tuple(x.list_id for x in FAMILIES)==(7,8,9,10)
    assert len({x.manifest for x in FAMILIES})==4
    assert len({x.slot0 for x in FAMILIES})==4
    assert all(x.manifest.startswith("/mnt/sda1/ARCADE/"+x.key+"/") for x in FAMILIES)
    assert all(len({x.slot0,x.slot1,x.slot2})==3 for x in FAMILIES)
    return True

if __name__=="__main__":
    validate()
    print("PASS four-family Arcade catalog descriptors")
