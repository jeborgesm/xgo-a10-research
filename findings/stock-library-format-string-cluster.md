# Stock frontend library/path format-string cluster

Status: **STATIC FIRMWARE EVIDENCE; CALLER TRACE PENDING**

A direct string scan of the stock `bios/bisrv.asd` found a tightly packed frontend-related string cluster near ASD file offset `0x9a341a`–`0x9a354d`.

Relevant strings occur together in this order:

```text
%s/save/%s.kmp
%s/save/%s.sa%d
%s/%s/save/%s.sa%d
/mnt/sda1/UpdateFirmware/Firmware.upk
%s/Resources/Foldername.ini
%s\n%d\n%x\n...          [large formatted configuration record]
SF2000
%d. %s
%s/%s/%s
LOADING......
%s/Resources/Test.zsf
SearchKey: %s \n
%s/bin/%s
Loading %s        
```

## Why this matters

The generic `%s/%s/%s` pathname formatter occurs immediately adjacent to visible-list-like formatting (`%d. %s`), a search-key diagnostic, and the loading UI strings. This is consistent with a filesystem-driven frontend that constructs paths from root/system/filename components rather than relying exclusively on a single hard-coded master game database.

This is **not yet proof** that dropping a wrapped ROM into `FC/`, `SFC/`, etc. automatically adds it to the stock list. Caller analysis is required.

The only wrapped-ROM extension found directly in this local string cluster is `.zsf`, via `%s/Resources/Test.zsf`. The absence of literal `.zfc`, `.zmd`, and `.zgb` strings from the stock ASD means extension filtering may be table-driven, encoded differently, derived from system metadata, or not performed by simple literal string comparison.

## SD-card inventory evidence

The recovered card inventory contains large ordinary per-system collections, including approximately:

- 765 `.zfc` paths (including non-library/resource occurrences)
- 1,067 `.zsf` paths (including `Resources/Test.zsf`)
- 833 `.zmd` paths
- no `.kmp` files in the captured inventory

The lack of `.kmp` files is useful: keymaps appear to be optional/per-game generated state rather than required static metadata for every listed game.

## Next reverse-engineering targets

1. Find code references to `%s/%s/%s`, `%d. %s`, and `SearchKey: %s` and recover the surrounding list/search routine.
2. Trace its filesystem calls to `fs_opendir` / `fs_readdir` and identify filtering/sorting behavior.
3. Determine where system directory names and accepted wrapper formats are sourced.
4. Trace `%s/save/%s.kmp` separately to establish exact keymap record size and load/save lifecycle.
5. Once the list construction is understood, design the smallest hardware test: add one known wrapped ROM under a controlled new filename and observe whether it appears without firmware modification.

Do not promote the auto-enumeration hypothesis to fact until caller analysis or hardware confirms it.
