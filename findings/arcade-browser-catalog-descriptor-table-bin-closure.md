# Arcade browser catalog descriptor table — exact BIN closure

Date: 2026-09-26
Branch: `research-arcade-refresh-four-family`
Status: **BIN descriptor-table closure; live-state/cache target remains OPEN**

## Exact current firmware

Current analysis uses the project `bios/bisrv.asd` image from the supplied XGo analysis archive.

Direct binary inspection closes the stock resource-name pointer table used by the browser.

The string records are contiguous:
- GBA triplet strings at runtime `0x809A30EC..0x809A310F`;
- CPS1 at `0x809A3110..0x809A3133`;
- CPS2 at `0x809A3134..0x809A3157`;
- IGS at `0x809A3158..0x809A317B`;
- NeoGeo at `0x809A317C..0x809A319F`.

The pointer table at runtime/raw `0x80A3C3xx / 0x00A3C3xx` contains three consecutive pointers per family.

Exact family triplet pointer bases:
- GBA: `0x80A3C374`
- CPS1: `0x80A3C380`
- CPS2: `0x80A3C38C`
- IGS: `0x80A3C398`
- NeoGeo: `0x80A3C3A4`

Resolved strings:

```
GBA
  vfnet.tax
  htuiw.nec
  sppnp.bvs

CPS1
  mswb7.tax
  msdtc.nec
  mfpmp.bvs

CPS2
  kjbyr.tax
  djoin.nec
  ke89a.bvs

IGS
  subst.tax
  aepic.nec
  sensc.bvs

NEOGEO
  rmapi.tax
  pcadm.nec
  ntdll.bvs
```

This independently confirms the XGO-native family order GBA -> CPS1 -> CPS2 -> IGS -> NeoGeo and the four-family catalog mapping used by the Refresh branch.

## Important cache result

A direct search of the nearby firmware data does **not** reveal literal pointers for hypothetical Arcade count-cache addresses such as `0x80D2897C` and onward. The nearby data region contains the known console base/count pointer evidence but no corresponding hard-coded Arcade continuation.

Therefore the console 8-byte count-cache progression must not be extrapolated into Arcade.

The Arcade browser evidently obtains at least part of its per-family state through indexed/table-driven code rather than four obvious family-specific absolute literals. The correct next target is the browser code that consumes the descriptor pointer base and computes the selected family state.

## Consequence for Test04 freeze

Test04's post-Refresh hard freeze remains consistent with stale resident frontend state after a valid on-disk catalog mutation. Reboot succeeds because it reconstructs that state from disk.

However, there is still no BIN authorization to write `0x80D2897C`, `0x80D28984`, etc.

The next closure must identify the actual browser state calculation/lifecycle or reuse a native lifecycle that rebuilds it. Do not add a guessed cache poke.
