# Test130 deeper closure — MD individual invocation ancestry and remaining runner exits

Date: 2026-09-23
Status: **BIN/HW consolidation; no new hardware candidate**

## User correction retained

MD, not GB, was the first enrichment implementation converted from cumulative Refresh to individual invocation. The closest execution ancestor is therefore the Test85/Test97/Test106 selective MD path.

## Exact binary comparison

Test106 and Test128 are byte-identical at native Refresh entry 0x807DB5CC, native workspace initialization through 0x807DB678, selective hook 0x807DB67C, selective-dispatch prologue 0x80A386BC, generic helper runner 0x80A382E0, and the protected MD body at 0x80A387AC.

Test127/128 diverge only where Test123 expanded the old FC/SFC/else-MD decoder and added a separate GB execution island at 0x80A39050. The GB island reproduces the MD helper-call grammar but is not literally the HW-proven MD branch.

## Test130 consequence

Test130 uses exact Test128 firmware and a size-identical GB helper whose first instructions return v0=1 immediately. Hardware still reports Refresh Failed.

The unchanged generic runner has only three failure gates before helper entry:
1. heap-boundary guard: *(0x80C237B0) > 0x86FFFFFF;
2. fopen(path,"rb") returns NULL;
3. fread return count != requested 0x101F08 bytes.

Once execution reaches 0x87000000, the Test130 helper must return +1 and cannot produce Refresh Failed.

Therefore Test130 is direct HW evidence that one of those three pre-entry gates fails for the GB invocation.

## What is NOT different

The runner itself is unchanged. Native Refresh frame/workspace initialization is unchanged. Requested helper size is the proven 0x101F08. The command body uses the same return test/aggregation grammar as MD.

Thus the remaining variables at the runner boundary are runtime heap-boundary state, pathname/filesystem lookup, and exact file byte availability/read count.

## Repository lesson

Do not alter GB materializer, extension parser, wrapper logic, catalog logic, or generic runner. First close the three pre-entry gates using the proven MD individual invocation lineage.

A future diagnostic, if needed, must be GB-local and distinguish these gates without modifying FC/SFC/MD/CLASSIC.
