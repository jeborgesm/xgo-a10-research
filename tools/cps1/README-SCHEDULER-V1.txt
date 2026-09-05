XGO CPS1 STOCK SCHEDULER V1 — HARDWARE TEST CANDIDATE
=====================================================

PURPOSE

This candidate does NOT replace the CPS1 emulator.

It keeps:
- mapper v19
- stock XGO FBA
- stock C68K
- stock 22.05-kHz FBA audio
- stock input/video/audio callbacks
- stock private FBA render-skip hook
- stock menu/save/keymap logic

It changes only the XGO frame-pacing / catch-up policy.

The replacement policy is derived from the stock SF2000 08/03, SF2000 1.71,
and GB300 v2 wall-time scheduler:

    elapsed = now - start_tick
    ideal_frame = elapsed * fps / 1000

When behind, it permits up to three catch-up frames. Catch-up frames use the
existing XGO/FBA private frameskip hook, which disables CPS drawing while
continuing emulation and audio.

When early, it sleeps 1 ms and re-evaluates against absolute wall time.

INPUT REQUIREMENT

The patcher accepts ONLY the exact hardware-confirmed mapper-v19 firmware:

    SHA-256
    466b336ee601f16314b73fbc66f0135a7090942157fce77c749391fbaa4189ab

If your current bisrv.asd has a different hash, STOP. Do not replace it with an
older firmware just to make this test work. Report the hash instead so the same
scheduler overlay can be composed onto that protected baseline.

HOW TO BUILD THE CANDIDATE

1. Make a backup of your current test card.
2. Copy the current mapper-v19:
       bios\bisrv.asd
   to your PC.
3. Drag bisrv.asd onto:
       PATCH-SCHEDULER-V1.cmd
4. The script creates:
       bisrv.scheduler-v1.asd
   next to your input file.
5. The original input is never modified.

HOW TO TEST

On a disposable/test card whose Resources already match mapper v19:

1. Back up bios\bisrv.asd.
2. Copy bisrv.scheduler-v1.asd to:
       bios\bisrv.asd
3. Do not replace Resources, ROMs, KMP files, or any other folder for this test.
4. Boot normally.
5. First verify:
   - normal XGO menu
   - Mapper still opens and works
   - a known NES/SNES game still behaves normally under the firmware baseline
   - normal return to menu
6. Then test the same CPS1 titles used for the stock baseline, especially:
   - Street Fighter II
   - Cadillacs and Dinosaurs

WHAT TO WATCH FOR

Success would look like:
- same game compatibility
- same controls
- same audio character
- same normal baseline speed
- fewer / shorter prolonged slow-motion episodes
- short render-drop bursts when the system falls behind
- faster recovery to normal cadence after a transient slowdown

Failure / regression includes:
- Loading freeze
- black screen
- broken pause/menu
- mapper failure
- audio instability not present in stock
- new ROM compatibility failures
- inability to return to the menu

ROLLBACK

Restore your backed-up mapper-v19 bios\bisrv.asd.

This patch does not touch SPI NOR and does not use Firmware.upk.

RESEARCH BASIS

The patch surface and fixed-address helper have passed assembler-level static
fit proof on the XGO firmware layout:
- main helper: 0x8035eee8..0x8035ef67 (0x80 bytes)
- early wait:  0x8035f070..0x8035f07f (0x10 bytes)
- existing XGO gfn_frameskip / retro_run path remains untouched

Authoritative project state:
HANDOFF-CURRENT.md on branch research-post-mapper-runtime
