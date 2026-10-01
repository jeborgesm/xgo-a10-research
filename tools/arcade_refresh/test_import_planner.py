#!/usr/bin/env python3
from import_planner import *

def E(**kw):
    d=dict(runtime_zip_exists=False,runtime_zip_identical=False,zfb_exists=False,
           zfb_driver=None,target_family_has_zfb=False,other_family_has_zfb=False)
    d.update(kw); return Existing(**d)

p=plan("dino.zip","Cadillacs.zfb",E())
assert p.decision is Decision.IMPORT and p.copy_zip and p.create_zfb and p.append_catalog

p=plan("dino.zip","Cadillacs.zfb",E(runtime_zip_exists=True,runtime_zip_identical=True))
assert p.decision is Decision.IMPORT and not p.copy_zip and p.create_zfb

p=plan("dino.zip","Cadillacs.zfb",E(runtime_zip_exists=True,runtime_zip_identical=False))
assert p.decision is Decision.FAIL_ZIP_COLLISION

p=plan("dino.zip","Cadillacs.zfb",E(zfb_exists=True,zfb_driver="other.zip"))
assert p.decision is Decision.FAIL_ZFB_COLLISION

p=plan("dino.zip","Cadillacs.zfb",E(zfb_exists=True,zfb_driver="dino.zip",
    runtime_zip_exists=True,runtime_zip_identical=True,target_family_has_zfb=True))
assert p.decision is Decision.NO_CHANGE

p=plan("dino.zip","Cadillacs.zfb",E(zfb_exists=True,zfb_driver="dino.zip",
    runtime_zip_exists=True,runtime_zip_identical=True,other_family_has_zfb=True))
assert p.decision is Decision.FAIL_CROSS_FAMILY

p=plan("dino.zip","Cadillacs.zfb",E(target_family_has_zfb=True))
assert p.decision is Decision.FAIL_ZFB_COLLISION

print("PASS Arcade import planner collision/idempotence matrix")
