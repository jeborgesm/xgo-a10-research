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

## 2023-06-22 — stock GBA execution path already under bnister investigation — CONFIRMED

Public SF2000 documentation records bnister's discovery that the stock gpSP emulator was not loading the bundled `gba_bios.bin` from the apparent top-level BIOS location. The actual stock paths included nested `mnt/sda1/bios/gba_bios.bin` locations under the GBA and user-ROM execution trees.

This predates multicore by almost three months and establishes that bnister/osaka was already tracing concrete behavior inside the stock GBA execution path well before that path became multicore's launch mechanism.

**Causal connection remains PARTIAL:** there is not yet surviving evidence that the BIOS-path investigation itself led directly to the later loader design. The chronology is nevertheless important because GBA was not an unexplored subsystem when multicore selected it.

Source: https://github.com/vonmillhausen/sf2000

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

## 2023-08-19 to 2023-08-29 — stock-core substitution appears as a separate experiment — CONFIRMED

The contemporaneous public documentation provides a much narrower window for the conceptual pivot than previously recognized. On **2023-08-19**, the custom-firmware status describes the HC-RTOS/RetroArch effort as individual cores built as complete firmware images, with no way to switch cores without replacing the firmware on the SD card. There is not yet any mention of modifying the stock firmware to host another emulator core.

By the **2023-08-29** documentation revision, a new sentence appears: **a side project was investigating modifying the stock firmware to replace or add additional emulator cores**. Crucially, the stated purpose at that point was exploratory—learning more about the device internals—and the documentation says there was not yet a plan to build custom firmware by this route.

This establishes that the stock-core substitution idea existed before the preserved September multicore repository and narrows its first publicly visible appearance to the ten-day interval **August 19–29, 2023**.

The distinction is historically important: two architectures were being explored in parallel by late August:

1. SDK/HC-RTOS replacement firmware containing a community-built RetroArch/core environment;
2. modification of the manufacturer's existing firmware to replace or add emulator cores.

Source: https://github.com/vonmillhausen/sf2000 (README revisions dated 2023-08-19 and 2023-08-29)

## 2023-08-30 — bnister is simultaneously probing cross-device stock-firmware portability — CONFIRMED

A contemporaneous 4PDA exchange adds a useful clue immediately after the August 29 public appearance of the stock-core-replacement side project. Asked whether an X60 could be given an SD card containing the SF2000 shell and emulators, bnister replied that the **reverse procedure was more interesting** to him because he preferred the X60 shell aesthetically. He then reported that an attempted test without an SF2000 physically available had failed: volunteers saw only a gear icon. He planned to revisit it after obtaining the unit and **soldering a debug output**, adding that the failure was unexpected.

This is not direct evidence for the multicore loader, but it is important context for the missing August/September phase. On August 30 bnister/osaka was not merely compiling RetroArch cores in the HC-RTOS environment; he was actively treating related stock firmware images as objects that might be transplanted, compared, instrumented and debugged across devices. That mindset is consistent with the family-level reverse-engineering program visible elsewhere in his work.

The timing is striking: this exchange is one day after public documentation first mentions the side project to modify stock firmware to replace/add emulator cores, and seventeen days before Osaka's preserved external-core loader. It strengthens the interpretation that late-August work had shifted back toward **stock-runtime experimentation and instrumentation**, even though it does not establish a causal link to the GBA interception.

Source: https://4pda.to/forum/index.php?showtopic=1067862&st=400


## 2023-09-03 — stock-core experiment persists; toolchain work becomes explicit — CONFIRMED

The September 3 documentation retains the stock-firmware core-replacement side project and adds that other efforts are focused on building an **efficient toolchain for further development**. Two days later bnister's CPU-clock discovery is documented; thirteen days later the surviving multicore repository begins with Osaka's native-loader work and a reproducible firmware-patching Makefile.

This does not prove that the September 3 toolchain effort was specifically the multicore toolchain, but it establishes that tooling work and stock-core experimentation were contemporaneous immediately before the external loader appeared.

Source: https://github.com/vonmillhausen/sf2000/commit/92384b220edf2d534254e8fe811e8157283c1819

## Late summer 2023 — architectural pivot toward the stock runtime — STRONG

Contemporaneous documentation explicitly describes multicore as a **new tack** after the HC-RTOS effort: rather than replacing the complete firmware, the developers modified the stock environment so they could retain the manufacturer's working audio/video drivers. The public description specifically says multicore **hijacks the stock Game Boy Advance emulator** to run additional cores and engines.

This establishes the practical reason for the pivot: the community had demonstrated arbitrary software/core execution with the SDK-based replacement environment, but the proprietary stock environment already solved difficult product-specific audio/video integration.

A useful working distinction is therefore:

1. **execution breakthrough:** HC-RTOS/RetroArch proved community code and cores could run on the platform;
2. **integration breakthrough:** stock-runtime archaeology revealed that the manufacturer's existing frontend could be repurposed to host external cores without recreating the complete device-support stack.

Source: https://github.com/vonmillhausen/sf2000 ; https://pt13762104.github.io/sf2000/faq/

## 2023-09-05 — bnister still actively mapping stock firmware immediately before multicore — CONFIRMED

The SF2000 documentation changelog records addition of `bnister`'s CPU clock-bump discovery on 2023-09-05. This is only eleven days before the preserved `osaka's initial code` commit.

The proximity matters: Osaka/bnister did not simply leave stock-firmware analysis behind during the HC-RTOS experiment. Stock `bisrv.asd` investigation was still producing concrete discoveries immediately before the external-core loader appeared.

Source: https://github.com/vonmillhausen/sf2000

## 2023-09-16 — Osaka's native-loader code is preserved — CONFIRMED

Commit `bdd02b0cd23e3005a6b3100278b445bf4dbcfd7c` in `madcock/sf2000_multicore`, titled `osaka's initial code`, is the **root commit** of the surviving Git history: it has no parent. It preserves the native symbol map, stock libretro callbacks/runtime globals, external-core jump table at `0x87000000`, CRC patcher, and LCD/GPIO UARTless-debug mechanism.

The source files carry `Copyright (C) 2023 Nikita Burnashev`. The community handle relationship `osaka (@bnister)` is independently preserved by later prerelease credits. Real-world identity correlation beyond those source/community records remains separate and should not be assumed.

### 2023-09-16, six minutes later — first surviving firmware-interception recipe — CONFIRMED

At 18:59:52Z, six minutes after the root commit, kobil committed the initial Makefile (`b9ace165a739a56e9240e7f01757c02303e12f2d`). It already contains the complete patching mechanism needed to enter the loader from stock firmware:

- link the external core at `0x87000000`;
- link the tiny loader at `0x800016d0`;
- inject `loader.bin` into `bisrv.asd` at file offset `0x16d0`;
- patch the stock call site at file offset `0x35a900` to `jal 0x800016d0`;
- patch watchdog and general-exception paths to loader-side debug handlers;
- recalculate the firmware CRC.

The original Makefile comment labels the patched call `jal run_nes`. That label should now be preserved as an **unresolved early identification**, not dismissed as merely stale documentation. By 2023-09-25 kobil explicitly states that the hook requires all routed files to have `.gba` appended, establishing that the mechanism was using the stock GBA-visible launch route by then. However, Osaka's 2023-09-16 root symbol map contains `run_emulator` but does **not** yet map `run_gba`; the explicit native `run_gba = 0x80359d1c` symbol is only added on 2023-10-31 when kobil implements fallback to the stock GBA emulator. Thus the surviving repository records an evolution in understanding/naming of the intercepted path. Whether the September 16 `run_nes` comment reflects an earlier NES experiment, an incorrect reverse-engineering label, or a call-site interpretation that was later refined remains **OPEN**.

This means the GBA/native-launch interception was **not invented by the later September 22 size-check commit**. The mechanism was already present at the beginning of the surviving repository history. Because the root commit is already labeled `osaka's initial code`, Git cannot presently establish whether Osaka identified the `0x35a900` call site, kobil identified it while packaging Osaka's code, or the two established it collaboratively before the first commit.

**Discovery attribution for the `0x35a900` interception therefore remains OPEN.** The missing evidence must predate the surviving repository history, making the Retro Handhelds development conversation and any reposts/notes from before September 16 the primary target.

Source: https://github.com/madcock/sf2000_multicore/commit/b9ace165a739a56e9240e7f01757c02303e12f2d

### Binary-level check of the `0x35a900` patch — CONFIRMED / OPEN attribution

The first patch writes little-endian bytes `B4 05 00 0C` at file offset `0x35a900`. Decoded as a MIPS `jal`, this replacement instruction targets `0x800016d0`, exactly the injected loader entry. This confirms that `0x35a900` is a **call instruction site**, not the address of the stock emulator function itself.

Later surviving multicore trees retain the same SF2000 patch site but relabel it explicitly as `jal run_gba`, while the September 16 Makefile called it `jal run_nes`. No surviving GitHub code search has produced an SF2000 `run_nes` symbol corresponding to the early comment. Conversely, the later linker map gives the stock GBA launcher as `run_gba = 0x80359d1c`.

The decisive missing datum is therefore the **four original stock bytes at file offset `0x35a900`** in the August 3 base `bisrv_08_03.asd`. Decoding those bytes will reveal the original JAL destination and let us test directly whether the stock call targeted `0x80359d1c` (`run_gba`) or another function. Until the pristine binary is recovered/inspected, the `run_nes` label remains an unresolved historical clue rather than evidence of a NES-based multicore prototype.


### 2023-09-17 — kobil generalizes Osaka's fixed core ABI — CONFIRMED

Within roughly nineteen hours, kobil replaced the initial hard-coded jump-table offsets at `0x87000000` with a single `__core_entry__()` function returning a structured table of libretro function pointers. The loader still reads the external image at `0x87000000`, but no longer needs a separate magic address for every exported core function. This is strong direct evidence for the later documented role split: Osaka supplied the low-level/native foundation while kobil rapidly developed generalized multicore internals.

Source: https://github.com/madcock/sf2000_multicore/commit/8874ebda98259a873971cfda1a9e8850e4c21e27

### 2023-09-21 — stock firmware ABI becomes an explicit interface — CONFIRMED

Commit `207a6f57e9cd89826927cbee6ad2b1f170626d58` extracts the native runtime declarations into `stockfw.h`. The interface includes `run_emulator`, stock video/audio/input/environment callbacks, save/load slots, `gfn_retro_*`, `g_retro_game_info`, `g_run_file_size`, `gp_buf_64m`, `RAMSIZE`, sound-task flags and native services. This is an important conceptual milestone: the proprietary firmware is being treated explicitly as a host ABI for the external core rather than merely as a binary to patch.

Source: https://github.com/madcock/sf2000_multicore/commit/207a6f57e9cd89826927cbee6ad2b1f170626d58

### Why the GBA hijack now matters — STRONG architecture clue

The September loader's mapped state includes `g_retro_game_info`, `g_run_file_size`, `gp_buf_64m`, `gfn_retro_*`, native frontend callbacks and `run_emulator()`, while the public multicore description says the modification hijacks the stock GBA emulator. Combined with bnister's June investigation of stock gpSP behavior, this narrows the missing archaeology question considerably: the likely breakthrough was not merely discovering an arbitrary executable address, but understanding enough of the stock GBA/frontend launch contract to substitute an external libretro-style core while retaining native services.

The exact discovery sequence remains **OPEN**. Do not promote the June BIOS-path bug to the cause of multicore without a surviving discussion, patch, disassembly note or commit establishing that connection.

Sources: https://github.com/madcock/sf2000_multicore/commit/bdd02b0cd23e3005a6b3100278b445bf4dbcfd7c ; https://github.com/vonmillhausen/sf2000

## 2023-09-23 — kobil public GitLab project created — CONFIRMED

GitLab reports `kobily/sf2000_multicore` was created on 2023-09-23, seven days after the preserved Osaka initial-code commit. Therefore the public GitLab repository is not the beginning of the multicore discovery process. A pre-GitLab development/exchange phase existed, with Retro Handhelds Discord the strongest surviving candidate for the missing connective record.

Source: https://gitlab.com/kobily/sf2000_multicore

## 2023-09-25 to 2023-09-27 — runtime switching and the original empty-stub protocol — CONFIRMED

On **2023-09-25**, commit `f471f68f8e364f6eaaf3302ad09f190cd5d3b893` introduces runtime core selection. At this stage selection is hard-coded for SNES and GBA and uses the ROM's extension while all intercepted files still carry a final `.gba` extension required by the stock launch path. The commit gives the concrete example `rom.sfc.gba` -> `/mnt/sda1/cores/snes/core_87000000`.

On **2023-09-27**, commit `ac5729163f2ad907d39b2265899eb6272c694a09` changes the convention to `[console];[rom filename].gba`. The commit explicitly records that these files **can be empty**: they exist so the stock UI will display/launch an apparent GBA item, while the loader parses the filename and opens the real ROM from `/mnt/sda1/ROMS/[console]/[filename]`.

This pins an important architectural progression after Osaka's initial loader: external-core execution existed first; generalized runtime selection and the user-facing stub protocol were added by kobil afterward. The stub was originally a filename-based dispatch command, not executable content and not a payload structure.

Sources: https://github.com/madcock/sf2000_multicore/commit/f471f68f8e364f6eaaf3302ad09f190cd5d3b893 ; https://github.com/madcock/sf2000_multicore/commit/ac5729163f2ad907d39b2265899eb6272c694a09

## 2024-09-14 — content-bearing stubs and the 251-byte discriminator appear later — CONFIRMED

Commit `a8b2970dab9580912aab1de1bad1eb6ef5669622`, titled **Improved stub format, improved save behavior**, adds a second dispatch path. If the legacy filename parser does not recognize the selected path, the loader opens the `.gba` file, reads its short contents, and parses that content as the core/ROM command. The associated README explains the resulting discriminator: files **up to 251 bytes are stubs; larger files are GBA ROMs**. Legacy filename stubs remain supported.

This resolves the earlier open question about the 251-byte threshold. It is **not part of the September 2023 multicore breakthrough** and should not be used to infer how Osaka/kobil first discovered the GBA interception. It belongs to a later improved stub format, roughly a year after the original empty filename-based stubs.

Source: https://github.com/Trademarked69/dy19_multicore/commit/a8b2970dab9580912aab1de1bad1eb6ef5669622


## 2023-10-31 — stock GBA fallback finally names `run_gba` explicitly — CONFIRMED

Commit `be91f03ced4d717e14b09771fbed5b91f0e2b3d5` adds the ability to launch the original stock GBA emulator when a selected filename is not recognized as a multicore stub. To do this, kobil adds the native symbol `run_gba = 0x80359d1c` and calls it directly on parser failure.

This is a small implementation change but an important archaeology marker. Osaka's September 16 symbol map already knew `run_emulator` and the frontend/global contract, but did not expose `run_gba`. The first Makefile six minutes later described the patched `0x35a900` call as `run_nes`; by September 25 the hook was definitely being presented through `.gba` filenames; and on October 31 the native GBA launcher itself is explicitly named and preserved. The evidence therefore supports an **evolving reverse-engineering model of the launch path**, rather than retroactively assuming every early label had the later meaning.

Source: https://github.com/madcock/sf2000_multicore/commit/be91f03ced4d717e14b09771fbed5b91f0e2b3d5


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

The especially important transition to investigate is **July-September 2023**. In July the community had a barely functional replacement RetroArch environment built on the incomplete HC-RTOS SDK. By September 16 Osaka had instead mapped enough of the stock runtime to expose its existing libretro-like frontend and load an external core at `0x87000000`; the first surviving Makefile already patches the stock launch path into that loader. Recovering the discussion/experiments behind that pre-Git transition may explain exactly who recognized the interception point and why the GBA path was chosen.

The GBA evidence makes the target more specific: bnister had already traced stock gpSP filesystem behavior in June; multicore later hijacked the stock GBA execution path; and Osaka's initial loader exposes the surrounding native frontend/runtime contract. This is a **strong chronological/architectural convergence**, but the causal bridge remains unproven pending recovery of the missing development conversation.

## Immediate archaeology targets

1. Recover Retro Handhelds Discord material between the July 20 gpSP true-CFW milestone and Osaka's September 16 native-loader code.
2. Search specifically for pre-September-16 references to `0x35a900`, `0x800016d0`, `run_gba`, `run_nes`, `0x87000000`, Osaka/bnister and kobil/kobily.
3. Determine who first identified the stock launch call site and whether the original `run_nes` Makefile comment reflects an earlier experiment, a simple labeling error, or a change in interception target.
4. Determine when the developers realized the stock GBA path exposed a reusable libretro-style frontend contract.
5. Trace the source of the native symbol addresses in Osaka's initial map: disassembly, SDK symbols, map files, runtime experiments, or a combination.
6. Search the HC-RTOS tree/history for code or notes that bridge the SDK-based experiment to the later stock-runtime loader.
7. Trace the original SDK dump provenance and compare its symbol/API vocabulary with Osaka's `stockfw` map.
8. Recover the earliest kobil GitLab commits after September 23 and distinguish Osaka's supplied loader foundation from kobil's generalized multicore internals.
9. Search for early references to stub files, the GBA-size discriminator, `gp_buf_64m`, `g_run_file_size`, and `run_emulator()` that may preserve the first description of the hijack mechanism.

Research timeline created 2026-09-17.