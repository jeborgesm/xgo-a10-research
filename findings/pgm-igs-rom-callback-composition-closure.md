# PGM/IGS ROM callback composition — BIN + source-family closure

Date: 2026-09-26
Branch: `research-arcade-refresh-four-family`
Status: **CLOSED for compatibility-manifest extraction**

## Why PGM looked different

The XGO `orlegend` ROM-info callback at `0x80493038` is the compiled form of
FB Alpha's `STDROMPICKEXT(orlegend, orlegend, pgm)` pattern rather than a
different loader.

The exact preserved FB Alpha 0.2.97.42 source macro defines two index spaces:

```
i < 0x80:
    game-specific Info1RomDesc[i]
    if i exceeds game table -> emptyRomDesc

i >= 0x80:
    i &= 0x7f
    shared Info2RomDesc[i]
    out of range -> NULL / return 1
```

For PGM, `Info2 = pgm`.

The corresponding XGO BIN at `0x80493038` directly implements the same split:
- tests `i < 0x80`;
- normal range uses the game-specific table at `0x80B1746C` for orlegend;
- high-bit range masks with `0x7f` and uses the shared table at
  `0x80B173E8`;
- the shared table contains the three PGM board ROM descriptors.

## Exact shared PGM descriptors

The XGO common table at `0x80B173E8` contains three 44-byte records:
- `pgm_p01s.rom`
- `pgm_t01s.rom`
- `pgm_m01s.rom`

Their exact length/CRC/type values are recoverable directly from BIN.

The game-specific orlegend table begins at `0x80B1746C`.

## Sparse-index consequence

This macro deliberately leaves the normal index range between the end of a
game's own ROM table and index `0x7f` as empty descriptors. The shared board
ROMs then occupy logical indices `0x80..`.

That explains the initially surprising callback control flow: the callback is
not trying to concatenate two physical tables into one dense list.

The stock archive loader tolerates zero/empty descriptors and marks entries with
zero type/length/CRC as satisfied. The shared board-ROM descriptors are therefore
part of the driver's logical ROM stream without being part of the game's ZIP
payload itself.

## Compatibility-gate consequence

The manifest must preserve **dependency ownership**, not merely flatten every
required descriptor into the imported game ZIP.

For PGM:
- game-specific required descriptors validate against the imported
  `<stem>.zip`;
- shared PGM board descriptors are a board-ROM dependency and may be satisfied
  from the stock PGM board archive.

The preserved SD inventory independently contains:

```
/bios/pgm.zip
```

Likewise NeoGeo has a preserved shared board archive:

```
/bios/neogeo.zip
```

Therefore an imported PGM/NeoGeo game must not be rejected merely because
shared BIOS/board ROM payloads are absent from the game's own ZIP.

## Manifest schema refinement

Per driver, record:
- family;
- short name;
- parent name if present;
- board-ROM name if present;
- game-specific descriptor stream;
- shared/board descriptor stream where the compiled callback exposes one;
- original type flags.

Validation should mirror stock archive search ownership:
1. imported game archive;
2. parent archive when applicable and available;
3. board-ROM archive when applicable;
4. CRC-first, then expected-name fallback;
5. optional descriptors do not reject the game;
6. unresolved required game/available-dependency descriptors reject.

For the Refresh import gate, the critical distinction is that a missing
game-specific payload is an incompatible import, while a shared board dependency
is not evidence that the imported ZIP itself is malformed.

## Evidence classification

- exact XGO callback branches/tables: BIN;
- exact `STDROMPICKEXT` semantics: UP/SRC from pinned 621e371 ancestry;
- instruction/source correspondence: BIN+SRC;
- `/bios/pgm.zip` and `/bios/neogeo.zip` presence: preserved SD inventory;
- PGM special-composition boundary: CLOSED.

This removes the last family-layout blocker to a four-family manifest generator.
