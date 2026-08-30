# Research Log

## 2026-08-30 — Initial forensic pass

- Confirmed tested XGO requires its microSD card to boot.
- Windows Disk Management sees the 32 GB card as a single FAT32 primary partition.
- Inventoried 6,558 filesystem entries.
- Preserved `bios/`, `Resources/`, and filesystem inventory for analysis.
- Identified `bios/bisrv.asd` as an `LCFG` application image.
- Found `SF2000` literal in `Resources/Foldername.ini`.
- Matched XGO resource/database naming conventions to documented SF2000 formats.
- Recovered emulator/core identification strings from `bisrv.asd`.
- Recovered explicit Player 2 and USB attach/detach strings.
- Connected earlier controller experiments with product-family documentation calling the mystery port `Handle Interface`.
- Identified `Resources/Test.zsf` as a likely explanation for the previously observed controller diagnostic screen.
- Located active open-source SF2000-family work (particularly UniFrog) as a potential reference architecture for an eventual XGO-specific target.

## Next research targets

- Produce a reproducible binary comparison against known SF2000 firmware specimens.
- Map `bisrv.asd` sections/signatures and locate external-input-related code regions.
- Determine the XGO SoC from direct evidence rather than reseller claims.
- Inspect MBR, FAT32 reserved sectors, and pre-partition area from a small extract of the preserved raw card image.
- Characterize the Handle Interface electrically/protocol-wise.
- Find photographs/listings/manuals for the original external XGO controller accessory.
- Determine a reproducible way to launch `Test.zsf` and test P2 state.
