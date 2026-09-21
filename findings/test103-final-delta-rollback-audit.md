# Test103 final extraction-delta and rollback audit

## Byte-for-byte package delta versus Test97

A complete ZIP entry manifest comparison was performed.

Only three differences exist:

ADDED:
- TEST103-OFFLINE-MANIFEST.json

REMOVED:
- MD/catalog.xgc

CHANGED:
- bios/bisrv.asd

Every other Test97 payload entry is byte-identical.

Firmware:
- Test97: b66dbcd86ad785875a6804bb7d07c6eb1195ceedb01c0bce8107f65eee2ab66e
- Test103: 170f4cef000578ae3245ffcfb16758a0e6f506f01c139b854c5f4a883bf9301e

## Resource overwrite audit

Candidate contains no MD catalog triplet.

The only Resources payload is:
- Resources/ihdsf.bke

This is inherited unchanged from Test97 and is unrelated to the MD TAX/NEC/BVS triplet.

MD payload contains only:
- MD/refresh.xgc

Therefore extracting Test103 cannot overwrite scksp.tax, setxa.nec, or wmiui.bvs. Their preflight restoration/validation remains under explicit operator control.

## Important additive-extraction caveat

Because ZIP extraction is additive, removing MD/catalog.xgc from the ZIP does NOT delete an already-existing MD/catalog.xgc from the SD.

This is safe for Test103 execution because firmware no longer calls that helper, but for archaeological cleanliness the stale file may remain physically present.

Do not require deletion before the first hardware test: deleting another file adds unnecessary SD mutation. Record it as dormant/stale and remove it only during a later controlled cleanup.

## Rollback model

Rollback has two independent layers:

Firmware rollback:
- restore exact Test97 bios/bisrv.asd (SHA b66dbcd...ab66e) or the user's protected cumulative baseline package.

Catalog rollback:
- restore all three MD catalog files as one matched generation.
- currently pinned coherent baseline is the pristine 788 triplet:
  scksp.tax d04479d8...bba01
  setxa.nec 835be147...8197c
  wmiui.bvs 60acca83...bf1a8

Never roll back only one member of the triplet.

## Pre-test preservation

Before first Test103 hardware invocation:
1. Preserve current SD image or at minimum copy the complete current Resources triplet and MD directory off-card.
2. Restore/verify exact coherent 788 triplet.
3. Verify Test103 firmware hash after extraction if practical.
4. Do not alter existing .zmd wrappers solely to reduce scanner workload.
5. Invoke Refresh once.
6. Enter MD once immediately.
7. If responsive, exit normally and power down normally before forensic copy.
8. If hard-locked, do not run Refresh again after reboot; preserve resulting triplet and firmware state for analysis.

## Gate conclusion

Package payload delta: CLOSED.
Catalog overwrite risk from package: CLOSED.
Rollback procedure: CLOSED.
Additive stale-helper issue: UNDERSTOOD and non-executing.

The remaining decision is operational risk: whether to perform the first hardware validation on a cloned/sacrificial card or the production card after complete backup. No further firmware modification is required for Test103.
