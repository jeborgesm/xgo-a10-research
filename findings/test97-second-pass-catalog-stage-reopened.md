# Test97 second-pass investigation — catalog-stage fault reopened

## Correction after full helper trace

The generic runner can return -1 before executing a helper, but the user's direct-after-reboot MD Refresh failure disproves the earlier FC/SFC cumulative-call explanation. Do not use invocation count as an explanation.

A full trace of Test97 MD refresh.xgc also confirms:
- output existence check uses /MD/<friendly>.zmd at 0x4F4;
- if that fopen succeeds, helper closes it and skips directly to the next import entry;
- the supplied MD.zip contains exactly the expected friendly .zmd files.

## DCC fact

Function 0xDCC counts source filename length including the NUL and then subtracts 5. This is exactly correct for four-character extensions including dot (.nes/.sfc) but one character too short for .md. Test102's -5 -> -4 change was therefore semantically correct for this helper.

However, current clean artifacts show friendly names/artwork that cannot be explained by the unmodified Test97 DCC path using the supplied full-stem meta/art filenames. Do not silently reconcile this contradiction. Possible provenance/pre-existing-state effects must be resolved.

## More important fault-stage distinction

Selective dispatcher runs TWO helpers:
1. MD/refresh.xgc
2. MD/catalog.xgc

UI only exposes aggregate failure. Therefore a direct-after-reboot Refresh Failed does NOT establish that refresh.xgc failed. It may:
- successfully return 0 after skipping all existing friendly wrappers;
- then MD/catalog.xgc return -1 while reopening/parsing the triplet written by the first successful import.

This is now a high-value hypothesis because:
- wrappers are valid/playable;
- frontend reads the updated catalog successfully after reboot;
- catalog helper could still reject or mishandle its own appended representation on a second mutation/scan;
- FC/SFC no-change behavior does not prove MD post-write triplet is identical in structure.

## Required forensic fixture

Need the CURRENT post-Test97 MD catalog triplet from the SD card, unchanged:
- /Resources/scksp.tax
- /Resources/setxa.nec
- /Resources/wmiui.bvs

Compare these against known-good baseline from XGoAnalisis.zip and reconstruct the exact appended MD records. This requires no hardware execution and can determine whether catalog.xgc can parse its own output on pass 2.

Do not run another Refresh before capturing these files.
