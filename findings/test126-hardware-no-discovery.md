# Test126 — corrected handheld isolation hardware result

Date: 2026-09-22
Branch: `research-refresh-gb-gbc-gba`

Status: **HW FAIL for discovery — isolation correction did not restore raw-ROM discovery**

## Hardware observation

With the corrected Test126 GB/GBC/GBA Stage2 resource-table descriptors installed:

- GB Refresh -> **No New Games**
- GBC Refresh -> **No New Games**
- GBA Refresh -> **No New Games**

The pending raw GBC/GBA ROMs therefore were not discovered.

No cross-family contamination was reported in this test. That is useful evidence
that the Test125 24-byte-stride descriptor bug was real and corrected, but it
does **not** make Test126 a discovery pass.

CLASSIC is not implicated by this result.

## Interpretation boundary

The corrected resource pointers alone are insufficient. The remaining failure
must be closed against the exact HW-passed Test08 worker before another
hardware candidate.

Do not produce Test127 by guessing another descriptor, classifier range, or
frontend status patch.

## Required next audit

1. Decode the exact 3601-byte Test08 scanner from
   `build_test08_all_console_scanner_candidate.py`.
2. Recover instruction-level per-system behavior for Test08 IDs 4/5/6:
   resource-table pointer calculation, folder/path construction, extension
   classification, scratch-base setup, classifier-global save/restore,
   count-cache invalidation, and loop/reset behavior.
3. Compare those instructions/semantics against the relocated Test126 Stage2
   workers.
4. Pay special attention to assumptions that are valid in the original
   `0x807DAB98` cave but may not survive execution as a Stage2 helper at
   `0x87180000`.
5. Only after the discrepancy is directly identified should a new candidate be
   emitted.

Test125 remains HW FAIL due cross-family corruption. Test126 is a separate HW
FAIL because corrected isolated workers still do not discover pending raw
handheld ROMs.
