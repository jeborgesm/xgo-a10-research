# Arcade Test11 — dynamic CPS1 preflight enumeration

Date: 2026-09-28

Parent architecture: Test10 HW PASS. Compatibility validation remains entirely before materialization.

Test11 removes the fixed 1941 source/stem literals from Test10's preflight. It uses the recovered stock directory ABI:
- open 0x807D40C4
- next 0x807D4124
- close 0x807D41F4

The preflight enumerates CPS1/import, ignores directories/non-ZIP files, derives source path and driver stem dynamically, validates every ZIP through XACM, closes the directory, and only then enters the proven Test05A materializer once.

For this narrow HW proof, the family is all-compatible-or-no-change: any incompatible/unsupported ZIP prevents the family materializer from running. This is deliberately not the final per-file quarantine policy; it proves dynamic enumeration without allowing an incompatible file to reach Test05A. Per-file skip/quarantine follows after this boundary is HW-proven.

Codescape audit run: 36503930359 PASS.
Dynamic preflight binary: 1756 bytes, SHA256 `1718795337ab8e9d2a952476df68a25314c23f29455b20a51f3909a22ff8ba1b`.
Stage2 SHA256 `503eb939cb5124a4ae71eecf427b238a511ab3db79addbc4bc87270cf59faed1`.
Test11 refresh.xgc SHA256 `5a3abb3cfe9841fc761f7778ae0b9cfc53afdd335d5f6393dc326e18e233549d`.
Package SHA256 `1328e60f86998376e59982964b4eccc6c4394b3bfc1a0c80ffff43252225a9d3`.

Mechanical parent reconstruction was hash-verified against Test05A SHA256 `2d6503ae20937bd9d525d68a18ee845d942667b582e71e2371450a83d8d29ad2`. Test11 changes only the entry JAL and previously-zero cave beginning +0x2600; artwork/JPEG/finalizer body remains byte-identical to Test05A.

HW probe: CPS1/import contains only the known compatible 1941.zip; remove generated 1941.zfb; retain CPS1/art/1941.jpg. Expected Games Updated, visible artwork, playable 1941.


## HW result — PASS (2026-09-28)

User hardware observation:
- Refresh reported Games Added;
- game appeared in CPS1 list with artwork;
- game launched and ran normally.

Interpretation: Test11 is **not hardcoded for a successful validator verdict**. Unlike Test10, the Test11 preflight does not contain a literal `1941.zip` source path or `1941` driver stem. It enumerates `/mnt/sda1/ARCADE/CPS1/import` through the recovered stock directory ABI, derives the candidate pathname and stem from the directory entry, and passes those derived values to XACM validation. The HW run therefore proves the dynamic-enumeration path can reach the proven Test05A body without regressing artwork or launch.

Scope remains narrow: family selection is CPS1 in the Test11 entry wrapper, and the current family preflight is all-compatible-or-no-change rather than final per-file quarantine. Test11 is evidence for dynamic candidate discovery, not the final four-family implementation.
