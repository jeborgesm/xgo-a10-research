# Arcade Test17 hardware result — no core-entry checkpoint

Date: 2026-09-08
Branch: `research-game-list-arcade-expansion`

Status: **HARDWARE FAIL — failure proven before external MAME C entry**

## Hardware result

Both Pac-Man and Ms. Pac-Man under Test17 now freeze on the stock:

```text
Loading.....
```

screen.

No `MAME17-11.txt` through `MAME17-17.txt` files are created on the SD-card root.

## Conclusion

The external MAME2000 C frontend is never reached.

Therefore the failure is earlier than:
- newlib/runtime initialization inside the external core;
- ROM-path construction;
- retro_init;
- stock run_emulator;
- MAME driver execution.

The active failure domain is now the pre-entry loader/handoff sequence.

Most important remaining pre-entry stages:

1. loader entered;
2. XGOC opened/read/validated;
3. stock sound task stop;
4. RAMSIZE ceiling move;
5. XGOC payload copy;
6. payload CRC;
7. BSS/zero;
8. IRQ-GP repair;
9. cache flush;
10. external entry jump.

Test17 itself also changes the symptom from post-Loading black screen to a hang on Loading, so the core-side persistent filesystem tracing may perturb timing/state. Do not infer a new emulator failure from that presentation change.

## Next diagnostic

Use a minimal loader-only persistent trace. Avoid filesystem calls from the external core entirely.

Prefer one compact fixed stage byte/file updated only from the loader, or a single preallocated trace object, so the loader remains within the verified cave and does not materially change the external core.

The next test must identify whether the hang is:
- before/inside sound-task shutdown;
- during core load/CRC;
- during IRQ/cache preparation;
- at the jump into 0x87000000.
