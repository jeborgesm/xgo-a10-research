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
