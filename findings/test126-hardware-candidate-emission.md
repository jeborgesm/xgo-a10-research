# Test126 corrected handheld isolation hardware candidate

Date: 2026-09-22
Branch: `research-refresh-gb-gbc-gba`
Status: **HARDWARE CANDIDATE — not golden**

Candidate:
`xgo-test126-gb-gbc-gba-corrected-isolation-HARDWARE-CANDIDATE.zip`

ZIP SHA-256:
`7c8d23a02ac66e02be860b90899b6200717e8f0a152ecac5189583fd5dfad9f3`

Firmware is byte-identical to Test125:
`4e5eb643ede9aa9883fa0ddf5590f92098af4baf369682bfa9ef3d4e185fd6c8`
LCFG CRC: `0xB34148B3`

Only the three Stage2 handheld workers differ from Test125. Stage1 is unchanged.

Corrected Stage2:
- GB  `6b3ec79439e7597044024bbf04a959b0309078c3e56b3884c8e277cc12f89568`
- GBC `a79fb1b98ff6253d541e471a3741cb2dbed08dbf928621e2eb70192b4d2395f6`
- GBA `1111a51ce927c68599df1dd0b8b958b3e7303ac1cb0b27f04c2e31f882a02635`

GitHub Actions isolation run `35811199041` passed:
- GB names=0x80A3C35C count=0x80D28964 folder=GB
- GBC names=0x80A3C368 count=0x80D2896C folder=GBC
- GBA names=0x80A3C374 count=0x80D28974 folder=GBA

Artifact helper build run `35812684071`, artifact `10730920871`, completed successfully.

## Hardware sequence

Use the existing pending GBC/GBA Mario files as blind evidence.

1. Install Test126 over the current cumulative SD.
2. Refresh GBC once.
   Expected: Games Updated; pending GBC ROM appears only in GBC and launches.
3. Refresh GBC once more.
   Expected: No New Games; responsive.
4. Refresh GBA once.
   Expected: Games Updated; pending GBA ROM appears only in GBA and launches.
5. Refresh GBA once more.
   Expected: No New Games; responsive.
6. Refresh GB once.
   Expected: No New Games if no other unindexed GB files remain; existing GB entries remain playable and no GBC/GBA entries cross into GB.
7. Refresh CLASSIC once.
   Expected: No New Games if unchanged; CLASSIC activates normally.

Do not spam Refresh.

A PASS proves corrected selective discovery/isolation only. It does not close
the branch; import/art/meta -> stock-shaped .zgb enrichment remains required.
