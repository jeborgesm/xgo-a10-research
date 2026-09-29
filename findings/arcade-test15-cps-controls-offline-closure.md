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
