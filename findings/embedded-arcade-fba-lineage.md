# XGO embedded arcade core: hybrid FB Alpha lineage

Status: **libretro-facing core identity exact; underlying engine ancestry strongly tied to the known SF2000/Data Frog hybrid**.

Firmware fingerprint:

`869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf`

## Exact banner in the XGO firmware

The arcade core string block at approximately ASD offset `0x009a4024` contains the full old FB Alpha libretro option surface and, at `0x009a4a50`, the core identity:

```text
FB Alpha
v0.2.97.42 621e371
iso|zip|7z
```

Adjacent options include:

```text
fba-neogeo-controls-p1
fba-neogeo-controls-p2
fba-neogeo-mode
fba-diagnostic-input
fba-lr-controls-p1
fba-lr-controls-p2
fba-hiscores
fba-sh2-mode
fba-controls-p1
fba-controls-p2
fba-cpu-speed-adjust
fba-aspect
```

and runtime diagnostics include:

```text
[FBA] Archive: %s
[FBA] Parsing archive %s.
[FBA] NeoGeo BIOS missing ...
[FBA] Cannot load this game.
[FBA] Using ROM at index %d with wrong CRC and name %s
[FBA] Cannot find driver.
[FBA] Game %s is not marked as working
```

This is the **old full FB Alpha libretro API**, not FBNeo branding and not the `fbalpha2012_*` option namespace used by the frozen FBA2012 core.

## Exact wrapper commit

The short SHA resolves in the historical `Aftnet/fbalpha` repository to:

```text
621e371e553eb7814f12504b23f78de4715b7d11
```

Date:

```text
2017-08-16 15:49:58 UTC
```

Commit message:

```text
Merge pull request #149 from retro-wertz/patch-1
PGM - single pcb boards, missing bios issue
```

Therefore the libretro-facing FBA wrapper compiled into XGO is tied to an exact August 2017 FB Alpha source revision.

## Important: the banner does not necessarily date the emulation engine

Existing SF2000 reverse-engineering work documents a nonstandard Data Frog arcade build: an older Final Burn Alpha engine/ROM-set lineage close to `v0.2.96.86`, combined with a libretro interface from `v0.2.97.42` / `621e371`, plus additional vendor/compiler modifications.

XGO reproduces the same distinctive libretro-facing identity:

```text
FB Alpha
v0.2.97.42 621e371
```

and the same old `fba-*` frontend option vocabulary.

Combined with the already-confirmed XGO/SF2000 firmware ancestry and the unusual XGO arcade ROM/database fossils, this is **strong evidence** that XGO inherited the same hybrid Data Frog arcade architecture rather than embedding an untouched 2017 upstream FBA binary.

Accordingly:

- **CONFIRMED:** the XGO arcade libretro wrapper identifies as FB Alpha `v0.2.97.42`, Git `621e371`.
- **CONFIRMED:** `621e371` is an August 2017 historical FB Alpha commit.
- **STRONG EVIDENCE:** the underlying arcade engine/driver set is older and vendor-customized, analogous to the documented SF2000 hybrid.
- **NOT justified:** claiming XGO has full stock upstream FBA `v0.2.97.42` ROM compatibility merely from the banner.

## Why this explains the card archaeology

The card contains a highly curated arcade library, duplicated Neo Geo BIOS residue, stale `.skp` quick-start states, separate PGM/CPS/Neo Geo metadata tables, and ROM-set artifacts that do not behave like a clean modern FB Alpha or FBNeo set.

A hybrid engine plus later libretro wrapper explains this cleanly:

```text
older FBA driver/ROM-set base
        +
newer 2017 libretro wrapper/options
        +
Data Frog HC15xx integration
        +
XGO-specific frontend databases/resources
```

This also makes arcade a potentially high-value future core-replacement target: upgrading the wrapper alone would not be enough; replacing the full arcade engine with a known HC15xx-capable FBA2012/FBNeo-family core could materially change supported ROM sets and driver behavior.

## Compatibility warning for the PC configurator

Because the stock main-list arcade database and ZIP set are tied to this old/hybrid driver lineage, a future PC tool must treat an arcade core upgrade differently from NES/FCEUmm.

For NES, existing ROM content can usually be passed directly to a newer FCEUmm.

For arcade, switching core families may require **ROM-set validation/rebuilding** against the replacement core's driver database. The configurator should therefore model arcade core choice and ROM-set compatibility together rather than assuming a ZIP that works on stock XGO will work unchanged on a newer core.
