# Test131 reboot discriminator — persistent GB catalog still stock

Date: 2026-09-23
Status: HW evidence; catalog merge failure isolated

After Test131:
- first GB Refresh -> Games Updated
- second unchanged GB Refresh -> No New Games
- visible GB list remained stock and prior scanner-added entries disappeared.

A reboot discriminator was then performed without another Refresh before opening Game Boy.

Observed after reboot:
- Game Boy list is still stock.

## Consequence

This falsifies the narrow hypothesis that Test131 had already written the correct
persistent GB catalog and only left the live frontend/native workspace stale.

The failure is now upstream of frontend reload: the persistent catalog consumed at
boot does not contain the expected imported GB entry.

The Test131 materializer remains HW-proven:
- corrected helper pathname reaches execution;
- first pass reports changed;
- second pass reports no change.

The next target is exclusively GB catalog persistence/merge:
1. determine exactly which triplet Test131 catalog.xgc opens and rewrites;
2. verify its record count/stride and wrapper filter;
3. compare the GB helper byte-for-byte with its FC/SFC parent and enumerate every
   system-specific substitution;
4. verify 0x80D28964 is only cache state and not being confused with catalog identity;
5. inspect whether GB has multiple stock catalog triplets/regions or a different
   list-ID mapping than assumed.

Do not modify the GB materializer and do not attribute the failure to stale live
workspace unless later evidence reopens that possibility.
