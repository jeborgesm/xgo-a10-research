#!/usr/bin/env python3
"""Descriptor contract for XGO stock Arcade Refresh.

Family selection is authoritative from the input directory. The worker must
not infer CPS/IGS/NeoGeo family from ROM ZIP contents or ZFB bytes.
"""
FAMILIES = {
    "cps1": {
        "list_id": 7,
        "input_root": "/ARCADE/CPS1",
        "catalog": ("mswb7.tax", "msdtc.nec", "mfpmp.bvs"),
    },
    "cps2": {
        "list_id": 8,
        "input_root": "/ARCADE/CPS2",
        "catalog": ("kjbyr.tax", "djoin.nec", "ke89a.bvs"),
    },
    "igs": {
        "list_id": 9,
        "input_root": "/ARCADE/IGS",
        "catalog": ("subst.tax", "aepic.nec", "sensc.bvs"),
    },
    "neogeo": {
        "list_id": 10,
        "input_root": "/ARCADE/NEOGEO",
        "catalog": ("rmapi.tax", "pcadm.nec", "ntdll.bvs"),
    },
}

COMMON = {
    "runtime_zip_root": "/ARCADE/bin",
    "zfb_root": "/ARCADE",
    "source_dir": "import",
    "art_dir": "art",
    "meta_dir": "meta",
    "source_ext": ".zip",
    "wrapper_ext": ".zfb",
    "preview_width": 144,
    "preview_height": 208,
    "preview_bytes": 0xEA00,
    "preview_format": "RGB565 little-endian",
    "art_exts": (".jpg", ".jpeg"),
    "meta_ext": ".txt",
    "append_only": True,
    "family_order": ("cps1", "cps2", "igs", "neogeo"),
    # Deliberately absent: guessed frontend cache addresses.
}

def validate():
    assert COMMON["preview_width"] * COMMON["preview_height"] * 2 == COMMON["preview_bytes"]
    assert tuple(FAMILIES) == COMMON["family_order"]
    assert [FAMILIES[k]["list_id"] for k in COMMON["family_order"]] == [7, 8, 9, 10]
    assert len({FAMILIES[k]["catalog"] for k in FAMILIES}) == 4
    assert all(len(v["catalog"]) == 3 for v in FAMILIES.values())
    assert all(v["input_root"].startswith("/ARCADE/") for v in FAMILIES.values())
    assert "count_cache" not in COMMON
    assert all("count_cache" not in v for v in FAMILIES.values())

if __name__ == "__main__":
    validate()
    for name in COMMON["family_order"]:
        print(name, FAMILIES[name])
