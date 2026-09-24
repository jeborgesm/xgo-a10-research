# GB propagation correction — recover the MD selective-refresh architecture first

Date: 2026-09-23
Status: **repository recovery / design correction after Test130**

## Correction

The prior interpretation that GB was the first conversion of an inert command into
an individual generic-helper invocation was wrong.

Repository history shows MD was the first new enrichment implementation to be
converted from the cumulative Refresh chain to individual invocation. Test85/Test97
established the post-native-workspace selective dispatcher architecture specifically
because cumulative FC -> SFC -> MD work was unnecessary when the user normally
refreshes one environment at a time.

Therefore GB propagation must use the **final MD individual-refresh architecture as
its ancestor**, not reconstruct an invocation model from Test75 cumulative Refresh.

## Recovered proven sequence

Native Refresh enters and initializes its full frame/workspace first. At
0x807DB67C the selective dispatcher takes over. For MD the Test97/Test106 lineage
runs the selected materializer and later the MD catalog/persistence contract, then
uses the native Refresh status/epilogue.

Test130 proves command 3 reaches a failure before a trivial GB helper can return.
That is an invocation-boundary problem. Do not change the GB materializer.

## Important historical distinction

Test75 is evidence for enrichment/materialization and the original cumulative
runner, but it is not the closest architectural ancestor for **individual module
invocation**. Test85/Test97/Test106 MD is.

The repository also records that the generic runner has a pre-open heap-boundary
guard at 0x80A38308..0x80A38320. This runner can return -1 before helper execution.
The exact MD individual invocation context and any state/reset assumptions around
that runner must now be compared against Test127/128/130 command 3 byte-for-byte.

## Gate

No Test131 until:
1. exact Test106 MD individual path from native Refresh entry through helper
   execution is reconstructed;
2. exact Test130 GB path is compared against it;
3. every difference before helper entry is enumerated;
4. the reason Test130 can return -1 is closed offline;
5. any fix remains GB-local and leaves FC/SFC/MD/CLASSIC protected.
