# XGO ARCHEOLOGY — HANDOFF
## Four-family Arcade Refresh / Test15 IGS runtime-transition investigation
## Current stopping point: CPS1/CPS2 direct controls vs IGS post-publication locks
## Date: 2026-09-29

Resume XGO Archeology from branch:

`research-arcade-refresh-four-family`

Repository:

`jeborgesm/xgo-a10-research`

DO NOT restart the investigation.

Read this handoff completely before doing anything. Also obey:
- `HANDOFF-CURRENT.md`
- `docs/MODIFICATION-CONTINUITY-PROTOCOL.md`
- `docs/REUSE-FIRST-ENGINEERING-INDEX.md`
- `findings/gb-gbc-gba-refresh-branch-contract.md`

The immediate task is NOT more CLASSIC archaeology, NOT validator redesign, and NOT artwork cleanup.

The immediate task is:

> Mechanically compare the hardware-proven CPS1/CPS2 Arcade Refresh + launch paths against IGS, preserving the now-working Test15 metadata/JPEG/RGB565/wrapper/catalog publication path, and identify why IGS (a) hard-locks after Games Added and (b) parses the game / starts music but hard-locks on Loading instead of entering gameplay.

The user explicitly corrected the investigation direction:

> CLASSIC was useful to compare/fix image production, but CPS1/CPS2 should now be the immediate controls for IGS because the Arcade family paths should work similarly if not identically. Do not regress/damage image acquisition.

That is now the highest-priority direction.

---

# 1. WORKFLOW / USER RULES

The user expects evidence-driven archaeology with GitHub as the authoritative notebook/source of truth.

**“continue” / “go” means do actual offline archaeology/work, not narrate a plan.**

User explicitly requested:
> Keep working until we get the next HW test. Keep notes of any failures and findings and keep GitHub updated but for today no more 20 seconds tasks just to tell me you found something. I want more work done and less step by step narration.

Do not stop after tiny findings. Batch substantial work and return only when:
1. a meaningful next HW candidate is ready, or
2. a genuine blocker requires user action.

Do not guess. The user has repeatedly caught avoidable mistakes:
- hardcoded `1941.zip`;
- validator injected in the middle of materialization;
- unsupported compatibility claims based on ZIP shape instead of exact XACM;
- incomplete family path specialization;
- Test14 marker-name inference.

Use bit/byte comparison, disassembly, exact artifact capture, exact hashes and already-proven ancestors.

Experimental cycle:
investigation -> build -> offline audit -> HW test -> exact HW observation -> archive exact ZIP -> commit evidence -> promote only after HW proof.

Maxim:
> Recover -> establish provenance -> compare offline -> make smallest evidence-driven delta -> mechanically audit -> hardware-test one unresolved boundary -> record exactly what happened -> archive -> commit -> promote only after HW proof.

---

# 2. PROTECTED CUMULATIVE BASELINE

Protect:
- Test123 CLASSIC
- Test106 MD
- Test75 FC
- Test74 SFC
- final GB/GBC/GBA Refresh
- Audio OSD v8
- stock consoles / stock Arcade
- Mapper v19
- normalized CLASSIC MAME2000 core
- CLASSIC Save/Load

Do not modify FC/SFC/MD/GB/GBC/GBA/CLASSIC to solve Arcade Refresh.

Physical pre-Arcade baseline:
`/mnt/data/20260924_PostGBCGBARefresh_CLEAN.zip`
SHA256:
`5df0b1340e7950ee072ccd72dd6f40fd84535d095f1dabd2359e7c5d9d60872e`

Firmware SHA:
`ea442b74bdc07cd5e05ec2de8da5c997848a76ed3125681c1955fbcb29b66152`

Immediate architectural/materializer parent = current final GBA materializer.
Test75 = enrichment/JPEG ancestry only.
Test106 = narrow stale-backup/staged-loader evidence only.

---

# 3. FOUR-FAMILY TARGET

Topology:

```
/ARCADE/
  CPS1/import art meta
  CPS2/import art meta
  IGS/import art meta
  NEOGEO/import art meta
```

XGO list mapping:
- list7 CPS1: `mswb7.tax / msdtc.nec / mfpmp.bvs`
- list8 CPS2: `kjbyr.tax / djoin.nec / ke89a.bvs`
- list9 IGS: `subst.tax / aepic.nec / sensc.bvs`
- list10 NeoGeo: `rmapi.tax / pcadm.nec / ntdll.bvs`
- list11 CLASSIC protected.

Order 7,8,9,10.

Correct global architecture:
```
Refresh
  -> preflight CPS1
  -> preflight CPS2
  -> preflight IGS
  -> preflight NeoGeo
  -> only compatible candidates reach materialization
  -> CPS1 materializer/catalog
  -> CPS2 materializer/catalog
  -> IGS materializer/catalog
  -> NeoGeo materializer/catalog
  -> aggregate status
  -> native Refresh epilogue
```

Validation MUST happen before processing/materialization for all four families. Tests06-09 proved validator execution inside the materializer breaks artwork and is rejected architecture.

No hardcoded game names or import counts.

---

# 4. CURRENT SCOPE FREEZE

Before validator quarantine, temp-art cleanup, or workspace/path cleanup:
1. get all four Arcade families to parity;
2. preserve dynamic import enumeration;
3. preserve existing XACM preflight before materialization;
4. preserve metadata/JPEG/RGB565/wrapper/catalog enrichment;
5. preserve family order CPS1/CPS2/IGS/NeoGeo;
6. do NOT redesign validator yet;
7. do NOT relocate `.xgo.jpg` / `.xgo.rgb565` yet;
8. do NOT introduce quarantine/rename yet;
9. protect all hardware-proven behavior while specializing helpers.

Shared scratch remains intentionally:
- `/mnt/sda1/ARCADE/.xgo.jpg`
- `/mnt/sda1/ARCADE/.xgo.rgb565`

Do not clean this up yet. Fixed path geometry previously mattered.

---

# 5. COMPATIBILITY / XACM

Exact driver table runtime `0x80A3D7F8`, file `0x00A3D7F8`, 1438 drivers.

Target counts:
- CPS1 154 including QSound
- CPS2 232
- PGM 34
- NeoGeo 258
- total 678

XACM SHA:
`86a798ab9e0c8042a84b99a37fcfacd8708706d0010e0459726420d92ab7c0f5`

Size 237921; 10404 ROM records; string pool 57797.

Tools:
- `generate_xgo_arcade_compat_manifest.py`
- `validate_arcade_import_zip.py`
- `compile_arcade_compat_manifest.py`
- `audit_arcade_compat_manifest.py`
- `zip_central_directory_reference.py`
- `validate_arcade_import_xacm.py`

Stage2 linked `0x87300000`.
Manifest `/mnt/sda1/ARCADE/.xgo-compat`.
Stage2 SHA used Test08 onward:
`503eb939cb5124a4ae71eecf427b238a511ab3db79addbc4bc87270cf59faed1`

Do not make compatibility claims from ZIP shape. Run exact XACM.

---

# 6. TEST06-09 — REJECTED ARCHITECTURE

Compatibility gate was injected inside materializer at +0x0530.
Incompatible rejection worked; compatible games lost artwork.
Tests07-09 tried collision relocation/register preservation.
Literal binary comparison proved no hidden JPEG drift.

Conclusion:
**validator execution itself inside the materializer broke artwork. Never repeat this.**

---

# 7. TEST10 / TEST11 — CORRECT PREFLIGHT ORDERING

Test10 proved preflight-before-materializer works but incorrectly hardcoded `1941.zip`. Do not reuse hardcoding.

Test11 dynamic CPS1 preflight:
- dynamically scans family import directory;
- ignores dirs/non-ZIP;
- constructs paths/stems dynamically;
- validates every candidate;
- closes directory before materializer;
- if all ZIPs compatible and at least one seen -> materializer once;
- incompatible/unsupported currently -> no-change;
- error -> -1;
- empty/nonexistent -> 0.

Stock directory ABI:
- open wrapper `0x807D40C4`
- read next `0x807D4124`
- close `0x807D41F4`
- entry buffer 0x238
- +0 is_directory
- +8 filename
- +0x22d forced NUL

Test11 package:
`xgo-arcade-test11-dynamic-cps1-preflight.zip`
SHA:
`1328e60f86998376e59982964b4eccc6c4394b3bfc1a0c80ffff43252225a9d3`

Test11 CPS1 refresh.xgc:
`5a3abb3cfe9841fc761f7778ae0b9cfc53afdd335d5f6393dc326e18e233549d`

HW PASS:
Games Added -> game appears with image -> runs.

Finding commit:
`87f9ed600c43fd811825bfebf735ff2b6db8d32f`

---

# 8. TEST12 — FOUR-FAMILY PROPAGATION

Source:
`tools/arcade_refresh/propagate_test11_four_family.py`

Initial commits:
- `a9ff5a350be6148102705bd83379d1070f1ae786`
- `050457b32eaa04aebde387ae5c03822f8433b871`
- `c278e2d5b4e9f6418fd7f0d5348fdf88bb43601c`

Finding:
`findings/arcade-test12-four-family-parity.md`

Package:
`xgo-arcade-test12-four-family-parity.zip`
SHA:
`1851cc99485a25ac16235cef5e049a63a88e2e293adc4e15a257ea93800566bf`

Test12 CPS2:
compatible `1944` eventually passed:
Refresh -> Games Added -> artwork -> ZIP read -> long black/loading interval -> game starts -> gameplay works.

Commit:
`d899d7b19282372d0def5baca9f441a84a34e25e`

Do not mistake long CPS2 black screen for failure.

IGS:
`theglad.zip` exact XACM compatible.
Test12 isolated IGS -> Refresh Failed.

NeoGeo:
early `bstars` candidates were confused. Do not trust old “compatible” claims unless exact XACM was run.
NeoGeo has still not received a clean isolated successful materialization/runtime test.

---

# 9. TEST13 — FAMILY PATH GEOMETRY

Offline comparison found materializer +0x0BE4:
`addiu v0, at, 29`

29 = CPS1/CPS2 import-prefix length including slash.

Correct:
- CPS1 29
- CPS2 29
- IGS 28
- NeoGeo 31

Propagation script was corrected:
commit `5dd355779b96e7871cffa8f5d32ae7d8ec48d863`

Finding:
`findings/arcade-test13-family-path-geometry.md`
commit `ec780d4edf95f72e580db91e2fbd37b8ef9921b3`

Test13 package:
`xgo-arcade-test13-family-path-geometry.zip`
SHA:
`39dc01afb1200e0b159a6524fb2a89b0986d515d4a0047863a1f29ca6b805a33`

Hashes:
- CPS1 `5a3abb3cfe9841fc761f7778ae0b9cfc53afdd335d5f6393dc326e18e233549d`
- CPS2 `81fc5a43f57aad69e89ac9e951750bfa4ffeb362d7c64cc361aa716c92a7bf68`
- IGS `1eca119e25dd4f40c26479f064e127c2ce0c3321dd31fc657137ae803389303d`
- NeoGeo `08ebb7029e38c23cf9a006e76ea849971060f4316cc98b1dba9cb7c5d2706b33`

Important correction:
a combined IGS+NeoGeo Test13 Refresh Failed could not identify family.
Then isolated IGS Test13 also Refresh Failed.
Commit recording isolation:
`25be2d863cf897d7ad5974594a407df1ff6ba1b5`

---

# 10. JPEG TEST FIXTURE CORRECTION

The custom keeper `theglad.jpg` initially supplied was 887x887.
The hardware-proven JPEG worker input geometry was 600x400 RGB JFIF.

A 600x400 version was supplied and user replaced the test artwork.

With Test13 + IGS only + 600x400 JPEG:
- Refresh completed;
- Games Added;
- visible entry was bare `theglad`;
- no image visible;
- game did not run.

This was a major clue, because hard Refresh failure disappeared.

---

# 11. CAPTURED TEST13 IGS OUTPUT — CRITICAL EVIDENCE

User supplied exact post-Refresh artifacts in `igs.zip`.

Offline inspection proved:

`The Gladiator.zfb`
- size 59,921
- SHA256 `39cb098cab5a7ebabbd621698065016e12ae8eb73a404f17901d6eda9060f6c9`

`.xgo.rgb565`
- size 59,904
- SHA256 `2fa20ba67982b94db573f8407803f28752a5fee54e290d93954cc3b64eb904a8`

The wrapper's entire first 0xEA00 bytes are byte-for-byte identical to `.xgo.rgb565`.

Wrapper tail at 0xEA00:
`00 00 00 00 "theglad.zip" 00 00`

Therefore all of these were ALREADY WORKING:
- metadata title selection;
- JPEG decode;
- RGB565 generation;
- wrapper construction;
- artwork embedding;
- runtime ZIP basename embedding;
- runtime ZIP copy.

Runtime `theglad.zip`:
- size 20,377,176
- SHA256 `31aac538a31f1c0c5db132659ddfd8dc033268d902e728837b832141a6ec2cc1`

The bad part was catalog publication.

Captured IGS triplet count 7, appended entries:
- SUBST.TAX: `theglad.zfb`
- AEPIC.NEC: `theglad`
- SENSC.BVS: `theglad`

Zero-byte marker:
`.refresh-set/theglad.zfb`

This explained bare title/no image/no launch: actual wrapper was `The Gladiator.zfb`, catalog pointed at `theglad.zfb`.

Evidence commit:
`74fe046c9e8e72bdbd2e494271f03208ec84f9dc`

---

# 12. TEST14 — REJECTED MARKER-TITLE ASSUMPTION

Test14 changed publication marker source to enriched wrapper-name buffer.

Package:
`xgo-arcade-test14-enriched-marker-identity.zip`
SHA:
`11911120695532938ff37a57c9ea3d2ca93ce6854a621eeb15a0105fc1fb8fd9`

HW FAIL:
list contained old `theglad` plus new `The Gladiator.zfb`.
Neither new/bad entry behaved correctly.

Photo proved UI literally showed `.zfb`, revealing Test14 effectively fed a doubled suffix path into the inherited normalization.

Test14 is rejected.
Commit:
`84e2c4882c3adf0448c1e10f448397d4d45a706d`

---

# 13. TEST15 — CURRENT BEST CANDIDATE / PARTIAL HW PASS

CLASSIC was used ONLY as the identity/publication analogy:
friendly outer wrapper/catalog identity vs short runtime ZIP identity.

The concrete Test14 bug was found in the Arcade finalizer itself:
the enriched-name buffer already contained complete `The Gladiator.zfb`, then inherited code appended another `.zfb`.

Test15 removed only that redundant suffix append.

Package:
`/mnt/data/xgo-arcade-test15-classic-style-marker.zip`
SHA:
`282ea8754fd5791d23aecce6fd07df97df3f3cbc55d5a9f1cc94177c109f1472`

Test15 family helper hashes:
- CPS1 `6955960d771ffbd98e12db8837b8c4c0c13018ce2ea4b9025e4f93906c360e6d`
- CPS2 `692f85083610e3f480bbcba752f6a34f52918177c6e060a17fed549f591e878e`
- IGS `c166cfdd929e256d5dae2e4a3d3503f05fbe8775a67408f9a3f3ffb6840e9e3e`
- NeoGeo `b8d7e99637dea8f217e062040a4550283f7542b040232e20ad54526115a36a9f`

Test15 HW procedure:
user restored clean IGS resource files and removed generated `The Gladiator.zfb`, then Refresh.

HW observation:
1. Refresh reported **Games Added**.
2. Device then hard-locked.
3. After reboot, list contained the two historical bad entries from Tests13/14 plus a NEW correct **The Gladiator** entry.
4. New correct entry displayed the generated artwork.
5. Launching new entry:
   - shows Loading;
   - parses/reads ROM files;
   - game music starts;
   - screen remains on Loading;
   - device hard-locks.

Photo evidence shows:
- correct `The Gladiator` title;
- correct custom artwork;
- launch progress `Loading pgm_m01s.rom 2048KB`.

Interpretation:
**Test15 closes the metadata/artwork/wrapper/catalog identity boundary for the newly generated entry.**
The two older bad entries are persisted Test13/Test14 catalog pollution, not Test15 duplicates.

Current remaining failures:
A. Refresh return/cleanup after successful publication -> hard lock.
B. IGS runtime transition after ROM parse/audio start -> hard lock on Loading.

Finding:
`findings/arcade-test15-classic-catalog-semantics.md`
initial HW-result commit:
`03a189a0e2b098092085b5a5b81026dff2c9110f`

Direction pin:
`964b1e5a1f8c48f9ae84d2243d033ed8f502d0a0`

---

# 14. CURRENT INVESTIGATION DIRECTION — VERY IMPORTANT

The user explicitly said:

> classic was used to compare and fix the image production but I think it would be better to continue to go over what is different between cps1 and cps2 and this IGS path... they should work similar if not exactly alike. no need to go back as far as classic for these of course do not regress and damage the image acquisition.

Obey this.

CLASSIC is NOT the next runtime ancestor.

Immediate working controls:
- CPS1: HW PASS Refresh -> artwork -> launch -> gameplay.
- CPS2: HW PASS Refresh -> artwork -> ROM parse -> long loading/black interval -> gameplay.
- IGS: Test15 title/artwork/publication PASS; Refresh-return FAIL; ROM parse/audio begins; Loading exit/runtime FAIL.

Direct comparison matrix:

```
                 CPS1       CPS2       IGS
Refresh           PASS       PASS       adds -> locks
Metadata/title    concealed* concealed*  PASS
Artwork           PASS       PASS       PASS
Wrapper           PASS       PASS       PASS
ROM parsing       PASS       PASS       PASS
Game execution    PASS       PASS       partial/audio
Loading exit      PASS       PASS       FAIL
```

*1941/1944 numeric names concealed whether friendly metadata naming worked, so do not claim that part independently HW-proven for CPS1/CPS2. Test15 publication fix was applied generically and should remain protected.

NEXT OFFLINE WORK:
1. mechanically diff Test15 CPS1, CPS2 and IGS `refresh.xgc` binaries;
2. classify EVERY executable delta:
   - required family ID;
   - import-prefix geometry;
   - family path literals/references;
   - staging geometry;
   - unexplained;
3. compare CPS1/CPS2/IGS Refresh return/cleanup behavior after catalog publication;
4. compare list7/list8/list9 stock launch routing;
5. compare family core/loader selection;
6. compare pre/post-launch callbacks, global flags, audio/task state, heap ownership, return/cleanup;
7. use CPS1/CPS2 as controls;
8. protect Test15 JPEG/RGB565/wrapper/title/catalog behavior;
9. no HW test until a concrete mechanically-supported delta/fix exists.

The fact that IGS MUSIC STARTS while Loading remains visible is a key boundary:
the ROM is not simply rejected early. Loader/core execution advances into audio/game initialization, but frontend/runtime transition does not complete.

Also investigate whether Refresh hard-lock and launch hard-lock share a family-specific cleanup/return assumption, but do not assume they are the same bug without evidence.

---

# 15. MATERIALIZER / PATH DETAILS

Current propagation source:
`tools/arcade_refresh/propagate_test11_four_family.py`

Relevant slots:
- `0x1200,0x20,"/mnt/sda1/ARCADE/{f}/import"`
- `0x1280,0x24,"/mnt/sda1/ARCADE/{f}/meta/%s.txt"`
- `0x12A4,0x24,"/mnt/sda1/ARCADE/{f}/art/%s.jpg"`
- `0x12C8,0x24,"/mnt/sda1/ARCADE/{f}/art/%s.jpeg"`
- `0x25C8,0x38,"/mnt/sda1/ARCADE/{f}/import/"`

Other:
- STAGE_REF `0x21D8`
- STAGE_CPS1 `0x258C`
- STAGE_NEOGEO `0x3000`
- FAMILY_WORD `0x2618`
- IMPORT_PREFIX_SKIP_WORD `0x0BE4`

NeoGeo staging path was relocated to +0x3000 because inherited slot is too short.
Dynamic preflight hook starts +0x2600; binary ~1756 bytes -> ends ~0x2CDC, so +0x3000 was selected from verified zero space. Re-audit before further NeoGeo work.

Test15 also removed redundant suffix append at finalizer region around `0x2204..0x221B`; preserve this behavior while comparing families.

---

# 16. ZFB CONTRACT

Arcade ZFB:
- 0x0000..0xE9FF: 59,904-byte 144x208 RGB565LE preview
- 0xEA00..0xEA03: zero
- 0xEA04: real ZIP basename
- two NUL total

Formula:
`59910 + strlen(zip basename)`

For Test15 IGS:
outer/display wrapper:
`The Gladiator.zfb`

embedded runtime target:
`theglad.zip`

runtime ROM:
`/ARCADE/bin/theglad.zip`

This separation is now proven and MUST NOT be regressed.

---

# 17. LIVE LIST / CACHE

Count base `0x80D2894C`
- list7 `0x80D28968`
- list8 `0x80D2896C`
- list9 `0x80D28970`
- list10 `0x80D28974`

Do not patch cache solely because of old Test04 freeze.

---

# 18. GENERIC RUNNER / COMMAND6

Generic external-helper runner:
`0x80A382E0..0x80A38454`
- a0 helper pathname
- a1 exact byte count
- loads at `0x87000000`
- cache maintenance
- jalr

Golden decoder continuation at `0x80A397E0`:
- command4 GBC
- command5 GBA
- command7 CLASSIC
- command6/default native No New Games

Command6 is clean additive integration point.
Do not put huge logic in firmware cave.

---

# 19. HARD PROHIBITIONS

- no frozen GB changes
- no Test129/Test133
- Test75 is not current materializer parent
- Test106 is not general transaction architecture
- no invented MD Stage2/.catalog
- no guessed cache addresses
- no numeric root aliases
- no huge Arcade firmware cave logic
- no Pac-Man reopening
- no reboot counted as successful Refresh
- preserve CLASSIC/list11
- LCFG CRC != standard CRC
- do not patch cache solely from old Test04 freeze
- do not move scratch files yet
- do not revisit Stage2 placement as artwork cause
- do not inject validator inside materializer
- validation before processing all four
- no validator cleanup/quarantine until four-family parity
- do not regress Test15 image/title/wrapper publication
- do not return to CLASSIC as the immediate IGS runtime model; compare CPS1/CPS2/IGS directly

---

# 20. CURRENT STOPPING POINT / FIRST ACTION IN NEW CHAT

Start by reading this handoff and the Test15 finding.

Then ACTUALLY perform the direct Test15 CPS1/CPS2/IGS binary/disassembly comparison.

The first question to close offline is:

> After normalizing expected family/path differences, what executable/control-flow differences remain between the HW-working CPS1/CPS2 helpers and IGS, especially around successful materializer return/catalog publication and the list9 launch transition?

Do not ask the user for another hardware test until that comparison yields a concrete evidence-driven candidate.

Keep GitHub updated and narration minimal.


## 2026-09-29 correction — stock list order revalidated from exact XGO binary

A prior direct-comparison note incorrectly reversed IGS and NeoGeo list IDs. Exact stock `bisrv.asd` evidence resolves this mechanically: the resource-triplet pointer table contains CPS1, CPS2, IGS (`subst.tax/aepic.nec/sensc.bvs`), then NeoGeo (`rmapi.tax/pcadm.nec/ntdll.bvs`) in consecutive list slots. With CPS1=list7, this pins CPS2=list8, IGS=list9, NeoGeo=list10. The physical catalog-correlation record independently agrees.

Correct mapping:
- CPS1 list7 / count word `0x80D28968`
- CPS2 list8 / count word `0x80D2896C`
- IGS list9 / count word `0x80D28970`
- NeoGeo list10 / count word `0x80D28974`

Therefore the temporary descriptor reversal from commit `73117a3` is rejected and corrected by `121cdca`. It must NOT be used as the Test15 Refresh-lock fix. The IGS Refresh-return failure remains open.
