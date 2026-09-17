# SF2000 reverse-engineering development timeline

Status: active chronology companion to `sf2000-community-development-archaeology.md`

Purpose: preserve dated evidence for how SF2000 knowledge progressed from stock-firmware archaeology through true-CFW experiments, multicore, and later HCSEMI-family ports. This file separates dated observations from broader architectural interpretation.

Evidence levels: **CONFIRMED** = directly preserved contemporaneous source/repository evidence; **STRONG** = multiple surviving sources; **PARTIAL** = useful clue requiring corroboration.

## 2023-04-24 — bnister already identifies the platform family — CONFIRMED

A contemporaneous 4PDA post by `bnister` says that the lower-end ALi processors had neither a Linux kernel nor leaked SDK available at that time, so only stock-firmware modification appeared practical. More importantly, bnister identifies the SF2000 processor as the same general processor used in the **Y2 SG/SFC with LFSE2022 board**, differing in the product path by LCD output rather than HDMI and referring to the B-line rather than A-line. The post also notes use of the platform in inexpensive video-card/postcard-like products.

This is important because it demonstrates family-level hardware recognition by bnister/osaka months before multicore. The later loader work did not begin with an unknown CPU in September 2023; there was already active platform identification and stock-firmware archaeology in April.

Source: https://4pda.to/forum/index.php?showtopic=1067862

## 2023-05 through 2023-06 — rapid stock-firmware archaeology — CONFIRMED

Surviving SF2000 documentation records a dense sequence of bnister discoveries and collaborations:

- hints identifying `Archive.sys` behavior;
- `.kmp` per-ROM key mappings and stock mapping locations in `bisrv.asd`, extended by `notv37` mapping individual button bits;
- firmware follow-up on the menu-audio sample-rate behavior initially analyzed mathematically by `notv37`;
- root cause and permanent patch for the bootloader/FAT-directory-entry bug;
- discovery of the GBA BIOS path bug and the paths stock gpSP actually searches;
- identification of the SNES first-launch slowdown as initialization-order behavior involving audio/clock settings after RetroArch initialization;
- collaboration with `dteyn` locating battery-calibration values and producing corrected calibration values.

By June 2023, public documentation also records discovery of an SDK for the SF2000 CPU/platform. This changes the development assumption visible in bnister's April 24 post: a true replacement firmware had become technically conceivable.

Sources: https://github.com/vonmillhausen/sf2000 ; https://dteyn.github.io/sf2000/ ; https://dteyn.github.io/sf2000_projects.htm

## 2023-06 to 2023-07 — hcRTOS / true-CFW experiment — CONFIRMED

The recovered HC-RTOS project describes itself as HiChip Semiconductor's HC-FreeRTOS SDK platform modified for the SF2000 / HCSEMI B210 and identifies the project roles as:

- Ignatz: maintainer / main custom-firmware developer;
- Osaka: researcher of original firmware, author of the bootloader fix and sample custom BMP-viewer code;
- xTxNinjaZx / Kev: firmware researcher/tester and custom-firmware support.

The repository points to an original SDK dump and firmware files, confirming that the SDK discovery became an actual development basis rather than merely a documentation lead.

Contemporaneous SF2000 documentation gives a useful progress sequence:

- 2023-06-26: discovered SDK documented;
- 2023-07-09: initial RetroArch build;
- 2023-07-12: RetroArch video driver displays the main menu;
- 2023-07-14: basic input driver functional;
- 2023-07-18: first running RetroArch core;
- 2023-07-20: second core, gpSP, at an early running stage; audio existed but was stuttery/crackly.

The true-CFW effort later stalled because the SDK was incomplete/low-quality: important video/audio support had to be developed, builds were unstable, crashes lacked useful diagnostics, and experimental builds often had performance/thermal problems. This context is critical: multicore emerged after a genuine attempt at replacing the firmware, not because nobody tried.

Sources: https://github.com/Data-Frog-Central/HC-RTOS ; https://github.com/vonmillhausen/sf2000

## 2023-09-16 — Osaka's native-loader code is preserved — CONFIRMED

Commit `bdd02b0cd23e3005a6b3100278b445bf4dbcfd7c` in `madcock/sf2000_multicore`, titled `osaka's initial code`, preserves the native symbol map, stock libretro callbacks/runtime globals, external-core jump table at `0x87000000`, CRC patcher, and LCD/GPIO UARTless-debug mechanism.

The source files carry `Copyright (C) 2023 Nikita Burnashev`. The community handle relationship `osaka (@bnister)` is independently preserved by later prerelease credits. Real-world identity correlation beyond those source/community records remains separate and should not be assumed.

Source: https://github.com/madcock/sf2000_multicore/commit/bdd02b0cd23e3005a6b3100278b445bf4dbcfd7c

## 2023-09-23 — kobil public GitLab project created — CONFIRMED

GitLab reports `kobily/sf2000_multicore` was created on 2023-09-23, seven days after the preserved Osaka initial-code commit. Therefore the public GitLab repository is not the beginning of the multicore discovery process. A pre-GitLab development/exchange phase existed, with Retro Handhelds Discord the strongest surviving candidate for the missing connective record.

Source: https://gitlab.com/kobily/sf2000_multicore

## 2023-10 to 2023-11 — multicore becomes a distinct stock-firmware modification path — CONFIRMED

By October, public SF2000 documentation explicitly distinguishes the hcRTOS true-CFW effort from the multicore experiment. The latter modifies/exploits the stock firmware environment rather than replacing it wholesale.

A November 2023 prerelease preserves the role split:

- `@osaka (@bnister)` — research and low-level developer;
- `@kobil (@kobily)` — multicore developer, internals;
- `@adcockm` — multicore developer, cores.

November commit history then records Osaka contributions involving cache flushing, MAME2000 linker/load layout, tearing, save-state image buffers, misaligned accesses and `clock()`, plus joint kobil/Osaka fixes. These are runtime-boundary problems rather than simple emulator-core compilation.

Sources: https://github.com/madcock/sf2000_multicore ; https://www.reddit.com/r/DataFrog/comments/17cj3zo/

## 2024-03-23 — `$gp` / dynarec / stock IRQ boundary documented — CONFIRMED

Commit `7998e068b6ade53a2f9dd56c4a08d63b7eeaa88b`, explicitly synchronized from kobil's GitLab work, documents gpSP dynarec-generated code modifying `$gp` while stock IRQ handlers require the original stock-startup `$gp`. The solution restores stock `$gp` before `irq_handler`.

This is direct evidence of multiple execution domains sharing the machine: stock firmware context, multicore/core context, and dynamically generated core code, with ABI/register ownership becoming significant at crossings back into stock services.

Source: https://github.com/madcock/sf2000_multicore/commit/7998e068b6ade53a2f9dd56c4a08d63b7eeaa88b

## 2024-04-27 onward — GB300 propagation — CONFIRMED

Independent GB300 documentation states that Osaka (`bnister`) and Prosty (`_prosty`) brought multicore to GB300 v1 on 2024-04-27. A 2024-04-28 community announcement specifically credits Osaka with determining the patches necessary to make the SF2000 multicore modification work on GB300.

On 2024-05-05, bnister also ported the GB300 stock firmware to run on SF2000, showing bidirectional experimentation rather than only one-way core reuse.

Later GB300 v2 work credits Osaka, Prosty, Karl Ellis and Mutandone alongside the original SF2000 multicore developers. July 2024 tooling incorporated a newer Osaka VTxx firmware patch that replaced earlier VT02/VT03 workarounds.

Sources: https://github.com/nummacway/gb300 ; https://github.com/tzubertowski/gb300_multicore ; https://www.reddit.com/r/SBCGaming/comments/1cfin56/ ; https://github.com/nummacway/gb300-sf2000-tool

## Historical interpretation — STRONG

The chronology now supports a continuous development story:

**stock firmware archaeology and family identification (spring 2023) -> SDK discovery and true-CFW/RetroArch experiments (summer 2023) -> pivot toward reusing the stock frontend/native runtime (late summer/September 2023) -> generalized multicore internals (kobil) and core integration (adcockm) -> runtime hardening and debugging -> propagation to GB300/DY19 and related HCSEMI devices.**

The especially important transition to investigate is **July-September 2023**. In July the community had a barely functional replacement RetroArch environment built on the incomplete HC-RTOS SDK. By September 16 Osaka had instead mapped enough of the stock runtime to expose its existing libretro-like frontend and load an external core at `0x87000000`. Recovering the discussion/experiments behind that pivot may explain exactly why multicore took its final architecture.

## Immediate archaeology targets

1. Recover Retro Handhelds Discord material between the July 20 gpSP true-CFW milestone and Osaka's September 16 native-loader code.
2. Determine when the developers realized the stock firmware already exposed a reusable libretro-style frontend contract.
3. Trace the source of the native symbol addresses in Osaka's initial map: disassembly, SDK symbols, map files, runtime experiments, or a combination.
4. Search the HC-RTOS tree/history for code or notes that bridge the SDK-based experiment to the later stock-runtime loader.
5. Trace the original SDK dump provenance and compare its symbol/API vocabulary with Osaka's `stockfw` map.
6. Recover the earliest kobil GitLab commits after September 23 and distinguish Osaka's supplied loader foundation from kobil's generalized multicore internals.

Research timeline created 2026-09-17.