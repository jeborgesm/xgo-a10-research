# Four-family Arcade compatibility manifest — first complete extraction and 1941 fixture proof

Date: 2026-09-26
Branch: `research-arcade-refresh-four-family`
Status: **OFFLINE GENERATOR + VERIFIER PROVEN; on-device integration not yet complete**

## Exact extraction result

The deterministic generator was run against the preserved current
`bios/bisrv.asd`.

Firmware SHA-256:

```
869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf
```

The generator successfully emitted all 678 target compiled drivers:

```
CPS1    154   (includes CPS1 / QSound)
CPS2    232
IGS      34   (PGM)
NeoGeo  258
total   678
```

No target driver required heuristic whole-binary discovery. Enumeration begins
from the BIN-closed 1438-entry driver pointer table and each target driver's
compiled ROM-info callback.

The first compact JSON manifest produced during the prototype run was 960159
bytes and had SHA-256:

```
49f68be3ee8413b9731024ea99f5dfa8b81952cbab234ec0e066e2172c7062bd
```

That hash describes the prototype emission before the repository generator was
polished with explicit callback/table metadata and sorted JSON keys; it is
recorded only as reproducibility evidence, not as the final package manifest.

## STDROMPICKEXT refinement

The same extended callback form is used beyond PGM, including NeoGeo drivers
such as `nam1975`.

For compatibility of the imported game ZIP, the generator extracts the
normal/game-specific branch. Parent and board archive names are retained from
the BurnDriver object as dependency metadata rather than flattening shared ROMs
into the imported ZIP requirement.

This is important for both PGM and NeoGeo.

## 1941 regression fixture

Two preserved 1941 archives were evaluated by the generated XGO contract.

Known failed Test04-era archive:

```
/mnt/data/1941(1).zip
=> INCOMPATIBLE
=> four unresolved required game ROMs:
   41e_30.rom
   41e_35.rom
   41e_31.rom
   41e_36.rom
```

Known hardware-compatible replacement:

```
/mnt/data/1941(2).zip
=> COMPATIBLE
=> zero unresolved required game ROMs
```

This exactly matches the later physical-XGO observation: replacing only the
runtime 1941 ZIP with the second archive made the unchanged Test04 entry launch
and play.

Therefore the generated-manifest validator correctly separates the known
negative and positive CPS1 fixtures.

## Matching rules implemented by the offline verifier

For each non-empty, non-optional game descriptor:
1. search ZIP members by required CRC;
2. if CRC matches, enforce expected size;
3. otherwise accept the stock loader's expected-filename fallback;
4. otherwise mark the descriptor unresolved.

A stem/family with no compiled XGO driver is `UNSUPPORTED`, not compatible.

## Repository implementation

Added:

```
tools/arcade_refresh/generate_xgo_arcade_compat_manifest.py
tools/arcade_refresh/validate_arcade_import_zip.py
```

The generator fails closed if the expected four-family population changes.

## Remaining boundary before Test05

The manifest/validator logic is now proven offline, but the on-device
materializer still needs:
- a compact representation suitable for the helper;
- ZIP central-directory enumeration using an already-proven or audited local
  implementation;
- fail-closed integration before runtime ZIP/ZFB/marker publication;
- recoverable incompatible-source handling (preferred
  `.zip.incompatible` rename still awaits a safe filesystem primitive).

No Test05 is authorized yet.
