# Test55 — CLASSIC missing page resource candidate

Date: 2026-09-10
Branch: `research-game-metadata-enrichment`

## Trigger

Test54 and Test54b both failed on hardware: changing the bottom text renderer path did not alter the persistent garbled/scrambled region on the CLASSIC page.

The investigation therefore moved from text rendering to the page-art/resource layer.

## Stronger root-cause lead

The first-class CLASSIC firmware setup writes the list-11 page-art pointer to:

```text
Resources/clssic.r56
```

The stock page-art table at `0x80a3c428` is one pointer per list. Stock entries resolve to files such as:

```text
fixas.ctp
drivr.ers
icuin.cpl
xajkg.hsp
qwave.bke
irftp.ctp
hctml.ers
dsuei.cpl
uycgf.kep
alkcn.bck
```

Direct inspection of the original XGO analysis archive shows these stock resources are each exactly 614,400 bytes, which is `640 * 480 * 2`.

Decoding `alkcn.bck` as little-endian RGB565 at 640x480 yields the expected Neo Geo full-screen page background, confirming the table is a full-screen page/background resource table rather than the game-cover thumbnail table.

Critically, `Resources/clssic.r56` does **not** exist in the original XGO resource archive.

The later normalized Test47/Test52/Test53 cumulative packages preserved the firmware pointer to `clssic.r56` but do not include a `Resources/clssic.r56` file. Therefore CLASSIC has been requesting a nonexistent full-screen page resource since the first-class list was introduced.

This is a plausible explanation for a persistent stale/scrambled region that is unaffected by the bottom text draw call.

## Candidate design

Test55 starts from the clean, hardware-passed Test53 cumulative package. It does **not** include the failed Test54/Test54b renderer hooks.

No firmware or core bytes are changed.

The only functional addition is:

```text
Resources/clssic.r56
```

with the exact stock page-resource contract:

- 640x480 pixels;
- RGB565;
- little-endian 16-bit pixels;
- row-major;
- exactly 614,400 bytes.

For the hardware probe, the resource is derived from a known-good stock XGO page background with the stock wordmark area replaced by `CLASSIC`.

## Protected identities

Test53 firmware remains:

```text
40083d8d05297bef6fd4dc6122f09151ddba6c6db1c4060b917ecbc2ee40c217
```

Protected MAME2000 core remains:

```text
60a62e463fd6faf92744a7be666602dd1621b9fd706f90d20e3b55ee3382bb1e
```

Test55 candidate ZIP:

```text
xgo-classic-test55-missing-page-resource-fix.zip
SHA-256 cb54e85dec2d9df8eae493ab6e6fb957b994a46451407f1d4de313bc3d5c5b80
```

New page resource:

```text
Resources/clssic.r56
size 614400
SHA-256 c4a29d919b6022d11c8bcc05aba98dcb92ef80398db8b2b7988c6a15c9b8d8da
```

## Hardware gate

1. Install Test55 over the current card.
2. Open CLASSIC immediately.
3. Check whether the persistent garbled/scrambled region disappears.
4. Confirm the CLASSIC page background is rendered cleanly.
5. Verify one CLASSIC game launch.
6. Verify Refresh still works.
7. Verify CLASSIC Save/Load still works.
8. Verify stock console and Arcade pages remain unchanged.

If the garble disappears, the missing page resource is the root cause and the renderer-hook line of investigation is closed.