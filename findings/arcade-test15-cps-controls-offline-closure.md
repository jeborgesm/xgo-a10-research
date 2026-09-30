# Test15 CPS1/CPS2/IGS direct-control offline closure

Date: 2026-09-29
Branch: `research-arcade-refresh-four-family`
Evidence: BIN/SRC/INF; no new HW claim

## 1. Correct stock list identity

A temporary branch change reversed IGS and NeoGeo IDs. That was wrong.

Exact stock `bisrv.asd` proves the triplet table at `0x80A3C32C` is 12 bytes per list. The Arcade sequence is:
- list7 CPS1 -> `mswb7.tax/msdtc.nec/mfpmp.bvs`
- list8 CPS2 -> `kjbyr.tax/djoin.nec/ke89a.bvs`
- list9 IGS -> `subst.tax/aepic.nec/sensc.bvs`
- list10 NeoGeo -> `rmapi.tax/pcadm.nec/ntdll.bvs`

The stock loader at `0x803536EC` independently indexes the count array as `0x80D2894C + list_id*4`, pinning:
- list7 `0x80D28968`
- list8 `0x80D2896C`
- list9 `0x80D28970`
- list10 `0x80D28974`

Commit `73117a3` is therefore a rejected false lead. Source was corrected in `121cdca`.

## 2. Test15 helper differential

After normalizing family path literals, validator family selector and the already-known import-prefix length specialization, the Test15 CPS1/CPS2/IGS materializer executable has no unexplained family-specific control-flow delta.

This protects the Test15 JPEG/RGB565/friendly-wrapper/catalog publication path. Do not change it merely because IGS launch locks.

## 3. Stock launch transition is shared

The stock launch path does not have a separate list9 IGS runner.

At `0x80360B88`, the launcher:
1. derives the file extension/type through `0x80360A08`;
2. stores the resulting runtime type flags in the common global at gp-0xCA4;
3. dispatches NES/SNES/etc special cases;
4. all ordinary Arcade ZFB cases fall through the common `run_emulator` path at `0x80360848`;
5. common cleanup remains at `0x80360E00`.

The Arcade path construction is also shared: `%s/bin/%s` using `0x810A0EB0` + `0x8109FCE8`.

Therefore CPS1/CPS2 vs IGS do not differ by a list9-specific frontend launch transition in stock firmware.

## 4. The Gladiator is not equivalent to a stock-proven IGS control

The exact XGO driver table contains 34 PGM drivers, but the shipped IGS catalog exposes only six:
- Knights of Valour
- Knights of Valour 1.15
- Knights of Valour Plus
- Knights of Valour Plus a
- Oriental Legend
- Dragon World II

The compiled driver descriptor for `theglad` is PGM and shares the same PGM init/exit/frame/draw callback family as `kov`, but its hardware discriminator differs:
- `kov`: 0x81
- `theglad`: 0x80

The stock curated parent titles `kov`, `orlegend`, and `drgw2` are 0x81; their listed clones are 0x91. Several non-curated PGM titles, including `theglad`, are 0x80/0x90.

This does not by itself prove why The Gladiator locks, but it proves that “present in the compiled driver table / XACM” is not the same claim as “stock hardware-proven playable.” Test15 reaching ROM parsing and game music while remaining on Loading is consistent with a deeper game/protection/runtime boundary and is not evidence of a list9 frontend routing mismatch.

## 5. Refresh lock remains separate

Test15 reaches `Games Added`, so materialization + catalog publication returned far enough to enter native status handling. The later hard lock is therefore post-publication/return-state corruption or lifecycle behavior, not an early IGS path/validator failure.

No mechanically justified IGS-only return patch has yet been identified. Do not hardware-test a guessed cache/list-ID change: the exact stock binary validates list9 and `0x80D28970`.

## Gate

No Test16 is authorized yet.

Next offline target is the data-dependent post-publication state: compare the exact successful CPS1/CPS2 publication state against the IGS Test15 output, especially marker identity, catalog record lengths, helper scratch/buffer bounds, and any state surviving into native status epilogue. The launch lock should be treated independently until a stock-curated IGS import control demonstrates the same transition failure.


## 6. Source-drift audit after closure

A branch-integrity check found that commit `121cdca` corrected the validation assertions but did **not** fully correct the live descriptor tuples: IGS still carried NeoGeo's `0x80D28974` count target and NeoGeo still carried list ID 9. This was repository drift introduced during the post-Test15 investigation, not evidence about the already-built Test15 package. The tuples are now corrected in `d482d456` to IGS=list9/`0x80D28970` and NeoGeo=list10/`0x80D28974`.

Historical reconstruction confirms the descriptor file was correct before the post-Test15 false-reversal work, so this source drift did not create the observed Test15 hardware lock. It did, however, prove the branch needed an explicit source-vs-assertion integrity check before any Test16 build.

## 7. Refresh-return candidate boundary narrowed

The catalog emitter deliberately performs a family-specific frontend-count invalidation immediately before returning. Earlier architecture had explicitly NOPed this write until exact Arcade count slots were closed; commit `32413da` later restored it after the stock count-array addresses were recovered. CPS1/CPS2 hardware passes show the mechanism is not generically invalid, but Test15 IGS reaches a valid committed catalog and `Games Added` before locking, placing the remaining failure after publication and making this post-commit frontend-state mutation the narrowest remaining IGS-specific lifecycle surface.

This is not yet proof that the IGS count invalidation is the cause. A Test16 must not change publication/JPEG/wrapper logic. If emitted, its only Refresh-side experiment should suppress the IGS post-commit count invalidation while leaving CPS1/CPS2 and all Test15 materialization/publication bytes unchanged. That is a single-boundary lifecycle test, not a list-ID guess.

The launch failure remains independent. `theglad` is not a stock-curated IGS runtime control; do not modify the shared stock launch path based on it. The next runtime control should use a stock-curated PGM/IGS driver or an otherwise hardware-proven 0x81/0x91 PGM control before changing runtime code.


## 8. Hardware-fixture policy: The Gladiator is disposable

User clarified the intent of `theglad`: it was selected only as a sample unlisted IGS game to exercise the Refresh pipeline. It is **not** a target title and must not become an investigation dependency.

Accordingly:
- Test15 already proves the metadata/artwork/wrapper/catalog publication path can create a correct enriched IGS entry from an unlisted candidate.
- If `theglad` itself is outside the XGO runtime-compatible PGM subset, replace it with another unlisted candidate rather than modifying shared runtime code to accommodate it.
- Prefer the next fixture from a driver class closest to the stock-curated IGS set (0x81/0x91) while requiring that it is not already in the visible stock IGS catalog.
- Keep the Refresh-return hard lock as a separate lifecycle defect; changing the runtime fixture does not retire that defect.

This prevents sample-game compatibility from hijacking the four-family Refresh objective.


## 9. Replacement IGS fixture identified from original-card archaeology

The preserved original-card inventory already supplies a better next IGS control: **Puzzle Star.zfb** is one of the seven packaged Arcade wrappers physically present on the vendor card but absent from all four visible stock Arcade catalogs. Independent driver-table inspection identifies `puzlstar` as PGM hardware discriminator `0x81`, matching the parent-class discriminator of the stock-curated `kov`, `orlegend`, and `drgw2` controls.

This makes Puzzle Star preferable to The Gladiator for the next runtime proof:
- vendor-supplied XGO wrapper existed physically;
- not already exposed in the visible IGS list;
- PGM/IGS family;
- 0x81 discriminator matches the curated parent class;
- does not require treating `theglad` compatibility as a branch objective.

Do not yet claim Puzzle Star is HW-playable merely from its presence. First recover its exact vendor wrapper/runtime ZIP identity from the preserved card/artifacts if available and use those bytes as the compatibility reference. The Refresh-return lock remains a separate lifecycle defect.


## 10. Puzzle Star provenance gate

A search of the currently mounted analysis bundle and repository found no recoverable `Puzzle Star.zfb` payload, only the preserved inventory evidence that the OEM card contained that filename. Therefore the original wrapper's embedded runtime target cannot yet be byte-verified from the available archive.

Do not fabricate the target from the display name. For a future hardware fixture, either (a) recover the OEM `Puzzle Star.zfb` from the physical/original-card corpus and inspect its wrapper tail, or (b) construct a new metadata fixture only after independently proving the matching runtime ZIP/driver identity. The likely driver name `puzlstar` remains a compatibility lead, not provenance proof.

This does not block the Refresh-return investigation, which remains independent of game runtime compatibility.


## 11. Tooling integrity repair before any Test16

Offline branch audit found a concrete repository defect in `emit_arcade_catalog_helpers.py`: commit `32413da` had inserted literal backslash-n text into the Python source while restoring family count-cache invalidation. This made the current emitter source syntactically unusable even though already-built Test15 binaries predate/stand independently of this source-state defect. The emitter was normalized in `33db32dd`; the companion audit source did not contain remaining literal escapes.

This repair is **tooling integrity only** and must not be interpreted as a Test15 hardware diagnosis. Any future candidate must be rebuilt from audited source and mechanically diffed against the protected Test15 behavior before hardware use.


## 12. BIN closure: exact-count invalidation can trap before lazy reload

Direct disassembly of the preserved stock `bisrv.asd` closes the previously missing mechanism. In the normal browser path around `0x80357ECC..0x80357F18`, firmware computes the current list's count-slot address from the same `0x80D2894C + list_id*4` array, loads that count into `$24`, and executes:

```
80357ee8  lw    $24,0($25)       # count[list]
80357ef4  div   $zero,$2,$24
80357ef8  teq   $24,$zero,7      # divide-by-zero trap guard emitted after DIV
...
80357f14  bnez  $5,0x80357ce8
80357f1c  ...                     # later lazy-reload path
```

The important ordering is mechanical: **the count is consumed as a divisor before the later zero-count lazy-reload branch is reached.** Therefore forcing the active list's exact count slot to zero at catalog-helper return is not a universally safe cache invalidation operation. On a re-entry path that reaches this block first, it can trap/hard-lock before stock lazy reload has an opportunity to repopulate the count.

This directly matches Test15 IGS: publication completes, native success status is visible, then the device hard-locks during frontend return/re-entry.

### Historical control resolves the apparent GBC/GBA contradiction

The earlier HW-proven handheld catalog helpers do **not** prove that exact active-list zeroing is safe. Their recorded count-cache targets were inherited/retargeted values that did not consistently correspond to the active handheld list. For example the golden GBA propagation record explicitly used `0x80D28974`, which direct stock BIN mapping identifies as Arcade list 10, not GBA list 6 (`0x80D28964`). Those hardware passes therefore demonstrate that catalog publication does not require exact active-list invalidation; they do not validate zeroing the active count immediately before browser return.

### Test16 authorization boundary

Offline evidence is now sufficient for a single-variable Refresh-side candidate:

- preserve Test15 firmware/materializer/publication/JPEG/title/wrapper/catalog semantics;
- in **IGS catalog.xgc only**, replace the final count-slot invalidation instruction sequence at helper offsets `+0x0730..+0x0738` with NOPs, restoring the earlier safe-emitter behavior;
- do not alter CPS1/CPS2/NeoGeo helpers;
- do not change shared launch/runtime code;
- judge only whether IGS Refresh returns normally after `Games Added` and whether the newly published entry remains visible after normal browser reload/reboot.

This is no longer a speculative list-ID test. It isolates a stock-BIN-proven divide-before-reload hazard introduced by exact active-list invalidation.


## 13. Uploaded Test15 IGS catalog helper falsifies count-invalidation hypothesis

User supplied the exact `IGS/catalog.xgc` from the tested SD card on 2026-09-29. Mechanical inspection:
- size: 2766 bytes;
- SHA-256: `97cde79e59626dcfc1997f1678d61a87d81dd0b5e686ec5ba629fb4b55683b7b`;
- words at `+0x0730/+0x0734/+0x0738`: all `0x00000000`.

Therefore the Test15 helper already had the earlier safe behavior: **no frontend count-cache invalidation at all**. The proposed Test16 NOP experiment would be byte-identical at that boundary and is cancelled. The divide-before-lazy-reload stock mechanism remains real, but it did not cause the observed Test15 IGS lock.

The uploaded helper hash also matches the pre-retarget IGS emitter lineage recorded in `arcade-refresh-catalog-first-emission-delta-audit.md` (`97cde7...`), proving Test15 used that lineage rather than the later exact-count retarget source state.

Investigation must return to post-publication lifecycle/data effects with this hypothesis eliminated. Do not emit a hardware candidate from the count-cache theory.


## 14. OEM Puzzle Star runtime identity recovered from original-card inventory

The preserved original-card file inventory (`xgo_filelist.csv`) closes the previously open provenance gate without inference:
- `D:\\ARCADE\\Puzzle Star.zfb` — 59,922 bytes — 2023-02-02;
- `D:\\ARCADE\\bin\\puzlstar.zip` — 5,980,261 bytes — 2022-07-13.

The 59,922-byte wrapper size is exactly the 59,904-byte stock preview prefix plus an 18-byte wrapper tail, consistent with the runtime identity `puzlstar.zip` plus wrapper framing. More importantly, the matching OEM bin archive is independently present on the same original card, so `Puzzle Star -> puzlstar.zip` is now provenance-backed rather than guessed from the driver table.

Puzzle Star is therefore approved as the replacement unlisted OEM PGM/IGS runtime control when the Refresh-return defect is isolated. It remains physically vendor-supplied but absent from the visible six-entry IGS catalog, making it suitable for testing import/publication without using The Gladiator.


## 15. Test16 hardware gate — clean known-stock IGS control, no firmware delta

After the exact Test15 catalog helper falsified the count-cache theory, the remaining ambiguity is whether the observed post-`Games Added` lock belongs to the IGS Refresh lifecycle itself or to the contaminated Test13/Test14/Test15 marker/runtime fixture state.

The smallest hardware discriminator requires **no firmware change**. Use current Test15 with a clean IGS marker directory and the OEM `drgw2.zip` already present on the card as the import source. Driver/archive identity is stock-curated and hardware-known; give it a unique metadata title `Dragon World II Refresh Control` so publication does not collide with the existing stock catalog identity. Deliberately omit artwork to remove JPEG handling as a variable.

Preparation:
1. back up then remove/rename `/ARCADE/IGS/.refresh-set` so the run begins with no stale markers;
2. copy existing OEM `/ARCADE/bin/drgw2.zip` to `/ARCADE/IGS/import/drgw2.zip`;
3. provide `/ARCADE/IGS/meta/drgw2.txt` containing `Dragon World II Refresh Control`;
4. no `drgw2.jpg/.jpeg` for this control;
5. run Refresh once.

Expected publication: `Dragon World II Refresh Control.zfb`, catalog title of the same friendly name, embedded/runtime target `drgw2.zip`.

Decision:
- if Refresh returns responsive, the Test15 lock is not an intrinsic IGS command/catalog lifecycle failure; stale-marker/Test13-15 fixture contamination becomes the primary cause class, and launch can then be checked with a known-stock runtime;
- if it locks after `Games Added`, the failure is reproduced with clean marker state and a stock-curated IGS driver, closing the fixture/runtime ambiguity and justifying deeper materializer-state tracing.

Fixture package: `xgo-arcade-test16-clean-igs-control.zip`, SHA-256 `ce775aa11e964fd41bdc4a0215aedbd05c411bab325fab520c5feb914221ba63`. It contains only the metadata/control instructions; it does not redistribute ROM data.


## 16. Test16 HW result — Refresh Failed before publication

Hardware result reported 2026-09-29: clean-marker `drgw2.zip` control returned **Refresh Failed**, not Games Added and not the prior post-success hard lock.

This is a different failure class from Test15. Because `drgw2` is a stock-curated PGM driver/archive identity, the result points back into the pre-materialization compatibility gate rather than catalog publication or frontend return. The current XACM validator is therefore not equivalent to stock PGM dependency resolution for this control.

The source-level reason is now concrete: `xgo_arcade_compat_engine.c` validates every required descriptor in the imported game ZIP alone. The previously closed PGM callback archaeology explicitly established that PGM uses `STDROMPICKEXT(..., pgm)`, with shared board ROM descriptors owned by `/bios/pgm.zip`. The implementation never opens/searches that board archive (nor parent archives), despite the finding requiring search ownership order game -> parent -> board ROM. Thus a legitimate stock PGM archive can be rejected by the Refresh validator before materialization.

Test16 therefore does **not** test the Test15 return lock. It exposes an independent validator implementation gap. Do not alter catalog/runtime code from this result. Next candidate must first make PGM validation honor shared-board dependency ownership, then repeat the clean stock control.


## 17. Test16 interpretation correction — board-ROM theory retracted

A source/reuse-first audit after the Test16 `Refresh Failed` result disproves the immediately recorded explanation that the validator rejects stock PGM games because it fails to search `/bios/pgm.zip`.

The PGM callback finding remains correct: stock PGM has shared board-ROM descriptors. However, the manifest generator intentionally extracts **game-specific ROM descriptors only** from the `STDROMPICKEXT` callback and retains `parent`/`board` merely as metadata. XACM v1 therefore does not contain the shared PGM board descriptors as requirements in the imported game ZIP. The Stage2 engine cannot reject `drgw2.zip` for absence of `pgm_p01s.rom`, `pgm_t01s.rom`, or `pgm_m01s.rom`, because those records are not in the driver's XACM ROM slice.

This correction preserves both facts:
- BIN/SRC: PGM dependency ownership is real;
- SRC: current XACM v1 validates only the game-specific descriptor stream.

Therefore commit `725b615e...` captured the HW result correctly but its causal interpretation was premature. Test16 `Refresh Failed` returns to OPEN. Do not implement board-ROM lookup as a response to this result.

### More important fixture defect

The Test16 control procedure copied `/ARCADE/bin/drgw2.zip` into `/ARCADE/IGS/import/drgw2.zip` while the stock catalog already contains Dragon World II. The materializer/Refresh path is append/idempotence-oriented and the test also changed marker state independently. That makes the probe unsuitable for isolating the Test15 post-publication lock: it was not a clean *new publication* control.

The OEM-unlisted `Puzzle Star.zfb` / `puzlstar.zip` pair recovered from the original-card inventory remains the correct provenance-backed IGS publication fixture. No further HW test is authorized until its exact XACM game-descriptor contract and current import/materializer decision path are simulated offline.

### Process lesson

Do not patch the validator from a family-level dependency theory until the exact generated XACM record for the failing driver has been inspected. The manifest's extraction boundary can intentionally remove dependencies that exist in the stock callback stream.


## 18. Corrected offline direction after Test16

The immediate Test16 failure does not authorize another hardware probe. Reuse/source audit establishes:

1. XACM v1 is intentionally a **game-specific descriptor** manifest. PGM shared-board descriptors are excluded at extraction time; board/parent names are metadata. Therefore adding `/bios/pgm.zip` lookup to Stage2 would solve a problem the current manifest does not present.
2. The stock `drgw2` control was not a valid new-publication discriminator because it is already represented in the stock IGS catalog. Refresh's planner is catalog-membership/idempotence oriented; using an already-cataloged driver while independently clearing markers mixed two state contracts.
3. The correct unlisted OEM control remains Puzzle Star: original-card inventory independently pairs `Puzzle Star.zfb` with `/ARCADE/bin/puzlstar.zip`, and the compiled driver is in the stock PGM family. Unlike `drgw2`, it is absent from the visible stock six-entry IGS catalog.
4. Before any HW candidate, the exact `puzlstar` game-specific descriptor stream must be recovered from stock BIN/XACM and the OEM `puzlstar.zip` must be validated offline against it. If the actual OEM archive bytes are not present in repository/artifacts, that missing user-owned file is the only justified input request.

No Test17 is authorized at this point.


## 19. OEM Puzzle Star archive recovered — exact fixture identity

User supplied the original-card `/ARCADE/bin/puzlstar.zip`.

Exact archive:
- size 5,980,261 bytes
- SHA-256 `9de64ad5a4a6ac547da9ca40471628edace1a0c58fcf9d44ef286f6907fc73ce`

ZIP members:
- `a0800.u1` 4,194,304 CRC32 `e1e6ec40`
- `b0800.u3` 2,097,152 CRC32 `52e7bef5`
- `m0800.u2` 4,194,304 CRC32 `e1a46541`
- `t0800.u5` 2,097,152 CRC32 `f9d84e59`
- `v100mg.u1` 524,288 CRC32 `5788b77d`
- `v100mg.u2` 524,288 CRC32 `4c79d979`

This closes the user-owned fixture acquisition gate. The archive is the exact size independently recorded in the original-card inventory and its basename matches the recovered OEM wrapper/runtime pair `Puzzle Star.zfb -> puzlstar.zip`.

Next offline task is exact stock-BIN/XACM descriptor comparison. No hardware test is authorized merely from archive recovery.


## 20. Puzzle Star stock-BIN compatibility gate CLOSED

Direct extraction from exact stock XGO `bisrv.asd` identifies:
- driver index 1069
- short name `puzlstar`
- system `PGM`
- parent: none
- board: `pgm`
- ROM-info callback `0x80494FB8`
- game-specific descriptor table `0x80B1A690`

Required game-owned descriptors:
- `v100mg.u1` 524288 CRC `5788b77d`
- `v100mg.u2` 524288 CRC `4c79d979`
- `t0800.u5` 2097152 CRC `f9d84e59`
- `a0800.u1` 4194304 CRC `e1e6ec40`
- `b0800.u3` 2097152 CRC `52e7bef5`
- `m0800.u2` 4194304 CRC `e1a46541`

The user-supplied original-card `puzlstar.zip` matches **all six required descriptors exactly by filename, uncompressed size, and CRC32**. There are no extra/missing game-owned requirements in the recovered XGO callback slice.

Thus Puzzle Star is now a fully provenance-backed compatibility fixture:
OEM card inventory + exact OEM archive bytes + exact stock XGO compiled driver contract all agree.

This also demonstrates that the XACM game-owned-descriptor model is sufficient for this fixture; no speculative board-ROM validator change is required before publication testing.


## 21. Test17 authorized — OEM Puzzle Star clean IGS publication control

Offline gate is complete. The exact OEM `puzlstar.zip` matches every game-owned descriptor in the stock XGO `puzlstar` callback, and Puzzle Star is physically vendor-supplied yet absent from the visible stock IGS catalog. This is the first clean fixture that simultaneously satisfies provenance, exact XACM/BIN compatibility, IGS family identity, and new-publication semantics.

No firmware/helper change is made. Protected Test15 code remains byte-identical.

Fixture overlay:
- `ARCADE/IGS/import/puzlstar.zip`
- `ARCADE/IGS/meta/puzlstar.txt` = `Puzzle Star`
- no artwork payload, intentionally removing JPEG conversion from this discriminator
- package SHA-256 `dab7d63c39842148a0d2fa785038a4b8c7cac974403bf12ba75f3dcdefb4cbc8`

Precondition: IGS import and transient `.refresh-set` must contain no prior Test13-16 fixture residue; only `puzlstar.zip` is presented to the IGS import pass. Existing OEM `/ARCADE/bin/puzlstar.zip` and/or `/ARCADE/Puzzle Star.zfb`, if present, are legitimate reusable physical assets and should not be deleted merely for this test.

Single HW question: after a genuine new IGS catalog publication of the exact OEM-compatible Puzzle Star fixture, does native Refresh return responsive after `Games Added`?

If responsive, launch Puzzle Star as the secondary observation because its exact OEM runtime archive is now provenance/BIN compatible. If Refresh locks after Games Added, the post-publication IGS lifecycle defect is reproduced independently of The Gladiator and its runtime compatibility.

This is the first post-Test15 hardware probe that is authorized by the full corrected evidence chain.


## 22. Physical SD audit closes current IGS Refresh Failed cause

User supplied the actual current `/ARCADE` tree after Test18. This exposes a concrete filesystem-contract break that explains why IGS worked at Test15 and every later clean-control run returned `Refresh Failed`.

Current physical IGS tree contains:
`/ARCADE/IGS/.refreshset/`

It does **not** contain:
`/ARCADE/IGS/.refresh-set/`

Exact Test15 IGS binaries both require the hyphenated pathname:
- `refresh.xgc` literal: `/mnt/sda1/ARCADE/IGS/.refresh-set/`
- `catalog.xgc` literal: `/mnt/sda1/ARCADE/IGS/.refresh-set`

The wrongly named `.refreshset` directory contains the historical Test13-15 markers (`theglad.zfb`, `The Gladiator.zfb.zfb`, `The Gladiator.zfb`), proving it is the old marker directory renamed during cleanup rather than a directory created by current helpers.

CPS1 and CPS2 on the same physical SD still have correctly named `.refresh-set` directories and are the known working family controls.

This also explains the timeline: Test15 succeeded through publication while the required IGS marker directory existed. The Test16/Test17 cleanup procedure explicitly instructed removal/rename of `.refresh-set`. The materializer writes a marker *inside* that directory but does not establish a replacement directory under the misspelled name. Once the required parent directory disappeared, IGS materialization could reach marker publication and fail. Test18 bypassed preflight but could not repair this missing filesystem prerequisite, so it also returned `Refresh Failed`.

Therefore Test16/Test17/Test18 do not demonstrate an IGS validator failure. Their common physical prerequisite was broken.

Next test must restore the directory name exactly and restore the exact Test15 IGS `refresh.xgc`; no firmware, catalog helper, validator, artwork, wrapper, or runtime change is justified.


## 23. Test19 HW result — required IGS marker directory restoration changes failure to No New Games

Hardware result: after restoring the exact required `/ARCADE/IGS/.refresh-set/` directory and exact Test15 IGS `refresh.xgc`, Arcade Refresh returned **No New Games** and remained responsive.

This confirms the prior `Refresh Failed` state in Tests16-18 was caused at least in material part by the broken physical filesystem prerequisite introduced when `.refresh-set` was removed/renamed during cleanup. Those tests are invalid as evidence that IGS preflight/validator itself was rejecting the fixture.

Test19 does not yet prove new IGS publication because `No New Games` means the current on-card state converged to no appendable change. Before another HW test, inspect the actual SD state and marker/catalog/assets to determine why Puzzle Star is considered unchanged. Do not delete/rename structural directories. Cleanup, if needed, may clear only proven transient contents while preserving required path topology.


## 24. HW MILESTONE — IGS end-to-end Refresh proven with Puzzle Star + artwork

Hardware result reported 2026-09-29 after restoring the required IGS filesystem contract and using the exact OEM Puzzle Star runtime fixture:

- Refresh status: **Games Added**
- frontend return: **responsive; no freeze**
- catalog publication: **Puzzle Star appears in the IGS list**
- artwork: **generated/displayed successfully from the supplied `puzlstar.jpg`**
- launch: **Puzzle Star launches and is playable**

This is the first clean end-to-end IGS Refresh proof covering:
`import ZIP + metadata + JPEG -> materializer -> ZFB/artwork -> marker -> catalog append -> native return -> frontend display -> runtime launch`.

The successful fixture uses the exact OEM `puzlstar.zip` previously matched against the stock XGO PGM driver descriptors. The artwork input was 144x208 JPEG and the generated wrapper path was `/ARCADE/Puzzle Star.zfb`.

### Superseded failure interpretation

Tests16-18 must not be used as evidence that IGS preflight/validator or runtime was intrinsically broken. Their common environment had lost the required `/ARCADE/IGS/.refresh-set/` directory after an erroneous cleanup instruction. Restoring that structural prerequisite first changed behavior to `No New Games`; removing only the already-converged `Puzzle Star.zfb` then restored a genuine new-publication transition and produced this full HW pass.

### Protected IGS rule

`/ARCADE/IGS/.refresh-set/` is structural runtime state. Its **contents** may be transient markers; the directory itself must be preserved. Never delete/rename a Refresh directory before proving whether helper code requires its existence.

IGS family functionality is now HW-proven. Preserve this exact mechanism while continuing four-family parity work; common validator refinement remains secondary.


## 25. NeoGeo physical-SD gate — current helper is correct; import filename is not

After the IGS HW pass, the user requested continuation to NeoGeo with the supplied physical SD tree as the authority before further changes.

Direct audit of `arcde.zip`:
- `/ARCADE/NEOGEO/refresh.xgc`: 1,056,520 bytes, SHA-256 `b8d7e99637dea8f217e062040a4550283f7542b040232e20ad54526115a36a9f` — exact protected Test15 NeoGeo helper.
- family selector at +0x2618 = 3.
- import-prefix skip at +0x0BE4 = 31, exactly the NeoGeo path length.
- staging reference at +0x21D8 targets relocated +0x3000.
- +0x3000 contains exact required `/mnt/sda1/ARCADE/NEOGEO/.refresh-set/`.
- `/ARCADE/NEOGEO/catalog.xgc`: SHA-256 `6f91ff89aeecea7f3128bdbdbd66e2a0eca2df46257ca93edcd02aa790f3ac7c`; it targets stock NeoGeo triplet `rmapi.tax/pcadm.nec/ntdll.bvs` and the same required marker directory.
- physical `.refresh-set/` directory exists.
- metadata exists: `bstars.txt` = `Baseball Stars Pro`.
- artwork exists: `bstars.jpg`.
- **physical import is misnamed `bstarszip`, with no dot.**

The dynamic preflight/materializer enumerates only names ending in `.zip`. Therefore the current physical NeoGeo fixture is invisible to Refresh. No helper/catalog/firmware change is justified.

The 3,472,134-byte `bstarszip` is a valid ZIP (SHA-256 `15b18b01df522625340fd237263853ee1a994e5803626058d837c4063da94905`). Direct stock-XGO driver extraction for `bstars` (Neo Geo driver index 789) gives 14 game-owned ROM requirements. Every required CRC+size is present in this archive; filename extensions differ but the validator deliberately accepts CRC+size identity. Thus the fixture is exact-XACM compatible offline.

Test20 is therefore a filesystem-only correction: present those exact bytes as `/ARCADE/NEOGEO/import/bstars.zip`, preserve the exact Test15 NeoGeo refresh/catalog helpers, artwork, metadata, and structural `.refresh-set/`. Package SHA-256 `e97ec6d77da015468b422f8fb69dc936fa2aa66ae82e7a3257edddb91a1beadc`.

Single HW boundary: Refresh once. Expected new-publication path is Games Added -> `Baseball Stars Pro` with artwork -> responsive return -> launch/play. Any different result is new NeoGeo-specific evidence; do not alter other families.


## 25. Test21 NeoGeo HW result — materialization commits state, catalog publication does not

HW result after correcting the physical NeoGeo fixture to a visible `bstars.zip` import and proven 600x400 RGB JPEG input:
1. selecting Arcade Refresh **hard-locked** before a native status message;
2. after reboot, a second Refresh returned **No New Games**;
3. NeoGeo game list was **not updated**.

This is materially different from Test20's immediate `Refresh Failed`. Test21 consumed/converged enough state that the next run reports no-change, but the NeoGeo catalog did not receive the new entry. Treat this as a transaction split between materializer output/marker state and NeoGeo catalog publication, not as evidence to modify validator policy.

Next step is an actual post-Test21 SD-state capture/comparison: inspect generated root ZFB, runtime bin ZIP, NeoGeo `.refresh-set` marker, and the three NeoGeo resource files. Do not delete or rename anything before that capture; the committed partial state is the evidence needed to locate the NeoGeo-only boundary.


## 26. Post-Test21 physical SD capture — NeoGeo split located before marker publication

User supplied an untouched post-Test21 `ARCADE` capture. Mechanical comparison with the pre-Test21 capture proves:
- NEW `/ARCADE/Baseball Stars Pro.zfb`, 59,920 bytes, SHA-256 `ee8c2da9ec72e8a38986a1022bbf97ee32b0be97e3801a253322139affe804de`;
- wrapper preview prefix is byte-identical to the new 59,904-byte `.xgo.rgb565`;
- wrapper tail is exactly four zero bytes + `bstars.zip\0\0`;
- corrected `/ARCADE/NEOGEO/import/bstars.zip` exists;
- **no** `/ARCADE/NEOGEO/.refresh-set/Baseball Stars Pro.zfb` marker exists;
- NeoGeo resource triplet remains stock count 117 and contains no Baseball Stars Pro entry.

Therefore Test21's hard lock occurred **after successful JPEG/RGB565/wrapper construction but before marker creation**. The subsequent `No New Games` is explained by the already-converged final wrapper short-circuiting the materializer while no marker remains for the catalog stage. This is the exact transaction split.

Test22 is authorized as a marker-only recovery discriminator: create only the missing zero-byte `/ARCADE/NEOGEO/.refresh-set/Baseball Stars Pro.zfb` and run Refresh once. It changes no executable, catalog, ROM, artwork, wrapper, or directory topology. If catalog publication succeeds, NeoGeo catalog helper semantics are cleared and the remaining defect is isolated to the NeoGeo materializer's post-wrapper marker path.


## 26. Test22 HW PASS — NeoGeo catalog/runtime path proven; defect isolated to marker creation

Hardware result reported 2026-09-29 from the untouched post-Test21 state plus one manually supplied zero-byte marker:
`/ARCADE/NEOGEO/.refresh-set/Baseball Stars Pro.zfb`

Result:
- Refresh: **Games Added**
- frontend return: **responsive**
- NeoGeo list: **updated**
- artwork: **displayed**
- launch: **Baseball Stars Pro playable**

No executable, ROM, artwork, wrapper, catalog file, or directory was deleted/renamed for this discriminator.

This closes the NeoGeo catalog helper, synchronized resource-triplet publication, frontend reload/return, wrapper identity, runtime ZIP identity, and game launch path as HW-good. Combined with the untouched post-Test21 capture, the remaining NeoGeo defect is now tightly isolated: the normal materializer creates the valid final `Baseball Stars Pro.zfb` and then hard-locks before creating the required `.refresh-set/Baseball Stars Pro.zfb` marker. Supplying only that missing marker allows the rest of the pipeline to complete end-to-end.

Next work is OFFLINE: mechanically compare the Test15 NeoGeo materializer's post-wrapper/marker-creation sequence against HW-working CPS1/CPS2/IGS, paying special attention to NeoGeo's relocated staging pathname at +0x3000 and any compiled address/capacity assumptions. Do not ask hardware to retest catalog/runtime behavior already proven by Test22.


## 27. NeoGeo post-wrapper marker failure — offline binary comparison

Test22 proves the catalog/runtime half is good. Mechanical comparison of exact Test15 family materializers now reduces the post-wrapper finalizer difference to one instruction:

- CPS1/CPS2/IGS at `+0x21D8`: `addiu a2,a2,0x258c`
- NeoGeo at `+0x21D8`: `addiu a2,a2,0x3000`

The surrounding marker-builder/finalizer instructions are byte-identical. NeoGeo alone relocated its longer staging pathname from the inherited +0x258c slot to +0x3000. Test21 then HW-proved a lock precisely before marker creation, while Test22 proved manually supplying that marker completes publication/runtime.

The current +0x3000 location is therefore the only executable/addressing delta at the isolated failure boundary. Re-audit found a 0x320-byte zero-owned cave at +0x2CE0..+0x2FFF, immediately after the dynamic preflight block/data and before +0x3000. A minimal candidate can relocate only the NeoGeo staging string to +0x2CE0 and retarget the single `addiu` immediate, leaving validator policy, materializer logic, wrapper/artwork code, catalog helper, ROM, and all other families unchanged.

This is an evidence-backed candidate, not yet HW-proven. Preserve Test22 as proof that no catalog/runtime change is required.


## 28. Test23 HW FAIL — +0x2CE0 relocation does not fix NeoGeo marker transition

Hardware result:
- clean transition was prepared by deleting only the generated `/ARCADE/Baseball Stars Pro.zfb` and `/ARCADE/NEOGEO/.refresh-set/Baseball Stars Pro.zfb`, preserving the required `.refresh-set/` directory;
- exact 117-entry pre-Test22 NeoGeo resource triplet was restored;
- Test23 NeoGeo helper relocated the marker staging pathname from +0x3000 to +0x2CE0 and retargeted only the finalizer pointer;
- every Arcade Refresh attempt **hard-locks**;
- reboot/retry hard-locks again;
- game list is **not updated**.

Therefore the earlier inference that +0x3000 itself was the defect is falsified. Test22 remains the key boundary proof: manually supplying the marker makes catalog publication/artwork/runtime pass. The unresolved defect is still in the automatic materializer path at or before marker publication, but it is not repaired merely by moving the staging pathname to another zero-owned cave.

Do not ask for another hardware candidate until the materializer finalizer is disassembled/traced against HW-working CPS1/CPS2/IGS and the exact call at +0x21E4/+0x21F8, its buffer ownership, and return/error branches are resolved offline.


## 29. CORRECTION — Test21 did not isolate the lock specifically to marker creation

Re-audit of the untouched post-Test21 physical capture `arcde(1).zip` found:
- `/ARCADE/Baseball Stars Pro.zfb` exists and has the valid `bstars.zip` trailer;
- **`/ARCADE/bin/bstars.zip` does not exist**;
- **the NeoGeo .refresh-set marker does not exist**.

This corrects sections 26–28 where the lock was described too narrowly as a marker-creation failure. The documented materializer splice contract is: final ZFB -> runtime ZIP convergence -> marker. Therefore the physical evidence places the Test21/Test23 failure **after final ZFB creation but before completion of runtime-ZIP convergence and marker publication**. Marker creation is not yet proven to be the first failing operation.

Test22 remains important but must be interpreted carefully: the manually seeded marker allowed the subsequent Refresh to publish the catalog and the game was HW-playable. Because no post-Test22 physical capture was taken, that run may also have converged `/ARCADE/bin/bstars.zip`; it does not prove that marker creation alone was the original failing instruction.

The +0x3000/+0x2CE0 marker-string relocation hypothesis is therefore rejected not only by Test23 HW failure but also because it targeted a later stage than the first missing post-wrapper artifact.

Offline priority is reset to the runtime-ZIP convergence block immediately following final ZFB convergence. No further hardware candidate until that block is mechanically compared with CPS1/CPS2/IGS and its state/idempotency behavior is resolved.


## 29. Runtime-ZIP convergence block mechanically closed; next defect boundary corrected again

Disassembly of exact Test15 CPS1/CPS2/IGS/NeoGeo helpers shows the complete materializer core at +0x2000..+0x2397 is instruction-identical across all four families except NeoGeo's already-known marker-root pointer at +0x21D8. In particular, the runtime-ZIP path construction and convergence logic is identical:

- +0x2118..+0x2158 builds the import source pathname in the 0x87002828 0x100-byte scratch buffer from family import-root + ROM stem + `.zip`.
- +0x2160..+0x219C builds the common `/mnt/sda1/ARCADE/bin/<stem>.zip` destination in the 0x87002728 0x100-byte scratch buffer.
- +0x21A8 calls the shared compare/convergence helper at 0x870023F4.
- +0x21C0 repeats the same convergence helper and requires return == 1 before entering marker construction at +0x21D0.
- 0x870023F4 opens both built paths, compares/copies in 0x2000-byte chunks, closes both streams, and returns 0/1/-1 according to convergence state.

NeoGeo's import literal at +0x25C8 is 32 bytes including NUL and ends exactly at +0x25E7. This is within its intended literal slot and the resulting `bstars.zip` source path is only 42 bytes including NUL, far below the 0x100-byte scratch bound. Destination is shorter. There is no NeoGeo-specific executable difference in runtime-ZIP convergence itself.

Important remaining anomaly: +0x25E8 is immediately reused as the 0x140-byte marker-path scratch buffer, yet executable code begins at +0x2600 only 24 bytes later. Marker construction necessarily overwrites +0x2600 onward. This is true in all four propagated helpers, so it cannot alone explain NeoGeo unless the working families avoid re-entering the overwritten region while NeoGeo's control/state causes a re-entry. The marker file is opened at +0x222C using this scratch path.

The post-Test21 capture lacking `ARCADE/bin/bstars.zip` still proves the first-pass transaction did not leave runtime ZIP convergence durable, but the static code comparison does not support a NeoGeo-specific bug in the copy routine. Next offline task is to reconcile Test21/Test23 persistence with helper return/re-entry semantics and inspect whether the 0x25E8 self-overwrite is part of the repeated-lock mechanism before generating another candidate.


## 30. Marker scratch self-overwrite resolved as a real implementation defect

Further control-flow tracing closes the ambiguity around the 0x870025E8 marker scratch buffer.

The helper entry at +0x0008 calls the dynamic preflight entry at +0x2600 exactly once, before materialization. The +0x2600 block returns to the wrapper entry; there are no later direct calls from the materializer finalizer back into +0x2600. Therefore overwriting +0x2600 during marker construction does not necessarily crash the same invocation, explaining why CPS1/CPS2/IGS could pass despite the defect.

However, +0x25E8 is unquestionably an unsafe scratch allocation: the finalizer treats it as a 0x140-byte mutable marker-path buffer at +0x21E0/+0x21FC/+0x2224, while executable preflight code begins at +0x2600. Any normal marker pathname overwrites the loaded helper's preflight code. This is self-modifying corruption, not merely adjacent data.

The zero-owned region after the XGO preflight metadata is large enough for a proper scratch object. In the Test15 NeoGeo image, +0x3025 onward is zero-filled; +0x3100..+0x323F provides a 0x140-byte scratch region with no code/data ownership. NeoGeo's marker-root literal can remain at +0x3000. A minimal repair therefore retargets only the three marker destination references:
- +0x21E0: destination base +0x25E8 -> +0x3100
- +0x21FC: destination base +0x25E8 -> +0x3100
- +0x2224: fopen pathname +0x25E8 -> +0x3100

This differs fundamentally from failed Test23, which moved only the marker SOURCE string and left the corrupting destination at +0x25E8. No validator, runtime-ZIP, catalog, ROM, artwork, or family logic needs to change.

Before HW candidate generation, restore the original Test15 NeoGeo marker-root source at +0x3000 (not Test23's +0x2CE0) and mechanically audit that +0x3100..+0x323F is zero-owned and has no static references.


## 31. Test24 HW result — scratch relocation changes failure mode but does not complete publication

Hardware result:
- Test24 moved only the NeoGeo marker-path destination scratch from unsafe +0x25E8 to zero-owned +0x3100, preserving the original marker-root source at +0x3000 and restoring the exact 117-entry pre-Test22 NeoGeo resource triplet.
- First Arcade Refresh returned **Refresh Failed** rather than hard-locking.
- Immediate second Refresh returned **No New Games**.
- Baseball Stars Pro was **not added to the game list**.

Interpretation discipline:
- Test24 falsifies the claim that fixing the marker scratch self-overwrite alone closes NeoGeo publication.
- The changed first-run behavior (hard-lock -> explicit Refresh Failed) is evidence that removing self-overwrite affected control/return behavior, but it does not prove the remaining failure is specifically marker creation.
- The second-run No New Games again indicates durable convergence/state was written on the first pass while catalog publication remained absent.
- Do not generate Test25 from another code guess. Preserve current post-Test24 SD state and capture it physically before further modification so wrapper, runtime ZIP, marker, import and catalog triplet can be compared against post-Test21/Test22 evidence.


## 32. Post-Test24 physical capture — exact persistence boundary

User supplied the untouched post-Test24 Arcade tree after first `Refresh Failed` and second `No New Games`.

Physical evidence:
- `/ARCADE/Baseball Stars Pro.zfb` EXISTS, size 59,920, SHA-256 `ee8c2da9ec72e8a38986a1022bbf97ee32b0be97e3801a253322139affe804de`.
- Wrapper trailer is structurally correct and contains `bstars.zip`.
- `/ARCADE/NEOGEO/.refresh-set/` EXISTS.
- `/ARCADE/NEOGEO/.refresh-set/Baseball Stars Pro.zfb` is ABSENT.
- `/ARCADE/NEOGEO/import/bstars.zip` EXISTS, size 3,472,134, SHA-256 `15b18b01df522625340fd237263853ee1a994e5803626058d837c4063da94905`.
- Test24 helper is exactly installed: SHA-256 `efdcd6c44fd7ae55db91123f74a7cc4cbb2d590bd99d8cb3996624051dcefb01`.
- NeoGeo catalog helper remains SHA-256 `6f91ff89aeecea7f3128bdbdbd66e2a0eca2df46257ca93edcd02aa790f3ac7c`.
- No `/ARCADE/bin/` directory or runtime ZIP is present in the supplied Arcade capture.
- Game list remains unpublished per HW observation.

This reproduces the Test21 durable state, but Test24 converts the former hard-lock into a controlled `Refresh Failed`. Therefore scratch relocation fixed a real control-corruption symptom while exposing the underlying transaction failure.

The first durable missing artifact after the completed ZFB remains runtime ZIP convergence. The immediate second-run `No New Games` is now explained as a materializer/preflight idempotence issue: existence of the generated root wrapper is sufficient to suppress another import attempt even though later transaction artifacts (runtime ZIP, marker/catalog publication) are absent. Do not treat `No New Games` as successful convergence.

Next offline task: disassemble the +0x227C copy/create branch and reconcile its `/ARCADE/bin/` destination contract with physical HW-working CPS1/CPS2/IGS captures, which also show no persisted `/ARCADE/bin/` contents. Do not alter current SD state.


### Correction to section 32 — capture omission is not filesystem absence

User clarified that the physical SD card **does contain** the `/ARCADE/bin/` directory and the runtime ZIP; that directory was intentionally omitted from the uploaded `arcade.zip` solely to keep the upload small enough for chat.

Therefore retract the section-32 statements/inferences that:
- no physical `/ARCADE/bin/` directory/runtime ZIP exists;
- the first durable missing artifact is runtime-ZIP convergence;
- the next investigation should be driven by supposed absence of `/ARCADE/bin/`.

The uploaded capture establishes only that `bin/` was not included in the archive. It provides no evidence about physical `bin/` state. User's direct HW observation establishes that the directory and ZIP are physically present.

The valid post-Test24 boundary from the capture + HW observation is instead:
- generated root ZFB exists and is structurally correct;
- runtime ZIP physically exists in `/ARCADE/bin/`;
- required `.refresh-set/` directory exists;
- per included tree, Baseball Stars Pro publication marker is absent;
- catalog/list publication is absent;
- first run returns controlled `Refresh Failed`, second run `No New Games`.

Thus Test24 now closes runtime-ZIP convergence as successful and isolates the remaining automatic failure to **after runtime-ZIP convergence and before/at marker creation**. Resume offline analysis at marker pathname construction/open/close and its return semantics, not runtime-ZIP copying.


## 33. Expanded post-Test24 capture closes runtime ZIP convergence physically

User supplied a more complete post-Test24 SD capture, intentionally retaining only the relevant runtime ZIP in `/ARCADE/bin/`.

Physical verification:
- `/ARCADE/NEOGEO/import/bstars.zip`: 3,472,134 bytes, SHA-256 `15b18b01df522625340fd237263853ee1a994e5803626058d837c4063da94905`.
- `/ARCADE/bin/bstars.zip`: 3,472,134 bytes, SHA-256 `15b18b01df522625340fd237263853ee1a994e5803626058d837c4063da94905`.
- The two ZIPs are byte-for-byte identical. Runtime ZIP convergence is therefore HW/physical proven successful in Test24.
- `/ARCADE/Baseball Stars Pro.zfb`: 59,920 bytes, SHA-256 `ee8c2da9ec72e8a38986a1022bbf97ee32b0be97e3801a253322139affe804de`.
- NeoGeo `.refresh-set/` exists but contains no Baseball Stars Pro marker. Existing markers are only CPS1 `1941.zfb`, CPS2 `1944.zfb`, and IGS `Puzzle Star.zfb`.
- NeoGeo resource triplet remains exact pre-publication 117-entry state:
  - rmapi.tax SHA `921a605a...`, count 117
  - pcadm.nec SHA `697b3b98...`, count 117
  - ntdll.bvs SHA `6336c727...`, count 117

This definitively closes the Test24 transaction boundary:
**wrapper complete -> runtime ZIP converged byte-identically -> marker creation fails -> catalog remains untouched -> Refresh Failed.**

The next offline investigation is exclusively marker construction/create semantics after +0x21C0. Do not revisit runtime ZIP convergence.


## 34. Marker create narrowed to pathname geometry; Test25 discriminator

Exact Test24 marker finalizer disassembly:
- marker source root: `/mnt/sda1/ARCADE/NEOGEO/.refresh-set/`
- enriched-name source at `0x87600400` is the complete outer wrapper filename including `.zfb`; Test15 intentionally removed the redundant suffix append.
- marker destination scratch is now safely at +0x3100.
- finalizer calls stock stdio fopen wrapper `0x802B3524` with mode `wb`, then fclose `0x802B2F40`; absent physical marker after Test24 means create/commit did not succeed.
- stock fopen routes the pathname through a 0x400-byte canonicalization buffer, so no generic 56-byte software buffer was found offline. Nevertheless NeoGeo's full marker pathname is 60 bytes including NUL, materially longer than the HW-proven IGS Puzzle Star marker path, and path/directory geometry is now the remaining family-local input at the failing fopen boundary.

Test25 is a controlled pathname-geometry discriminator, not a claimed final architecture. It preserves Test24's safe +0x3100 marker scratch and all materializer/catalog logic, but shortens only the NeoGeo marker directory:
`.refresh-set/` -> `.r/`
in both the materializer and NeoGeo catalog helper. This reduces the Baseball Stars Pro marker pathname from 60 bytes including NUL to 50, approximately the proven IGS geometry, while preserving the complete friendly marker filename.

Test25 hashes:
- helper SHA-256 `ec5bd91f6c1161bd4f285cbd4bf9848daf63c8ba9726bf3f49a92af7898dcf2d`
- catalog helper SHA-256 `2da7642100baed5778f81c1db0e464b4cd01160f6f5b293045f26242ee9235e6`
- package SHA-256 `1c03ccadc932452900d7750303eb55e8bcda7a66dc3df0f61f1e3214d7d32ff5`
- exact 117-entry NeoGeo resource triplet retained.
- existing byte-identical `/ARCADE/bin/bstars.zip` may remain; delete only generated root `/ARCADE/Baseball Stars Pro.zfb` before the test.

Interpretation:
- If Test25 creates `.r/Baseball Stars Pro.zfb` and publishes, the unresolved failure is marker pathname/directory geometry rather than ZIP convergence or catalog logic.
- If it still fails with no marker, pathname length is rejected and investigation returns to fopen/create semantics or runtime contents of the enriched-name buffer.
