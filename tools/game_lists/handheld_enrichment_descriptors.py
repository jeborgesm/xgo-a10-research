#!/usr/bin/env python3
"""Descriptor record for GB/GBC/GBA stock-enrichment propagation.

This intentionally does not emit executable helpers.  It freezes the system-
specific substitutions that will be applied to the already HW-proven
Test74/Test75 materializer/catalog implementation after selective Test125
routing is hardware-proven.
"""
SYSTEMS={
 "gb":{
  "command":3,"root":"/GB","import_ext":".gb","wrapper_ext":".zgb",
  "catalog":("vdsdc.tax","umboa.nec","qdvd6.bvs"),"count_cache":0x80D28964,
 },
 "gbc":{
  "command":4,"root":"/GBC","import_ext":".gbc","wrapper_ext":".zgb",
  "catalog":("pnpui.tax","wjere.nec","mgdel.bvs"),"count_cache":0x80D2896C,
 },
 "gba":{
  "command":5,"root":"/GBA","import_ext":".gba","wrapper_ext":".zgb",
  "catalog":("vfnet.tax","htuiw.nec","sppnp.bvs"),"count_cache":0x80D28974,
 },
}
COMMON={
 "preview_width":144,
 "preview_height":208,
 "preview_bytes":0xEA00,
 "preview_format":"RGB565 little-endian",
 "art_exts":(".jpg",".jpeg"),
 "meta_ext":".txt",
 "source_dir":"import",
 "art_dir":"art",
 "meta_dir":"meta",
 "retain_sources":True,
 "initial_no_overwrite":True,
}
def validate():
 assert COMMON["preview_width"]*COMMON["preview_height"]*2==COMMON["preview_bytes"]
 assert sorted(v["command"] for v in SYSTEMS.values())==[3,4,5]
 assert len({v["root"] for v in SYSTEMS.values()})==3
 assert all(v["wrapper_ext"]==".zgb" for v in SYSTEMS.values())
 assert len({v["catalog"] for v in SYSTEMS.values()})==3
 assert [SYSTEMS[k]["count_cache"] for k in ("gb","gbc","gba")]==[0x80D28964,0x80D2896C,0x80D28974]
if __name__=="__main__":
 validate()
 for name,d in SYSTEMS.items():
  print(name,d)
