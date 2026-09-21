# Test106 initial hardware result — compatibility recovery path

Status: PARTIAL HW PASS. Marker filesystem confirmation still pending.

Starting card state:
- LIVE MD catalog healthy at 839 generation.
- complete stale 788 Test105 recovery triplet still present.
- no .xgo-cat-state marker.
- Test106 hardware candidate installed.

Observed:
1. device booted;
2. Refresh invoked exactly once;
3. UI reported "Games Updated";
4. device remained usable;
5. user entered one of the newer Mega Drive games immediately;
6. game launched and functioned as expected;
7. artwork/images remained present.

HW conclusions:
- corrected Test106 Stage1 boots;
- missing-marker compatibility path does not prevent successful recovery/rebuild;
- Test106 Stage2 integration returns successfully;
- post-run LIVE catalog is consumable immediately by frontend;
- artwork association remains healthy;
- game launch/gameplay remains healthy.

Still OPEN until filesystem capture:
- whether .xgo-cat-state was created;
- whether its exact contents are CLEAN!;
- whether stale 788 backup triplet remains;
- exact final LIVE catalog hashes/counts.

Do not run a second Refresh yet. The next evidence should be a passive SD capture of MD/art and the three MD Resources catalog files. If CLEAN! is present, the second Refresh becomes the decisive proof that stale backup files are logically ignored.
