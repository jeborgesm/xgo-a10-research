# DY19 stock firmware recovery and DY12 revision lineage

Date: 2026-09-07

## Major recovery result: public DY19 stock image exists in two independent locations

The DY19 firmware is no longer only a "known filename" target.

### Internet Archive owner dump

In the r/SBCGaming thread "Got a Powerbank Handheld, time to play around with it", owner MarsRT states that he ripped the entire DY19 SD-card partition and uploaded it to Internet Archive.

Exact item:

`https://archive.org/details/dy-19-firmware-2024315`

He explicitly says the image is what he ripped from the SD card and recommends writing it with Win32DiskImager.

This is especially important because it is an **owner-originated stock-card dump**, not merely a reseller firmware package.

### Handhelds Wiki stock firmware mirror

The DY19 Handhelds Wiki page independently publishes a stock-firmware link:

`https://mega.nz/file/4gN2jB6R#x1yYkAIgynTIVxuSdDJgtsQm3_vXRMgW0eRxGXip9qc`

This gives the project two independent public recovery routes:
- Internet Archive owner dump;
- MEGA stock-firmware mirror.

The actual payloads have not yet been downloaded and hash-compared by this project, so they should not be assumed identical until verified.

## Why this is a major opportunity

A genuine DY19 stock image can provide:

- `bios/bisrv.asd`;
- `Resources/`;
- original list/database files;
- stock language/theme resources;
- exact folder layout;
- device-specific controller/LCD adaptation;
- game-registration data needed for comparison to XGO Test04/game-list work.

The 4PDA owner report that the nominal 30GB image contains only about 40MB of meaningful system files reinforces the plan to extract only the firmware/resource layer rather than preserve bulk ROM content.

## Multicore compatibility confirmed by an actual DY19 owner

MarsRT documents a working procedure where DY19 uses:

1. SF2000 bootloader update;
2. SF2000 vanilla/resources;
3. SF2000 multicore files;
4. a **DY19-specific `bisrv.asd`**.

He reports the device successfully running SF2000 multicore after this model-specific application swap.

He also records the remapped physical-button behavior under the SF2000-derived software:

```text
Y -> Left
A -> Right
R -> A
B -> B
L -> X
H -> Y
```

This is direct runtime evidence supporting our model that the software family is shared while controller adaptation differs by product.

Source:
https://www.reddit.com/r/SBCGaming/comments/1bf6vzv/got_a_powerbank_handheld_time_to_play_around_with/

## DY12 lineage is more complicated than "same as SF2000"

Earlier community shorthand described DY12 as the same hardware/firmware as SF2000. Later owner testing refines that:

- DY12 can boot SF2000-derived firmware but may have dead controls or incorrect display;
- a user with a **DY12 MY2024** reports that the DY19 multicore BIOS works on that DY12 revision;
- another participant explicitly says DY12 is not completely identical to SF2000.

Therefore DY12 should be modeled as a **revision family**, not one immutable board.

### Working lineage hypothesis

```text
SF2000 / H1512 reference platform
        |
        +-- early DY12 revision(s)
        |      - SF2000-like
        |      - model-specific display/input adaptation
        |
        +-- DY12 MY2024
        |      - reported compatible with DY19 multicore bisrv
        |
        +-- DY19
               - six-button / power-bank product
               - model-specific bisrv
```

This suggests DY19 may have evolved from a later DY12 board/application branch rather than directly from stock SF2000.

## External wired-controller evidence

4PDA reverse-engineering notes state that controllers from X60 or DY12 can be used with SF2000 through connector adaptation, and that the USB-shaped controller connector is not standard USB HID.

This matters because it adds DY12 to the same non-USB wired-controller ecosystem already relevant to XGO's Handle Interface.

## Immediate recovery plan

Priority:

1. retrieve the Internet Archive DY19 image;
2. retrieve the MEGA DY19 stock firmware;
3. extract only firmware/resources/list metadata;
4. hash both distributions and determine whether they are the same stock revision;
5. compare their `bisrv.asd` against:
   - XGO A10;
   - DY19 multicore bisrv if recovered separately;
   - SF2000 1.71;
   - GB300;
   - DY19 13-menu;
6. specifically inspect:
   - controller scanner;
   - game-list writer/reader;
   - mapper UI;
   - display init;
   - battery/power paths.

## Confidence

**CONFIRMED EXTERNALLY:** a DY19 owner published a full SD-card partition dump to Internet Archive.

**CONFIRMED EXTERNALLY:** Handhelds Wiki exposes a separate stock firmware MEGA link.

**STRONG:** DY19 is an SF2000/H1512-family board variant with model-specific `bisrv.asd`.

**STRONG BUT REVISION-SPECIFIC:** DY12 MY2024 can use DY19 multicore BIOS according to owner testing.

**NOT YET VERIFIED:** whether the Internet Archive and MEGA stock images are byte-identical or represent different DY19 production revisions.
