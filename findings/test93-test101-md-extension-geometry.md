# MD Refresh extension-geometry investigation — Tests 93–101

Status: active investigation. Hardware evidence takes precedence over inference.

## Hardware observations

- Test93: MD materializer isolation -> **No New Games**.
- Test94: attempted two-character extension fix -> **No New Games**.
- Test95: bypassed m/d rejection branches -> **No New Games**.
- Test96: bypassed filename gates -> **Refresh Failed**; this proved execution reached farther downstream.
- Test97: bypassed only the second/redundant dot gate at helper offset `0x027C` -> **Games Updated**. Four existing `.md` files were imported. After reboot they appeared in the MD list and were playable. Artwork was absent. Immediate list/count refresh was stale and could hard-lock until reboot.
- Test98: attempted dot-register reload -> **Refresh Failed**. Rejected.
- Test99: helper was byte-identical to Test97 but returned **Refresh Failed** after Test97 had already modified persistent catalog state and generated wrappers had been removed. Treat as confounded/inconclusive, not a regression proof.
- Test100: dynamic extension/stem rewrite -> **Refresh Failed**. Rejected. Offline re-audit found an off-by-one in the replacement stem routine.
- Test101: corrected final-dot stem rewrite -> **Refresh Failed**. Rejected as a hardware candidate.

## Proven extension-filter defect

FC/SFC helper geometry assumes a four-byte suffix `.xxx`:

```
L-4 '.'
L-3 ext[0]
L-2 ext[1]
L-1 ext[2]
```

The cloned MD helper changed comparison characters without changing that geometry, producing the effective expectation:

```
L-4 '.'
L-3 '.'
L-2 'm'
L-1 'd'
```

Relevant MD helper offsets in the Test85 lineage:

```
0x024C  first dot rejection branch
0x0278  compare '.'
0x027C  second/redundant dot rejection branch
0x02A8  compare 'm'
0x02AC  rejection branch
0x02D4  compare 'd'
0x02D8  rejection branch
```

Test97's hardware success after bypassing only `0x027C` is the strongest evidence that the two-character MD extension was incorrectly adapted from the FC/SFC three-character implementation.

## Stem-length defect / artwork hypothesis

The inherited stem helper at approximately `0x0DCC` computes a basename by removing a fixed four-character suffix appropriate for `.nes`/`.sfc`. MD `.md` needs a three-character suffix removed. This can cause an extra basename character to be lost, which would make metadata/art paths fail to match while wrapper creation can still succeed using the black-preview fallback.

Expected correct mapping:

```
Streets of Rage (World).md
 -> stem: Streets of Rage (World)
 -> /MD/meta/Streets of Rage (World).txt
 -> /MD/art/Streets of Rage (World).jpg
 -> /MD/art/Streets of Rage (World).jpeg
```

This explains Test97's combination of playable generated wrappers plus missing artwork, but the artwork-path explanation remains an inference until isolated on hardware.

The shared stem helper is called from more than one point in the materializer (observed calls include `0x02E4` and `0x0524`). Replacing the entire helper, as attempted in Tests100/101, was too invasive.

## Design target

Long-term MD parsing should not assume a fixed extension length. Preferred contract:

1. locate the final dot;
2. derive the stem from bytes before that dot;
3. derive the extension from bytes after it;
4. validate against an explicit whitelist such as `.md`, `.bin`, `.sms`;
5. use the same derived stem for metadata, artwork and wrapper construction.

This avoids exceptional-extension bugs and correctly handles names containing earlier periods, e.g. `Sonic Rev. A.bin`.

However, do **not** jump directly to another rewritten parser. Hardware evidence says Test97 is the only proven foothold.

## Next experiment discipline

Start from the **exact Test97 MD helper**. Preserve its hardware-proven extension gate and all control flow. Change only the inherited fixed stem-length calculation from removal of four suffix bytes to removal of three for the currently proven `.md` input. Audit all callers and path construction offline before producing another hardware candidate.

Only after that minimal change proves artwork/stem behavior should the helper be generalized to final-dot parsing and a 2/3-character whitelist.

## Separate unresolved issue

Test97 also proved a distinct live catalog/cache problem: imported wrappers were playable after reboot, but the MD list/count was stale immediately after Refresh and could hard-lock. Keep this separate from extension/stem work. Compare FC/SFC/MD catalog-helper invalidation sequences before patching it.
