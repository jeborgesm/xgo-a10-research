# XGO GBA Save-Sidecar Provisioning

Status: **factory/preload save-sidecar provisioning strongly established from card inventory and gpSP behavior**.

## Major finding

The preserved XGO card contains **490 `.sav` files directly beside GBA packaged ROMs** in the `GBA` directory.

These are not a random set of user-created saves:

- all 490 `.sav` basenames exactly match a physically present `.zgb` GBA ROM basename;
- there are **zero orphan `.sav` files**;
- 485 of the 490 files share the exact timestamp `2023-06-29 13:12:10`, strongly indicating batch generation during card preparation;
- only five exact file sizes occur;
- those sizes correspond exactly to the backup-memory sizes that gpSP uses to infer GBA save hardware type.

The card therefore appears to have been deliberately provisioned with save sidecars so gpSP can identify each game's backup-memory type immediately from the existing save-file size.

## Exact card inventory

The `GBA` root contains:

```text
656 packaged .zgb ROMs
490 matching .sav files
166 ROMs without a pre-existing .sav
0 orphan .sav files
```

The 490 sidecars have the following exact size distribution:

```text
512 bytes      232 files
8192 bytes      92 files
32768 bytes    119 files
65536 bytes     45 files
131072 bytes     2 files
```

The two 128 KiB sidecars are:

```text
Calciobit (CN).sav
Sennen Kazoku.sav
```

## Why the sizes are semantically meaningful

The gpSP source lineage embedded in XGO keeps a 128 KiB `gamepak_backup` buffer and supports:

```text
EEPROM 512 B
EEPROM 8 KiB
SRAM 32 KiB / 64 KiB
FLASH 64 KiB / 128 KiB
```

More importantly, gpSP's `load_backup()` explicitly says:

```text
The size might give away what kind of backup it is.
```

and classifies an existing save file by exact length:

```text
0x0200   -> EEPROM, 512-byte mode
0x2000   -> EEPROM, 8-KiB mode
0x8000   -> SRAM, 32-KiB mode
0x10000  -> FLASH, 64-KiB mode
0x20000  -> FLASH, 128-KiB mode
```

This is an exact one-to-one match with every `.sav` size present on the XGO card.

Therefore an existing `.sav` is not only persistent game data. Its **file size is input to gpSP's save-hardware detection path**.

## XGO core corroboration

The XGO `bisrv.asd` contains gpSP strings and diagnostics for:

```text
.sav
game_config.txt
game_name
game_code
vender_code
idle_loop_eliminate_target
translation_gate_target
iwram_stack_optimize
flash_rom_type
128KB
game config missing
gamepak_ram_buffer_size:%d
```

The public gpSP `game_config.txt` documentation explains that `flash_rom_type = 128KB` is required for specific games that use 128 KiB Flash backup hardware.

No `game_config.txt` is present in the preserved XGO card file listing. The XGO core retains the generic gpSP per-game configuration machinery, but the mass-preprovisioned `.sav` files give the vendor another reliable way for the backup loader to begin with the intended memory geometry whenever a sidecar already exists.

This does **not** prove that every sidecar was generated solely for type detection; their actual byte contents were not included in the analysis archive, so some may also contain initialized or non-empty save data. The size-based role, however, is directly supported by gpSP's loader logic.

## Reconstructed provisioned backup-type counts

Using gpSP's exact size classifier, the shipped sidecars imply:

```text
EEPROM 512 B   : 232 games
EEPROM 8 KiB   :  92 games
SRAM 32 KiB    : 119 games
FLASH 64 KiB   :  45 games
FLASH 128 KiB  :   2 games
```

These counts describe the **preprovisioned files**, not necessarily the true backup-memory distribution of all 656 shipped GBA games. The remaining 166 games have no pre-existing `.sav` and may rely on runtime auto-detection/default behavior until a save is first written.

## Card-production implication

The timestamp clustering is especially revealing:

```text
485 / 490 .sav files -> 2023-06-29 13:12:10
```

This strongly suggests a vendor/OEM preprocessing step rather than hundreds of independent gameplay sessions. The GBA ROM packages themselves mostly carry earlier February 2023 timestamps, so the save-sidecar population appears to have been applied later as a separate card-build operation.

Thus the SD card was not assembled simply by copying ROMs and firmware. It was **post-processed with emulator-specific compatibility/provisioning data**.

## Confidence

### CONFIRMED

- 490 GBA-root `.sav` files exist in the original card inventory;
- every one matches an existing `.zgb` basename;
- no orphan sidecars exist;
- exact size distribution is 512 / 8192 / 32768 / 65536 / 131072 bytes;
- 485 files share one exact timestamp;
- gpSP `load_backup()` uses those same exact five sizes to determine EEPROM/SRAM/Flash backup geometry;
- XGO `bisrv.asd` contains the same gpSP save/config lineage and `.sav` handling strings.

### STRONG EVIDENCE

- the bulk of the sidecars were generated as part of OEM/card preparation;
- their existence pre-seeds gpSP with the desired backup-memory type for those games.

### OPEN

- actual contents of the 490 `.sav` files (not preserved in the uploaded analysis archive);
- whether they are blank `0xFF`/zero-filled templates, initialized game data, or a mixture;
- how the vendor selected which 490 of 656 GBA titles received sidecars;
- whether the 166 games without sidecars were tested and known to auto-detect correctly;
- whether XGO's compiled gpSP fork adds any additional sidecar-size behavior beyond upstream gpSP.
