# Test42 follow-up — SD inspection closes missing-file hypothesis

Date: 2026-09-09
Branch: research-game-list-arcade-expansion

User showed D:\Resources on the physical SD. clm.tax, clm.nec, clm.bvs and clssic.r56 are physically present.

Therefore Test42 failure is NOT evidence that CLASSIC catalog resources are absent from SD.

Offline audit of the exact Test33A package:
- Resources/clm.tax = 71 bytes
- Resources/clm.nec = 71 bytes
- Resources/clm.bvs = 71 bytes
- each has count=3, offsets [0,12,27], strings:
  Pac-Man.zfb
  Ms Pac-Man.zfb
  Cadillacs and Dinosaurs.zfb

New leading suspect:
Tests 40-42 introduced fseeko (0x802b3804) and ftell (0x802b3f1c) to discover catalog length. These calls/signatures were not part of the hardware-proven Test04 catalog writer contract. Test04 used fopen/fread/fwrite/fclose with known lengths.

Next diagnostic should eliminate fseeko/ftell entirely:
- fopen absolute /mnt/sda1/Resources/clm.tax
- fread(catbuf,1,4096,f)
- use returned byte count as size
- validate count/header in RAM
- close
- no writes

If that passes, use the same direct-fread length in the next single-catalog writer.

Repository hygiene note:
Physical SD contains experimental leftovers from multiple branches (mame2000, mame2000_xgo_t12, cores/classic/refresh.bin, loader.bin, etc.). Update ZIP installs do not necessarily delete obsolete files. After Refresh is closed, create a canonical runtime-layout cleanup/migration package and document which paths are active before renaming proven core paths.
