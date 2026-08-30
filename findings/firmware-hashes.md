# Firmware Specimen Metadata

## Tested XGO `bios/bisrv.asd`

| Property | Value |
| --- | --- |
| Size | 12,768,452 bytes |
| CRC32 | `DD70C40B` |
| SHA-256 | `869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf` |
| Header magic | `LCFG` |
| Observed file timestamp | 2023-08-12 |

These values identify the research specimen without redistributing the proprietary firmware.

## Comparison notes

Known SF2000 firmware images are similar in size but not identical. The XGO image is larger than commonly documented stock SF2000 v1.6/v1.71 images, supporting the conclusion that this is a modified/forked image rather than an untouched SF2000 binary with cosmetic resources.

A future reproducible comparison should record exact upstream image hashes and generate binary similarity/diff statistics rather than relying on file size alone.
