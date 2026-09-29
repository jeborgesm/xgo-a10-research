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
