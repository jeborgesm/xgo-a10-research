# Test58 hardware PASS, Test59 observation, and image-conversion next step

Date: 2026-09-10

## Test58 hardware result

Hardware PASS for CLASSIC deletion reconciliation.

Deleting a ROM ZIP from `/CLASSIC/bin` and running Refresh removes the corresponding visible CLASSIC entry successfully.

This behavior is now protected together with Test57's completed CLASSIC logo atlas.

## Test59 hardware observation

The external `/CLASSIC/refresh.xgc` architecture executes successfully enough to:

- run Refresh repeatedly;
- remove an old CLASSIC game;
- add a new CLASSIC game;
- consume the `.txt` metadata/display-name sidecar.

However Test59 incorrectly reports `Games Updated` on every Refresh instead of reaching the no-change path. This is being corrected separately by final-catalog comparison rather than a sticky intermediate `changed` flag.

## Artwork observation

An attempted `shinobib.rgb565` sidecar was 143,360 bytes, corresponding to 320 x 224 x 2 bytes. It is plausible RGB565 data but is not the proven XGO CLASSIC preview contract.

Required CLASSIC preview sidecar remains:

- 144 x 208
- little-endian RGB565
- exactly 59,904 bytes

Therefore rejecting the 143,360-byte sidecar was correct.

The desired final workflow remains ordinary source artwork (`.png`/`.jpg`) on SD with on-device resize/letterbox and conversion to the 144 x 208 RGB565 preview.

## Decoder archaeology

Direct firmware string/reference work confirms:

- `image/jpeg` at runtime 0x808BA2A8;
- `image/png` at runtime 0x808BA2CC;
- JPEG hardware/decoder diagnostic string `JPEG scan type no support!` in the 0x8099E6F8 diagnostic cluster;
- a direct MIPS code reference to that JPEG diagnostic cluster from around 0x80230F58.

The firmware also contains codec tables naming `png`, `MPNG`, `PNG1`, MJPEG and related media codecs, so PNG/JPEG support is real firmware functionality rather than only filename-extension strings. The unresolved task is still to map a callable still-image decode path suitable for Refresh.

Because Test59 proved an SD-resident external Refresh helper can execute at 0x87000000, image decode/scale/conversion should be implemented there rather than in the 4,600-byte firmware importer cave.