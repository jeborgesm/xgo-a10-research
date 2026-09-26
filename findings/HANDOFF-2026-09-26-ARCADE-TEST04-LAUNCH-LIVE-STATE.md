# XGO ARCHEOLOGY — HANDOFF
## Arcade Four-Family Refresh — Test04 first successful Refresh, post-refresh/list + launch closure
## Date: 2026-09-26
## Branch: research-arcade-refresh-four-family

Resume XGO Archeology from branch `research-arcade-refresh-four-family`.

Repository: `jeborgesm/xgo-a10-research`.

**DO NOT restart the investigation. DO NOT build another SD candidate yet.**

The current physical SD state is Test04 after one successful Arcade Refresh. Test04 is the first candidate in this branch where command 6 actually completed and appended a CPS1 game. Preserve that Refresh architecture while closing the two remaining failures offline.

---

# 1. User/process requirements

The user wants implementation and exact archaeology, not repeated speculative hardware cycles.

Before proposing/building firmware:
1. read `HANDOFF-CURRENT.md`;
2. read `docs/MODIFICATION-CONTINUITY-PROTOCOL.md`;
3. read `findings/gb-gbc-gba-refresh-branch-contract.md`;
4. follow architectural-ancestor-selection rules;
5. inspect golden artifacts;
6. search the repo for FINAL HW-proven implementations;
7. reconstruct lineage backward only as needed.

Evidence discipline:
- HW = hardware proven
- BIN = direct binary evidence
- SRC = source/reconstruction
- INF = inference
- UP = upstream/family behavior
- OPEN = unresolved

Hardware-test gate before a new candidate:
A exact new unknown;
B HW-proven ancestor for preserved mechanisms;
C exact golden binaries/source recovered;
D delta mechanically audited;
E historical experiments reviewed;
F why offline analysis cannot answer further.

User explicitly said:
> "If there are limitations, I can facilitate please ask for help. no need to stop the progress because there is an impediment I can easily overcome on my side."

Also treat user interventions as lineage/scope corrections, not obstruction.

---

# 2. Protected cumulative baseline

Protect:
- Test123 CLASSIC
- Test106 MD
- Test75 FC
- Test74 SFC
- final GB/GBC/GBA Refresh
- Audio OSD v8
- stock consoles/Arcade
- Mapper v19
- normalized CLASSIC MAME2000 core
- CLASSIC Save/Load

Do not modify FC/SFC/MD/GB/GBC/GBA/CLASSIC to solve Arcade Refresh.

Current physical pre-Arcade baseline:
`/mnt/data/20260924_PostGBCGBARefresh_CLEAN.zip`
SHA-256:
`5df0b1340e7950ee072ccd72dd6f40fd84535d095f1dabd2359e7c5d9d60872e`

Firmware:
`ea442b74bdc07cd5e05ec2de8da5c997848a76ed3125681c1955fbcb29b66152`

Final GBC/GBA package:
`3c8c7829d2aab4fc6050d896f00335adfe40f4115db1fcfe546586404b10dbb1`

Current GBA materializer is the immediate architectural/materializer parent.
**Test75 is historical enrichment/JPEG ancestry only.**
**Test106 is narrow stale-backup evidence only.**

---

# 3. Arcade target

Target topology:

```text
/ARCADE/
  CPS1/import art meta
  CPS2/import art meta
  IGS/import art meta
  NEOGEO/import art meta
```

Folder identity selects family/core/catalog. No ROM introspection.

XGO list mapping:
- list 7 CPS1: `mswb7.tax / msdtc.nec / mfpmp.bvs`
- list 8 CPS2: `kjbyr.tax / djoin.nec / ke89a.bvs`
- list 9 IGS/PGM: `subst.tax / aepic.nec / sensc.bvs`
- list 10 NeoGeo: `rmapi.tax / pcadm.nec / ntdll.bvs`
- list 11 CLASSIC protected/out of scope.

Do not copy DY19's 9/10 order; XGO evidence controls.

Command 6 intended architecture:

```text
cmd6
 -> CPS1 materializer -> CPS1 catalog
 -> CPS2 materializer -> CPS2 catalog
 -> IGS materializer -> IGS catalog
 -> NEOGEO materializer -> NEOGEO catalog
 -> aggregate status -> native Refresh epilogue
```

Order 7,8,9,10.
Empty/nonexistent family import = no-change.
Any failure => failed.
Any addition => updated.
Otherwise => no new.
No global rollback.

---

# 4. ZFB contract — direct BIN proof

Arcade ZFB geometry:

```text
0x0000..0xE9FF  59,904-byte 144x208 RGB565LE preview
0xEA00..EA03    four zero bytes
0xEA04..        real ZIP basename, e.g. dino.zip
then two NUL bytes total around the string/trailer
```

Formula:
`59910 + strlen(zip basename)`.

Known-good direct fixtures previously uploaded:
- KOF94 NeoGeo SHA `42fe80265245293f097ba415f070a4840bcb2dd985a5bcd1558c4b6db0c726b9`
- Dino CPS1 SHA `906395f282ba3c048311a77f32ee929622c92b074a1ff3f46450ddf19f06a6bc`
- KOV IGS SHA `f102b67b5beb7e2acdc248a249a45c633bd5c1830d6d8b43ab0a136c487cf774`
- SFA3 CPS2 SHA `c7f9ba3d3e8bf260d2ceaf31481e6d35aa6a0a61d7e490a63a6331de6f331a56`

Known-good Dino preview:
- first 0xEA00 SHA `03da57a18af24afbe2b0cde67832491dc859560b426519b3e60e9b83370e268b`
- nonzero bytes 57,476.

---

# 5. Authoritative Arcade catalog helpers

The final emitted catalog helpers are derived mechanically from the exact final GBA catalog helper, not Test75.

Parent GBA catalog:
- SHA `db7c1173f5b98adb3506b2676a035ba6e54b35a4391709cbbcd7ad92b983cbc6`
- size 0xA52.

Emitter:
- patches `.zgb` -> `.zfb`;
- NOPs GBA-specific cache invalidation at +0x0730..+0x0738;
- appends family resource/root strings;
- retargets seven MIPS references.

Authoritative family helper hashes:
- CPS1 size 2767 SHA `dd7f6c21428bd482ddbc7da298bd9e2e9fb4b6b449065831b26d0fadc9374528`
- CPS2 size 2767 SHA `7a636c1a801de7c63bfe4d7e9bbed9acd9ac0bdb4b8756f966ee04a37e3edb88`
- IGS size 2766 SHA `97cde79e59626dcfc1997f1678d61a87d81dd0b5e686ec5ba629fb4b55683b7b`
- NeoGeo size 2769 SHA `6f91ff89aeecea7f3128bdbdbd66e2a0eca2df46257ca93edcd02aa790f3ac7c`

Each changes only 20 bytes in the original parent outside appended data; zero changes outside the allow-list.

Staging:
`/ARCADE/<family>/.refresh-set/`

Marker basename = exact outer ZFB filename.
Materializer clears/recreates family set at start.
Marker created only after ZIP + ZFB converge.
Catalog scans the marker set using inherited native GBA DIR iteration/stable append.

**Important open issue:** GBA cache invalidation was intentionally NOPed because GBA cache pointer `0x80D28974` cannot be reused for Arcade. Exact Arcade list cache/live-state invalidation remains unresolved.

---

# 6. Test01–Test03 failures (do not repeat)

Test01 malformed:
- splice +0x09C4 called `0x87008000`;
- helper was linked at `0x87002000`;
- intended regions zero;
- convergence helper never called.
HW: Refresh Failed.

Test02 restored numeric root aliases 0..7. Never do numeric root aliases again.
First three catalog hashes also wrong.

Test03 removed aliases and patched command6 direct paths by appending strings to firmware.
HW: Refresh Failed.
ZIP SHA:
`223c42caea955b15598bd273e27cadf6e920946ef233ec1e2c69ba0ec77a9676`
FW SHA:
`c9b16741f85f56cf9041d77e25193b224a099f92ae860dcf67c702e48f3a7882`
LCFG:
`0xCDA9FC0F`.

---

# 7. v3 finalizer

User compiled and supplied:
`/mnt/data/arcade_finalize_v3.zip`

CPS1 helper:
- size 1512
- SHA `5c443db116dd85867c95d85c03f895331ed4d1cd2143ebd855cddd888b787693`

ABI:
- a0 = frame+0x44 open destination wrapper FILE*
- a1 = frame+0xB8 stem
- no a2.

Behavior:
1. writes four zero bytes + stem + `.zip` + two NULs;
2. closes wrapper;
3. source ZIP `/mnt/sda1/ARCADE/<FAMILY>/import/<stem>.zip`;
4. destination `/mnt/sda1/ARCADE/bin/<stem>.zip`;
5. copies/verifies runtime ZIP;
6. creates marker `/mnt/sda1/ARCADE/<FAMILY>/.refresh-set/<stem>.zfb`;
7. returns 0/-1.

Native callbacks:
- fopen 0x802B3524
- fread 0x802B3698
- fwrite 0x802B42AC
- fclose 0x802B2F40.

Linked at `0x87002000`.

Golden GBA scratch identities:
- s7 = 0x87600000
- s4 initially 0x87600005
- s3 0x8760000A
- s2 0x87600008
- frame+0xB8 = 0x87600500 (stem)
- frame+0xA0 = 0x87600200
- frame+0xCC = 0x87600400
- frame+0xC8 = 0x87600501
- frame+0xA8 = 0x876003FF
- frame+0x94 = 0x87600100.

Do not revive the earlier incorrect assumption that frame+0x94 is the outer ZFB identity. Do not claim 0x87600500 is invalid; it is the golden current stem buffer.

---

# 8. Test04 — current first Refresh-success baseline

Package:
`/mnt/data/xgo-arcade-four-family-test04.zip`

ZIP SHA:
`bd7db55d70beb0a726824026e4bc6f6f2b979c46e10339b7584691de7d4a293f`

Firmware:
- SHA `b9178dc551516dcb700445fb4b76cd9c626eb8dad873d2b2f705ed0d714249f0`
- exact golden size 12,768,452
- LCFG CRC-32/MPEG-2 `0x85A9C08E`.

No appended firmware data.
No root numeric aliases.
Roots only `ARCADE/` and `bios/`.

Test04 CPS1 splice at +0x09B4:
```text
8fc40044
8fc500b8
0dc00800
00000000
144000ef
00000000
09c0031d
00000000
```
=> a0 frame+44, a1 frame+B8, JAL 0x87002000, fail branch, success jump.

Test04 CPS1 live relocated literal refs:
- +0060 -> 0x1200
- +00C0 -> 0x1280
- +0140 -> 0x1200
- +014C -> 0x1220
- +0158 -> 0x12A4
- +0164 -> 0x12C8
- +01C8 -> 0x1234
- +01D4 -> 0x1258.

Strings:
- 0x1200 `/mnt/sda1/ARCADE/CPS1/import`
- 0x1220 `/mnt/sda1/ARCADE`
- 0x1234 `/mnt/sda1/ARCADE/CPS1/art/.xgo.jpg`
- 0x1258 `/mnt/sda1/ARCADE/CPS1/art/.xgo.rgb565`
- 0x1280 `/mnt/sda1/ARCADE/CPS1/meta/%s.txt`
- 0x12A4 `/mnt/sda1/ARCADE/CPS1/art/%s.jpg`
- 0x12C8 `/mnt/sda1/ARCADE/CPS1/art/%s.jpeg`.

Test04 materializer SHAs:
- CPS1 `301df6494c89928cf615a918b76f81d4c0774d864cd45c77cacc2e145fed3f28`
- CPS2 `24a64f9645bf69a6c110d3668ed58f5af77191be1253fe658c46fd2e6053e6a1`
- IGS `7ad397a2c622fab65e48fc50d2deeb165b5d7d8e3cf886d65b5b1a021a3507d5`
- NeoGeo `947ef03e735935a3b06843d67924c3dc5da25a2f2a5fc10c4ea6df569e844ba0`.

Catalog helpers are exactly the authoritative hashes listed above.

## Test04 HW result

One Refresh was run.

Observed:
1. Refresh displayed **Games added**.
2. Immediately entering CPS1 hard froze.
3. After reboot, CPS1 list displayed the newly added game, **1941**, but with no image.
4. Launching 1941 hard froze at **Loading....**.

Therefore Test04 HW proves:
- command6 routing reaches CPS1 materializer;
- materializer reaches success;
- v3 finalizer completes;
- runtime ZIP convergence completes enough for finalizer verification;
- marker is created;
- catalog helper appends the entry;
- catalog persists and is readable after reboot.

Failures:
- immediate post-Refresh list re-entry/live visibility;
- no artwork shown;
- launch freezes at Loading.

**Freeze Test04 Refresh architecture. Do not gratuitously rewrite it.**

---

# 9. Exact generated Test04 artifacts supplied by user

User uploaded from the Test04 SD:
- `/mnt/data/1941.zfb`
- `/mnt/data/1941.zip`

These are now failed-output fixtures. Preserve them.

Direct inspection established:

## 1941.zfb

Size:
**59,918 bytes**

Trailer at 0xEA00:
```text
00 00 00 00 31 39 34 31 2E 7A 69 70 00 00
```

ASCII:
```text
[4 zeros] 1941.zip [2 zeros]
```

This matches the expected ZFB geometry exactly:
59904 + 4 + len("1941.zip") + 2 = 59918.

The first 0xEA00 bytes are **all zero**.

That initially looked like corruption, but a direct golden-GBA materializer comparison closed the mechanism:

At materializer +0x08C0:
```text
08C0  lw    at,0x38(fp)
08C4  bnez  at,0x0960
```

`frame+0x38` is the artwork/fallback state.

Golden inherited behavior:
- frame+0x38 = 0 => valid artwork path;
- frame+0x38 = 1 => no-art/fallback path.

The branch to +0x0960 explicitly zeroes the preview buffer before the 0xEA00 write.

Therefore:
**the blank 1941 preview is intentional inherited GBA no-art fallback behavior, not a broken finalizer.**

This explains the missing image.
It does **not** by itself explain launch failure.

Later improvement can provide an Arcade fallback image, but do not conflate that with launch.

## 1941.zip

The generated ZFB names `1941.zip`, and the uploaded runtime ZIP has that exact basename.
The previous analysis found it internally coherent as a 1941 CPS1 ROM archive, but do not rely on web ROM-set claims as the launch proof. Compare against XGO stock loader/core requirements directly.

---

# 10. Important correction: do NOT use historical Test11 Pac-Man as the current launch oracle

A dangerous false lead occurred at the end of this chat.

Historical findings say Test11 temporarily appended `Pac-Man.zfb` as CPS1/list7 entry 27 and at that historical stage Pac-Man reportedly launched/gameplay worked (audio silent).

However the user correctly intervened:

> "The current entry in the SD card for pac-man in cps1 is not loading, it returns to the menu. I think that is why we moved to implement Classic in the first place"

This is the relevant present hardware state.

Current CPS1 Pac-Man:
```text
select
 -> Loading...
 -> returns to menu
```

CLASSIC was developed specifically to obtain a reliable MAME2000 path for Pac-Man/Ms Pac-Man and other classic titles.

Therefore:
- **DO NOT claim Test11 proves the current CPS1 stock loader accepts arbitrary newly appended games.**
- **DO NOT use current CPS1 Pac-Man as a known-good control.**
- Historical Test11 is archaeology only and may reflect an earlier firmware/runtime/content state.
- Do not reopen obsolete Pac-Man investigation as part of this branch.

For Test04 `1941`, the correct stock control must be a **currently working stock CPS1 entry**, e.g. Cadillacs & Dinosaurs or another protected stock CPS1 game.

The assistant explicitly retracted the earlier conclusion that Test04 must differ from Test11 only in catalog semantics.

---

# 11. Stock launcher facts already established in repo

Useful findings:

`findings/console-wrapper-import-contract.md`
- preserved XGO `run_game` is at 0x80360B88.
- Arcade ZFB is a thumbnail/reference record, unlike console wrappers.

`findings/classic-deep-test12-contract-audit-test33.md`
established direct machine-code facts about stock `run_game`.

Before the final arcade runtime call at 0x80360DF8, stock firmware has already:
1. classified selected extension/system family;
2. opened/read selected wrapper;
3. populated `gp_buf_64m @ 0x80C33AD8`;
4. populated `g_run_file_size @ 0x80C33A7C`;
5. executed stock packaged-content/Arcade preprocessing;
6. resolved/mutated selected archive-name state;
7. set Arcade family bit `0x40`;
8. registered ordinary pre-loader UI callback through 0x8036B558;
9. then calls the arcade loader/runtime path.

This is valuable for Test04 launch closure. We need to compare the generated `1941.zfb` against a **currently working stock CPS1 wrapper/runtime pair**, and determine whether stock preprocessing derives any state beyond the trailer basename that our generated wrapper/catalog row fails to supply.

Historical finding:
`findings/hardware-test-05-cps1-zfb-load-failure-test06-fix.md`
also documents:
- ZFB preloaded into ROM buffer;
- four-zero separator at 59904;
- basename begins at 59908;
- runtime ZIP path concept `/mnt/sda1/ARCADE/bin/<embedded-name>`.
Use as architecture evidence, but remember it concerns an external CPS1 frontend experiment, not proof of current stock acceptance for arbitrary drivers.

---

# 12. Current two independent blockers

## Blocker A — immediate post-Refresh CPS1 list freeze

Direct HW evidence:
- Refresh says Games added.
- immediate CPS1 entry freezes.
- reboot makes the new row visible.

This strongly localizes the problem to **live frontend/list state**, not persistent catalog corruption.

The Arcade catalog helpers deliberately NOP inherited GBA cache invalidation at +0x0730..+0x0738 because the GBA cache pointer `0x80D28974` is wrong for Arcade.

Do NOT guess Arcade cache addresses.

Next static work:
- disassemble/search current protected firmware around list7/list8/list9/list10 catalog loading;
- identify exact cache/global pointer(s) or native invalidation/reload path for Arcade;
- determine whether all four families have distinct slots;
- implement only after direct BIN proof.

The next candidate must not require reboot for visibility.

## Blocker B — 1941 launch freezes at Loading

Closed:
- ZFB total geometry is correct.
- separator is correct.
- embedded basename is exactly `1941.zip`.
- runtime ZIP exists with matching basename.
- blank preview is intentional no-art fallback and is a separate presentation issue.

Still OPEN:
- exact current stock CPS1 loader requirements beyond wrapper basename;
- whether generated catalog row values (filename/title/search key) influence runtime preprocessing;
- whether current stock FBA actually contains/supports the 1941 driver expected by this ZIP;
- whether archive contents/driver identity match the vendor's compiled FBA build;
- whether stock runtime depends on a hidden per-entry/subtype/index mapping not represented by the visible catalog triplet;
- whether the hard freeze is before/inside `run_fba`.

Do not blame the ROM set without evidence.
Do not assume arbitrary CPS1 support because historical Pac-Man once launched.
Do not change the Refresh materializer until the loader contract is closed.

---

# 13. Correct next analysis sequence

1. **Choose a current known-good stock CPS1 control**, preferably Cadillacs & Dinosaurs because it is repeatedly hardware-proven on the protected baseline.

2. Recover/inspect the exact current stock pair:
```text
/ARCADE/Cadillacs and Dinosaurs.zfb
/ARCADE/bin/dino.zip
```
plus its exact three CPS1 catalog row values.

If these exact files are not available in repo/local artifacts, ASK USER for them rather than guessing. User has explicitly invited precise artifact requests.

3. Compare known-good stock CPS1 pair vs generated Test04 pair:
- wrapper geometry;
- trailer;
- preview relevance;
- ZIP filename;
- ZIP central directory/content structure;
- compression;
- ROM member names/CRCs only as needed;
- catalog slot0/slot1/slot2 values;
- index position;
- any runtime-derived family/subtype state.

4. Disassemble current stock `run_game`/Arcade preprocessing around:
`0x80360B88..0x80360DF8`
and stock runtime call after `0x80360DF8`.
Trace:
- how list ID is used;
- how ZFB trailer is parsed;
- where archive basename is stored;
- what `run_fba` receives;
- whether driver selection is purely basename-driven or index/table-driven;
- any CPS1-specific driver/subtype table.

5. Separately solve live-state/cache invalidation:
- locate list7 CPS1 cache pointer/reload;
- then list8/list9/list10;
- no direct address guessing.

6. Only when both blockers have exact fixes, update Test04 minimally into the next candidate.

7. Keep artwork fallback improvement secondary. A blank preview is now explained and does not justify another SD cycle by itself.

---

# 14. Current repo tooling on branch

Existing tools include:
- `tools/arcade_refresh/zfb_codec.py`
- `verify_stock_zfb_fixtures.py`
- `arcade_descriptors.py`
- `catalog_codec.py`
- `import_planner.py`
- `artwork_adapter.py`
- `runtime_zip_contract.py`
- `family_staging.py`
- `materializer_staging_contract.py`
- `catalog_family_descriptors.py`
- `catalog_relocation.py`
- `emit_arcade_catalog_helpers.py`
- `audit_arcade_catalog_helpers.py`.

Relevant branch commits already recorded:
- ZFB codec `53e38d31...`
- fixture verifier `92dc444...`
- descriptors `8653f5a...`
- catalog codec `c297314...`
- planner `57c0b1d...`
- JPEG closure `6555c9...`
- runtime contract `049d3ec...`
- staging refinement `ad314e...`
- catalog emitter tightened `2abaad...`
- catalog delta audit `9ce4c...`
- independent audit `68bb9c...`
- lineage lock `254e7a...`
- current runner audit `aa50ab...`.

---

# 15. LCFG reseal

Firmware LCFG:
- payload size = file_size - 0x200;
- LE32 payload size at 0x184;
- CRC-32/MPEG-2 over data[0x200:];
- LE32 CRC at 0x18C.

Do not confuse this with standard ZIP CRC32.

---

# 16. Hard prohibitions / lessons

- Do not modify frozen GB materializer.
- Do not resurrect Test129/Test133.
- Do not use Test75 as current materializer parent.
- Do not use Test106 as general transaction architecture.
- Do not invent MD Stage2 or .catalog ledger behavior.
- Do not guess Arcade cache addresses.
- Do not add numeric root aliases.
- Do not force large Arcade logic into firmware cave; command6 route + external helpers.
- Do not promote historical Pac-Man behavior into a current stock CPS1 guarantee.
- Do not reopen Pac-Man as the branch target.
- Do not issue another hardware candidate until launch and live-list failures are closed offline as far as possible.
- Do not require reboot as part of successful Refresh behavior.
- Preserve CLASSIC/list11.
- Standard file CRC32 != LCFG CRC32/MPEG-2.
- Do not trust prior assistant wording such as "mechanically proven" without rechecking the actual artifact/code.

---

# 17. Exact stopping point

The chat ended while beginning the corrected comparison of Test04 `1941` against a **currently working stock CPS1 game**, after the user caught the incorrect attempt to use historical Test11 Pac-Man as the current oracle.

The immediate next action in the new chat is:

> Continue offline from Test04. Recover a current known-good stock CPS1 wrapper/runtime/catalog row (preferably Cadillacs & Dinosaurs), compare it mechanically against generated `1941.zfb` + `1941.zip`, and trace current stock Arcade preprocessing/driver selection. In parallel, identify exact Arcade live-list cache invalidation from firmware. Do not build Test05 until both failure mechanisms are understood enough to justify the delta.

If the exact current Dino ZFB/ZIP cannot be recovered from golden artifacts/repo, ask the user for those **two exact SD files**. That is a legitimate precise blocker and the user has explicitly offered to facilitate.
