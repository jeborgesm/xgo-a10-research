# Arcade Test16 hardware result — unchanged black-screen freeze

Date: 2026-09-08
Branch: `research-game-list-arcade-expansion`

Status: **HARDWARE FAIL — runtime-list spoof ruled out**

## Hardware result

Test16 temporarily spoofed ACTIVE_LIST_ID from 11 to 7 only while the external MAME2000 core executed.

Observed for both Pac-Man and Ms. Pac-Man:

```text
select game
 -> Loading.....
 -> black screen
 -> device frozen/unresponsive
```

No pause menu, no volume OSD, no recovery path.

This is indistinguishable from Test15.

## Conclusion

The dormant list-ID-11 runtime identity is not the blocker.

Close:
- list-ID-11 lower runtime policy hypothesis: **ruled out**.

The failure occurs after the stock loading screen and before any usable external-core video/input/UI service returns.

## Next diagnostic

Instrument the external-core loader boundary with persistent SD-card stage markers. The marker must be fs-synced after each checkpoint so that a hard power-cycle after the freeze reveals the last completed stage.

Checkpoints should include:
1. loader entered;
2. XGOC header opened/read/validated;
3. stock sound task stopped;
4. RAMSIZE ceiling moved;
5. full core payload read;
6. payload CRC passed;
7. zero/BSS completed;
8. IRQ-GP repair completed;
9. cache flush completed;
10. immediately before external entry call;
11. first instruction / first C entry inside core frontend;
12. after runtime init;
13. before retro_init;
14. after retro_init;
15. immediately before stock run_emulator;
16. after stock run_emulator returns.

Do not change emulator behavior while collecting this trace.
