# Arcade Test14 — enriched marker/catalog identity correction

Date: 2026-09-28
Branch: `research-arcade-refresh-four-family`
Status: hardware candidate

## Evidence that changed the diagnosis

The exact Test13 IGS capture proved `The Gladiator.zfb` itself was correct: its 59,904-byte preview prefix matched the generated RGB565 byte-for-byte and its payload embedded `theglad.zip`. The failure was publication identity: `.refresh-set/theglad.zfb` caused the catalog helper to append `theglad.zfb / theglad / theglad`, while the real enriched wrapper was `The Gladiator.zfb`.

This can also be latent in CPS1/CPS2: the prior hardware probes used numeric shortnames 1941 and 1944, so filename-derived and metadata-derived visible identity were not distinguished by those tests.

## Mechanical fix

Finalizer keeps ROM shortname identity for import/bin ZIP paths. Only marker construction changes. At +0x21F0/+0x21F4, marker append source is retargeted from the ROM stem to the already-built display-title buffer at 0x87600400.

The exact bounded append helper at +0x2398 reads but does not modify a1, so the preceding 0x140 capacity remains live. No finalizer ABI change is required.

Applied identically to CPS1, CPS2, IGS and NeoGeo. No validator policy, quarantine, temp-art workspace, or catalog-helper redesign.

Expected IGS identity:
```
source/runtime ZIP: theglad.zip
outer wrapper:      The Gladiator.zfb
publication marker: .refresh-set/The Gladiator.zfb
catalog slot0:      The Gladiator.zfb
visible title:      The Gladiator
```

Candidate: `xgo-arcade-test14-enriched-marker-identity.zip`
ZIP SHA256: `11911120695532938ff37a57c9ea3d2ca93ce6854a621eeb15a0105fc1fb8fd9`

Family refresh hashes:
- CPS1 `8cb4f3ca4b83f5b523682698a41e67bf450e6a14a3d9ebc44ad8e8bd27b817a6`
- CPS2 `e7e776ee5c7247ab2e4dd1c3e00cd92ed0f3d07359c1fc8d9c718ab015885a9c`
- IGS `6042520a3348ce7502c99b2546120dcc7b59fd289c47898ddc4c9a169330a6ac`
- NeoGeo `4f6b04aef1265f07a07578b0fb0cca95add826655467ccb1f965fdd34831b759`
