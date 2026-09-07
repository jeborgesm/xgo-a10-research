# Direct DY19 stock-image extraction and XGO comparison

Date: 2026-09-07

## Source image recovered selectively

Internet Archive item:

`dy-19-firmware-2024315`

Original image:

`DY19Firmware2024315.img`

Size:
`31,266,439,168 bytes`

Internet Archive hashes:

- MD5 `1195478159615405ddf55c2a644d69f7`
- SHA-1 `f82c5e34f9456636e1ffeef5224e6fbc2befda56`

The project did **not** download the 31GB ROM payload. Instead, a reproducible HTTP-Range FAT32 reader recovered only BIOS, Resources and small metadata files.

## Disk geometry

The image is a full-disk MBR image:

- partition type: `0x0c` FAT32 LBA
- partition start: sector 8192 = 4 MiB
- partition sectors: 60,612,608
- FAT32 OEM string: `MSDOS5.0`
- 512-byte sectors
- 64 sectors/cluster = 32 KiB clusters
- two FATs
- FAT size: 7,398 sectors
- root cluster: 2

Root directories include:

```text
FC
GB
GBA
GBC
MD
Resources
SFC
ARCADE
BIOS
Download
```

This is structurally the same broad card architecture as XGO/SF2000-family devices.

## DY19 application binary recovered

Recovered:

`BIOS/BISRV.ASD`

DY19 size:

`12,477,596 bytes`

SHA-256:

`135ddf837f37570cedbd204036e02bdede876338ad94a9c33cac0db5ac8fe9e4`

XGO preserved specimen:

`12,768,452 bytes`

SHA-256:

`869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf`

Both begin with the same `LCFG` application-image header.

They are **not byte-identical**, but direct binary inspection shows unmistakable common ancestry.

## Exact shared firmware fingerprints

Both DY19 and XGO contain:

```text
h1512_gpio_pinmux_sel
Libcore version 3.6.1.1@SDK3.AB_20210616
(gcc version 3.4.4 mipssde-6.06.01-20070420)
MARIOVSDK
/mnt/sda1/UpdateFirmware/Firmware.upk
%s/Resources/Foldername.ini
FCEUmm
Snes9x 2005
```

The SDK/compiler string is byte-identical.

The XGO-specific RF test strings:

```text
RF_IC Test Fail !
RF_IC Test Pass!
```

are **absent from the recovered DY19 application**.

This is an important board/runtime difference and is consistent with XGO retaining an RF-controller path that is not present in this DY19 build.

## Low-level binary similarity

At the same file offsets, DY19 and XGO share about **29% of bytes** across the entire shorter image.

There are many exact 4-KiB blocks shared at identical or nearby offsets.

The first large population of H1512 GPIO `0xb880....` load instructions occurs at the **same offsets in both binaries**. For example, dozens of early `lui ...,0xb880` sites are position-identical before later sections begin to shift.

Counts:

- XGO generic `lui ?,0xb880` hits: 749
- DY19: 743

This is much stronger evidence than shared strings alone: large parts of the compiled low-level platform code retain the same link layout.

## Controller scanner result

The exact XGO controller-scanner byte prefixes at:

- XGO offset `0x35D6F0`
- XGO offset `0x35D770`
- XGO offset `0x35DEB0`

do **not** occur byte-for-byte in DY19.

Therefore the direct comparison now confirms:

- shared H1512 GPIO/platform implementation;
- **different controller/input adaptation code** in the relevant later application region.

This matches real-world reports where sibling firmware can boot while controls fail.

It also means the XGO B15/L0/B7 12-bit serial scanner must still be treated as XGO/board-specific until a semantic DY19 disassembly says otherwise.

## Resource corpus comparison

The selective extraction recovered 117 DY19 Resources files small enough for direct comparison.

Against the corresponding small XGO Resource corpus:

- 65 filenames overlap;
- 10 of those files are byte-identical;
- 55 overlap by name but differ in content.

Examples of byte-identical shared resource files include:

```text
aepic.nec
bttlve.kbp
dpnet.dll
help.lis
igc64.dll
jccatm.kbp
sensc.bvs
subst.tax
swapfile.sys
wshrm.nec
```

This proves actual payload reuse, not merely reuse of opaque filenames.

## Strongest game-database result

The DY19 card contains `_orig` backups for many list/resource files while current files have been reduced to four-byte placeholders.

That means this owner image is **not a pristine untouched seller card**; it had undergone a tool/modification step that preserved original list files as backups.

Those `_orig` list files are extremely valuable because they preserve the original DY19 game databases.

Comparison of DY19 original list filenames against XGO shows:

| System | DY19 games | XGO games | XGO entries found in DY19 |
|---|---:|---:|---:|
| FC | 867 | 743 | **743 / 743** |
| SFC | 1165 | 927 | **927 / 927** |
| MD | 910 | 786 | **786 / 786** |
| GB | 1139 | 883 | **883 / 883** |
| GBC | 1109 | 956 | **956 / 956** |
| GBA | 760 | 624 | **624 / 624** |
| CPS1 | 28 | 26 | **26 / 26** |
| CPS2 | 29 | 28 | **28 / 28** |
| Neo Geo | 135 | 117 | 114 / 117 |
| IGS/PGM | 6 | 6 | **6 / 6** |

For eight of the ten systems, **every XGO game-list filename is a subset of the DY19 original list**.

The IGS/PGM triplet is even stronger:

```text
subst.tax
aepic.nec
sensc.bvs
```

is **byte-for-byte identical between DY19 and XGO**.

This materially upgrades the lineage conclusion: XGO did not merely reuse the DY19 list-slot naming convention. Its shipped game catalog appears to have been **derived from the same DY19 content set, usually by pruning games from a larger DY19 list**.

## Shared UI text, with fork-specific additions

DY19 `MLage.ini` and XGO `fhshl.skb` share the exact text:

```text
Loading......
Folder is empty。
Archive already exists,
overwrite this archive?
Archive save failed .
Please check TF card
after power off .
LOW BATTERY!
Please charge it in time.
Save the progress, Power off and charge.
Search
No games match the keyword.
```

DY19 additionally includes explicit joystick-key-mapping instructions.

XGO additionally includes Resume/Quit/Load/Save and Favorites messages.

This is consistent with sibling frontend forks sharing a common UI-resource base and diverging in features.

## Foldername.ini differs substantially

DY19 recovered `Foldername.ini`:

- 378 bytes
- SHA-256 `dedd70233f3ddfe741c701495dbdf229ec21bf0bc38700434380abfbd58f6e5f`
- begins with `AHHM3`
- includes eight explicit featured game ZIPs
- contains a `12 11 0` tuple and expanded ARCADE entries.

XGO:

- 208 bytes
- SHA-256 `080b036d4ca0c9c1195b8bd15f1d8fec67da7630e8c19fd002ab444efc303c49`
- begins with `SF2000`
- uses `11 7 0`.

This is a high-level frontend/configuration fork difference, not a contradiction of common lineage.

## Bottom line

The recovered DY19 image resolves a major open question.

**Confirmed:**

1. XGO and DY19 do not use byte-identical `bisrv.asd`.
2. They use the same H1512 SDK/compiler/application family.
3. Large portions of low-level binary layout remain shared.
4. Their board-specific input/RF regions diverge.
5. They reuse real resource payloads, not only filenames.
6. XGO's shipped game lists are overwhelmingly subsets of the larger DY19 original lists.
7. The IGS list triplet is byte-identical.
8. XGO is therefore best described as a **DY19-family software/content fork with XGO-specific board adaptation**, rather than merely an SF2000-like device.

## Reproducibility

The HTTP-range extractor is preserved at:

`tools/dy19/remote_fat32_extract.py`

The GitHub Actions probe can recover the firmware/resource subset without downloading the entire 31GB image.

Workflow artifact from the first successful selective extraction:

- run: `34149462986`
- artifact id: `10028835373`
- artifact ZIP SHA-256: `3d7ebfb44fd0c31a6b022b4d58018da9bb7518de1b4ed7493a0d0a6229dc19d6`

