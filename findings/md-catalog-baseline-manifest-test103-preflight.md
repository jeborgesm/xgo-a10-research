# MD catalog baseline manifest and Test103 preflight gate

This manifest is derived from the two available forensic archives and defines the only currently proven coherent MD catalog baseline for a future native-scanner validation.

## Proven coherent baseline: XGoAnalisis.zip

All three files have count 788 and come from the same archive generation.

| File | Size | Count | SHA-256 |
|---|---:|---:|---|
| scksp.tax | 22156 | 788 | d04479d8214233d417ebf1791aa38b030a89b9ee55657c586c997257301bba01 |
| setxa.nec | 15984 | 788 | 835be147cfb05da648385667da6ad5c81467a281ecfa8f71d60bf50d01d8197c |
| wmiui.bvs | 8160 | 788 | 60acca83cbcd3086a1f27c2f9c2f192474759d1711f0adf8c9b9e3419a3bf1a8 |

This is the safest currently available matched triplet.

## Current forensic state: 20260919XGO_MD_Analysis.zip

| File | Size | Count | SHA-256 |
|---|---:|---:|---|
| SCKSP.TAX | 23458 | 839 | ca552d6c67eef499fa8d26dff532e75827947ae0230521db7d420d4237b451ee |
| SETXA.NEC | 17082 | 839 | 44371b1e48c225e4d871a253b4b5c459af42f6c3bf29e269e49c299e3ccdd955 |
| wmiui.bvs | 8160 | 788 | 60acca83cbcd3086a1f27c2f9c2f192474759d1711f0adf8c9b9e3419a3bf1a8 |

This state is intentionally/forensically mixed. BVS is byte-identical to the pristine 788 baseline while TAX/NEC are Test97-expanded 839 files.

Do not invoke Refresh/native scanner on this mixed triplet.

## Preflight rule

A future Test103 package/test procedure must require one of:
1. exact SHA match to the coherent 788 triplet above; or
2. another separately captured triplet whose three structures validate and whose counts match.

For the first hardware validation, prefer exact SHA match to the known 788 triplet. This removes catalog provenance as an experimental variable.

## Expected first-run consequence

Restoring the 788 triplet while leaving Test97-created top-level MD wrappers present means the native scanner should rediscover wrappers absent from the 788 catalog and rebuild catalog state. This is useful because it exercises native scanner integration without requiring the materializer to recreate already-existing wrappers.

However, because there are 51 top-level wrappers absent from the 788 baseline, the scanner may add all 51 in one pass. That is within previously established helper/scanner bounds, but it is a nontrivial live rewrite.

A safer minimal fixture would temporarily expose only the intended four Test97 wrappers beyond the 788 baseline, but changing/removing existing stock wrapper files introduces its own provenance risk. Do not manipulate the production SD solely to create a smaller test fixture unless using a clone/sacrificial card.

## Recommendation for eventual first hardware test

Best: clone/sacrificial card + exact 788 triplet + controlled MD directory.

Acceptable: production card only after exact 788 triplet restore and complete backup, with one Refresh invocation and immediate frontend-state observation, followed by normal shutdown if responsive.

No repeated Refresh, no forced shutdown unless already irrecoverably locked.

## Gate status

Executable Test103 patch: statically closed/minimal.
Catalog baseline: now closed.
Filesystem atomicity: still open.
Hardware release: still gated pending final package audit and recovery procedure.
