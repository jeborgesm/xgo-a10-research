# Hardware Test 05 result and Test 06 ZFB content-path correction

Status: **TEST 05 HARDWARE FAILED DURING CPS1 LOAD; TEST 06 READY**

## Test 05 hardware result

Physical XGO observations:

- CPS2 works normally, proving the list-ID guard preserves non-CPS1 arcade;
- CPS1 reaches the game RAM/self-test screen;
- SFII and other CPS1 titles then hang during startup;
- Start+Select does not recover the session once hung;
- unlike the stock arcade path, the visible lower-screen file-loading phase is absent.

This is the first hardware evidence that the corrected runtime hook actually enters external CPS1 rather than stock FBA.

## Content-path root cause

XGO arcade browser entries are not the real ROM ZIPs.

The preserved card inventory shows:

```text
D:\ARCADE\Street Fighter II- The World Warrior.zfb   59,917 bytes
D:\ARCADE\bin\sf2.zip                              8,903,809 bytes
```

The SF2000/XGO-family ZFB structure is:

```text
offset 0       59,904-byte RGB565 thumbnail
offset 59904   four zero bytes
offset 59908   real ZIP basename, NUL-terminated
               e.g. sf2.zip
trailer        second NUL
```

The XGO sizes independently confirm this geometry:

```text
59904 + 4 + len("sf2.zip") + 2 = 59917
```

Stock `run_game()` preloads the selected ZFB wrapper into `ROM_BUFFER`.
The previous external CPS1 frontend incorrectly passed the menu-facing ZFB
path to FBA2012, which is a full-path arcade core that identifies the driver
from the actual ZIP basename.

## Test 06 correction

The external CPS1 frontend now:

1. reads the already-preloaded ZFB from `ROM_BUFFER`;
2. verifies the four-zero separator at offset 59904;
3. extracts the basename beginning at offset 59908;
4. rejects separators/path traversal;
5. constructs:
   `/mnt/sda1/ARCADE/bin/<embedded-name>`;
6. passes that real ZIP path as `retro_game_info.path`;
7. passes no fake ZFB data buffer to the core.

Example:

```text
Street Fighter II- The World Warrior.zfb
 -> embedded sf2.zip
 -> /mnt/sda1/ARCADE/bin/sf2.zip
 -> FBA2012 CPS1 driver sf2
```

## Regression boundary

Test 06 changes only the CPS1 external `core.xgc` relative to Test 05.

Unchanged:

- mapper v19;
- `gpapi.bvs`;
- external Snes9x2005;
- NES path;
- CPS1 list-ID gate;
- corrected arcade runtime hook at `0x80360df8`;
- stock arcade cleanup at `0x80360e00`;
- CPS2/IGS/Neo Geo stock fallback;
- firmware image.

## Test 06 identity

```text
xgo-core3-cps1-test06-zfbfix-v19-snes.zip
SHA-256
9f8e52a4ea61e93dc2ddbf0e34da0689eb6209331d9cd7a830aca24bbc99855b

firmware
16233cbb0d7b7e5a90d72a0eed04b873a3754bcdbaaedcea64fc1b3b972e3f1f

CPS1 core.xgc
d74498db446b021a263f9fc927461af7b6abeb01f8b31cdb05a88328dc469580
```

## Hardware gate

1. CPS2 still launches/quits normally.
2. SFII progresses beyond self-test into gameplay.
3. Compare actual external-core SFII frame pacing against stock.
4. Start+Select enters pause UI.
5. QUIT returns cleanly.
6. Relaunch SFII.
7. Mapper and SNES remain functional.
