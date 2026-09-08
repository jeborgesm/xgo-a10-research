# Arcade Test18 hardware result — FAT trace instrumentation invalid

Date: 2026-09-08
Branch: `research-game-list-arcade-expansion`

Status: **DIAGNOSTIC INVALID — filesystem trace method retired**

## Hardware / filesystem result

Test18 created a visible one-byte FAT directory entry:

`MAME17-L.txt`

but Windows could not open it:

```text
type D:\MAME17-L.txt
The file or directory is corrupted and unreadable.
```

`dir /x D:\` also reports repeated `The parameter is incorrect.` around multiple XGO-created trace entries and shows corrupted date/time metadata.

Therefore the trace byte itself cannot be trusted.

## What remains valid

The existence of the directory entry proves the loader executed far enough to attempt the trace write.

However, firmware-side `fopen/fwrite/fclose` tracing from this unusual loader context can leave malformed FAT metadata and changes runtime behavior:
- Test15/16: Loading -> black screen -> freeze;
- Test17: freeze on Loading;
- Test18: corrupt trace entry.

Filesystem tracing is therefore perturbing the system and is retired for this investigation.

## Safety decision

Do not use SD-card filesystem writes for further loader/core checkpoints.

Do not run CHKDSK before preserving/copying the readable SD-card contents or making a sector image, because repair may delete diagnostic entries or other damaged metadata.

## Next diagnostic

Test19 uses only the already-proven stock OEM text renderer to display checkpoint letters on the LCD:

- C = immediately before stock sound-task shutdown;
- D = immediately after sound-task shutdown returns;
- J = immediately before external MAME2000 entry.

No filesystem writes and no external-core instrumentation.
