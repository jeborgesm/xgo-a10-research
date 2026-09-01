# DY19 Tadpole as a Base for an XGO PC Configuration Tool

Status: **DY19 Tadpole contains the exact XGO-family game-list resource filenames and can likely serve as a code base for XGO list management, but its device profile must not be used unchanged because at least one menu/list-ID ordering differs from the XGO executable.**

## Why this matters

One long-term XGO goal is a desktop application that can:

- add/remove games from the real system lists;
- rebuild thumbnail wrappers;
- edit per-game button mappings;
- validate and reseal modified `bisrv.asd` images;
- eventually manage safer firmware patches.

An existing DY19 fork of Tadpole already solves much of the generic SF2000-family card-management problem.

## Exact resource-map overlap

`Trademarked69/dy19-tadpole` defines these game-list triplets:

```text
FC      rdbui.tax  fhcfg.nec  nethn.bvs
SFC     urefs.tax  adsnt.nec  xvb6c.bvs
MD      scksp.tax  setxa.nec  wmiui.bvs
GB      vdsdc.tax  umboa.nec  qdvd6.bvs
GBC     pnpui.tax  wjere.nec  mgdel.bvs
GBA     vfnet.tax  htuiw.nec  sppnp.bvs
CPS1    mswb7.tax  msdtc.nec  mfpmp.bvs
CPS2    kjbyr.tax  djoin.nec  ke89a.bvs
NEOGEO  rmapi.tax  pcadm.nec  ntdll.bvs
IGS     subst.tax  aepic.nec  sensc.bvs
```

These are the same opaque filenames independently recovered from the XGO firmware and preserved card.

The probability of this entire filename set matching by coincidence is effectively negligible. The DY19 tool is therefore operating on the same vendor resource-layout fork family as XGO.

## List-file algorithm also matches XGO

The DY19 Frogtool code writes list files as:

```text
uint32 count
uint32 offsets[count]
NUL-terminated string data
```

with offsets relative to the string-data area.

That is the same format independently reconstructed from XGO files.

Therefore its core list writer is directly relevant to XGO.

## Important XGO-specific difference

The XGO executable's actual menu/list resource table at `0x80a3c32c` is:

```text
0   tsmfk.tax / tsmfk.tax / tsmfk.tax
1   FC
2   SFC
3   MD
4   GB
5   GBC
6   GBA
7   CPS1
8   CPS2
9   subst.tax / aepic.nec / sensc.bvs    = IGS/PGM curated group
10  rmapi.tax / pcadm.nec / ntdll.bvs    = Neo Geo
11  None / None / None
```

The DY19 Tadpole higher-level configuration assigns:

```text
9  NEOGEO
10 IGS
```

So at least those two logical IDs are reversed relative to XGO.

This is precisely the kind of subtle mismatch that could make a tool appear to work while corrupting favorites/history/shortcut references.

## Recommended direction

Do not use stock SF2000 Tadpole or the DY19 fork blindly on the preserved XGO card.

Instead, the practical path is to create an **XGO device profile/fork** using DY19 Tadpole's existing components:

```text
Reusable essentially as-is:
  Zxx thumbnail/container creation
  list-file serialization
  file backup behavior
  cover-art workflow
  generic UI scaffolding

XGO-specific replacements/additions:
  exact menu/list IDs
  exact XGO resource-role map
  fifth Arcade placeholder handling
  Favorites/History preservation rules
  XGO per-game 48-byte .kmp editor
  XGO bisrv.asd hash recognition
  LCFG reseal using tools/reseal_lcfg.py
  explicit block on generic Firmware.upk operations
  future Player-2 diagnostics
```

## Relevance to adding games to main lists

This finding means that adding games directly to the real XGO FC/SFC/MD/GB/GBC/GBA/CPS1/CPS2/IGS/NeoGeo menus does **not** require custom firmware.

It is primarily a card-database-management problem, and most of the necessary implementation already exists in open-source DY19 tooling.

That goal can therefore be separated from the more difficult emulator-core replacement goal.

## Confidence

### CONFIRMED

- DY19 Tadpole uses the exact XGO opaque list filenames;
- its list serialization algorithm matches the XGO format;
- XGO executable list IDs 9 and 10 are IGS/PGM then Neo Geo;
- DY19 Tadpole's higher-level IDs reverse those two positions;
- therefore the DY19 codebase is highly reusable but its device profile is not drop-in safe for XGO.

### STRONG CONCLUSION

An XGO-specific Tadpole/Frogtool fork is likely much less work than building a desktop card manager from scratch.

### OPEN

- whether other DY19-specific menu shortcut/resource IDs also differ;
- whether DY19 multicore patches can be retargeted to XGO's shifted function addresses;
- whether an XGO GUI should remain a Tadpole fork or extract the reusable file-format logic into a new cleaner application.
