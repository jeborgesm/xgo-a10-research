# Arcade Test13 — family path geometry correction

Offline comparison of Test12 CPS1/CPS2 PASS binaries against isolated IGS FAIL found a family-length assumption in the proven materializer body at +0x0BE4:

`addiu v0, at, 29`

29 is not arbitrary: it is `strlen("/mnt/sda1/ARCADE/CPS1/import/")`, and CPS2 has the same length. Test12 changed the family path literals and validator family ID but failed to retarget this compiled prefix-skip geometry. Therefore CPS1 and CPS2 passed while shorter IGS failed after compatible preflight.

Correct values:
- CPS1: 29 (unchanged)
- CPS2: 29 (unchanged)
- IGS: 28
- NeoGeo: 31

This is a direct mechanism matching the HW split; no validator or cleanup behavior is changed.

Test13 hashes:
- package `39dc01afb1200e0b159a6524fb2a89b0986d515d4a0047863a1f29ca6b805a33`
- CPS1 unchanged `5a3abb3cfe9841fc761f7778ae0b9cfc53afdd335d5f6393dc326e18e233549d`
- CPS2 unchanged `81fc5a43f57aad69e89ac9e951750bfa4ffeb362d7c64cc361aa716c92a7bf68`
- IGS `1eca119e25dd4f40c26479f064e127c2ce0c3321dd31fc657137ae803389303d`
- NeoGeo `08ebb7029e38c23cf9a006e76ea849971060f4316cc98b1dba9cb7c5d2706b33`

First HW target: compatible `theglad.zip` alone in IGS/import with `theglad.jpg` in IGS/art. Expected: Games Added, artwork, launch. NeoGeo remains pending a compatible ROM candidate.


## NeoGeo HW probe — Refresh Failed

User tested Test13 with the later `bstars` candidate (archive supplied as `bstars(4).zip`, renamed for import) and Refresh returned **Refresh Failed**.

This means NeoGeo parity is not established. Do not infer that the +0x0BE4 prefix-length correction was sufficient for NeoGeo. The NeoGeo specialization has at least one remaining family-length/path-geometry or materializer specialization defect, OR the candidate does not satisfy the exact XACM contract despite containing the sought alternate program payload. Re-run exact manifest validation and mechanically compare every path-length-dependent immediate/reference against CPS1/CPS2 before requesting another HW probe.


### Correction — Test13 probe was combined IGS + NeoGeo, not NeoGeo-only

User clarified that the Refresh Failed observation was obtained with **both IGS and NeoGeo candidates present simultaneously**. Therefore the previous wording must not be interpreted as an isolated NeoGeo Test13 failure.

Current evidence after Test13:
- CPS1: PASS (prior HW)
- CPS2: PASS (prior HW)
- IGS: Test12 isolated FAIL; **Test13 not yet isolated**
- NeoGeo: **not yet isolated through materialization**
- Test13 combined IGS+NeoGeo: Refresh Failed

Because command6/aggregate status reports failure if either family returns failure, the combined Test13 result cannot identify which family failed. Do not mark NeoGeo individually failed from this run and do not mark the IGS path-length fix failed until an isolated Test13 IGS run exists.


## Isolated Test13 IGS result — FAIL

User removed NeoGeo candidate and ran Test13 with only compatible `theglad.zip` in IGS import. Result: **Refresh Failed**.

Therefore the +0x0BE4 import-prefix skip correction was real but **not sufficient** to specialize the Test11 CPS1 materializer for IGS. IGS remains independently broken after Test13. NeoGeo remains unisolated.

Next work is offline binary archaeology only: compare all path-derived arithmetic, literal references, staging/finalizer assumptions and family-dependent geometry in the materializer against the working equal-length CPS1/CPS2 cases. Do not request another HW test until a complete mechanical delta audit identifies the remaining IGS-specific assumption(s).


## Offline audit after isolated IGS failure — test artwork violated proven JPEG input geometry

A full Test13 CPS1-vs-IGS binary delta audit found only the intended family specializations: IGS family ID, family path literals, and the corrected import-prefix skip. No second hidden CPS1/IGS executable delta was present.

The remaining test-input difference exposed a separate mistake in the HW fixture: the assistant-generated `theglad.jpg` supplied for the IGS test is **887x887 RGB JFIF**. The physical artwork path previously proven on Test05A used an ordinary **600x400 RGB JFIF** source. Therefore the isolated IGS failure has not yet cleanly falsified the IGS specialization: its artwork input was outside the hardware-proven JPEG-worker input geometry.

Do not patch firmware again before controlling this variable. A replacement of the same generated artwork has been prepared at exactly 600x400 RGB JFIF. Next HW probe keeps Test13 firmware and compatible `theglad.zip` unchanged and changes only the JPEG fixture to the proven 600x400 geometry. If this still returns Refresh Failed, resume materializer archaeology; if it passes, the apparent IGS code failure was an invalid artwork test fixture.


## Isolated IGS rerun with 600x400 JPEG — partial pipeline PASS, semantic specialization FAIL

User replaced the earlier square test artwork with a 600x400 JPEG matching the HW-proven JPEG input geometry and reran Test13 with IGS `theglad.zip` alone.

HW observation:
- Refresh completed and reported **Games Added**;
- list entry was added as literal filename-derived **`theglad`**, ignoring supplied metadata;
- no artwork appeared (and no black fallback preview appeared either);
- game did not run.

Interpretation: this is materially different from the earlier Refresh Failed result. IGS now reaches successful publication/aggregate status, so the 28-byte import-prefix correction plus proven JPEG geometry removed the hard failure. However, the generated IGS entry is semantically wrong: metadata/artwork/runtime identity specialization is not equivalent to the working CPS1/CPS2 path. The absence of even the black fallback is especially strong evidence that this is not merely a JPEG decode failure; the IGS wrapper/finalization path or family-specific literal/reference geometry is wrong.

Do not promote IGS. Next work is offline comparison of the actual generated IGS artifacts/path identities against CPS1/CPS2 contracts; no validator or cleanup work yet.


## Captured Test13 IGS output — wrapper/artwork are actually correct; catalog publication is wrong

User supplied the exact post-Refresh IGS outputs in `igs.zip`. Offline inspection:

- `The Gladiator.zfb`: 59,921 bytes, SHA256 `39cb098cab5a7ebabbd621698065016e12ae8eb73a404f17901d6eda9060f6c9`
- `.xgo.rgb565`: 59,904 bytes, SHA256 `2fa20ba67982b94db573f8407803f28752a5fee54e290d93954cc3b64eb904a8`
- the wrapper's entire 0xEA00 preview prefix is byte-for-byte identical to `.xgo.rgb565`
- wrapper tail at 0xEA00 is exactly `00 00 00 00 'theglad.zip' 00 00`
- therefore metadata title selection, JPEG decode, RGB565 generation, wrapper construction, and runtime ZIP basename embedding all succeeded.
- `.refresh-set/theglad.zfb` exists as a zero-byte marker.
- runtime `theglad.zip` exists, 20,377,176 bytes, SHA256 `31aac538a31f1c0c5db132659ddfd8dc033268d902e728837b832141a6ec2cc1`.

Captured IGS catalog triplet has count 7, but the appended seventh entries are:
- SUBST.TAX: `theglad.zfb`
- AEPIC.NEC: `theglad`
- SENSC.BVS: `theglad`

This explains the observed bare `theglad` entry and missing image: the enriched wrapper `The Gladiator.zfb` is valid on disk, but the catalog helper publishes filename-derived `theglad.zfb` instead of the enriched outer wrapper filename. The frontend therefore cannot open the actual enriched wrapper. The earlier interpretation that IGS wrapper/finalization itself was broken is superseded by this artifact evidence.

Next fix must target IGS catalog publication/marker naming contract, not JPEG/materializer internals.


## Test14 HW — FAIL; marker-title substitution was wrong

HW observation after Test14 IGS rerun:
- Refresh reported Games Updated;
- IGS list now contains two bad appended entries: prior `theglad` plus new `The Gladiator.zfb`;
- neither entry displays artwork;
- neither launches.

The photo confirms the new slot is rendered literally as **The Gladiator.zfb**, including extension, unlike stock titles. Therefore Test14's assumption that the marker basename could simply be replaced by the enriched wrapper display filename is false. The catalog helper is not a transparent marker->slot0 publisher; its three synchronized slots have their own naming/normalization contract. Test14 is rejected and must not be promoted.

Important: the prior captured Test13 artifact still proves `The Gladiator.zfb` itself was correctly built with artwork and embedded `theglad.zip`. The unresolved boundary is catalog triplet construction / launcher identity, not JPEG decoding.
