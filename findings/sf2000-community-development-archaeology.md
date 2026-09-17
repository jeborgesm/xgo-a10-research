# SF2000 community development archaeology

Status: active research log

Purpose: reconstruct how SF2000 reverse-engineering knowledge developed and propagated through developer conversations, experiments, repositories, and later HCSEMI-family ports. This is specifically intended to distinguish original discoveries from later integration/implementation and to identify knowledge that can inform XGO A10 work.

## Evidence discipline

- CONFIRMED: directly preserved in source, commit history, release notes, or contemporaneous documentation.
- STRONG: multiple independent surviving sources agree, but original conversation may be unavailable.
- PARTIAL: useful attribution/lineage clue requiring more evidence.
- Do not assume the final committer originated a technique when release notes or commits attribute it to another developer.

## Early stock-firmware reverse engineering

### bnister / notv37 key mapping chain — CONFIRMED

Surviving SF2000 documentation records that `bnister` discovered per-ROM `.kmp` key bindings and the locations of default emulator mappings in `bisrv.asd`. `notv37` then mapped the individual button bits. Their combined findings became button-mapping tooling.

This is a useful example of the community knowledge pipeline: firmware observation -> shared reverse-engineering information -> second developer extends it -> tooling/documentation.

The same documentation attributes initial menu-audio sample-rate math to `notv37`, followed by firmware-level technical follow-up by `bnister`, with the deeper discussion originally linked into Retro Handhelds Discord.

Other contemporaneous documentation credits `taizou` with identifying previously unknown stock Resources files and `adcockm` with detailed arcade-emulation metadata.

### Osaka and bnister are the same Retro Handhelds developer identity — CONFIRMED

A contemporaneous November 2023 SF2000 multicore prerelease post preserves the developer credits as **`@osaka (@bnister) research and low-level developer`**, alongside `@kobil (@kobily) multicore developer (internals)` and `@adcockm multicore developer (cores)`. Later GB300 documentation independently states that Discord user **osaka (`bnister`)** and Prosty (`_prosty`) brought multicore to GB300 v1.

This closes an important attribution gap: the earlier stock-firmware discoveries credited to `bnister` and the later low-level multicore work credited to `osaka` belong to the same community developer identity. Therefore the development history is more continuous than the handles initially suggested: the person who discovered stock `.kmp`/mapping behavior was also the low-level researcher behind the initial multicore/native-loader work.

This does **not** by itself prove that every external historical record for the real name appearing in source headers belongs to the same person; handle identity and real-world identity remain separate provenance questions.

## Multicore lineage

### Repository ancestry — CONFIRMED

The surviving `madcock/sf2000_multicore` README states that it mirrors/follows `kobil`'s original GitLab multicore repository and directs readers to the Retro Handhelds Discord development channel for the latest information. Later GB300 multicore material preserves the same ancestry. The surviving DY19 multicore repository explicitly says its DY19 work was originally made by Osaka and later updated from the SF2000 multicore lineage.

The original GitLab project remains publicly indexed at `gitlab.com/kobily/sf2000_multicore`. GitLab reports that the project was created on **2023-09-23**. This is historically significant because Osaka's preserved initial-code commit in madcock's GitHub history is dated **2023-09-16**, one week earlier. Therefore the surviving Osaka code predates the creation date of kobil's public GitLab project. The pre-2023-09-23 discovery/exchange path cannot be reconstructed by treating the GitLab project as the beginning of multicore development.

Working lineage:

stock SF2000 reverse engineering by bnister/osaka and other community researchers -> Discord experimentation and native-loader work -> kobil multicore GitLab -> madcock/adcockm integration/release mirror -> GB300 and other family adaptation

with Osaka contributing important low-level platform work and later explicit GB300 and DY19 adaptations.

## Osaka initial multicore code — CONFIRMED, high importance

GitHub commit `bdd02b0cd23e3005a6b3100278b445bf4dbcfd7c` in `madcock/sf2000_multicore`, dated 2023-09-16, is explicitly titled `osaka's initial code`.

This is much more important than a generic code contribution. The preserved diff already contains a substantial stock-firmware ABI/symbol map, including:

- stock libc addresses (`malloc`, `free`, `memcpy`, stdio/file APIs, etc.);
- TDS2 services such as `osal_tds2_cache_flush`, `os_disable_interrupt`, and `dly_tsk`;
- native libretro frontend callbacks: `retro_video_refresh_cb`, `retro_audio_sample_batch_cb`, `retro_input_poll_cb`, `retro_input_state_cb`, `retro_set_environment_cb`;
- native `run_emulator`;
- runtime globals including `RAMSIZE`, `g_snd_task_flags`, `g_retro_game_info`, `g_run_file_size`, `gp_buf_64m`, state-load/state-save function pointers, and `gfn_retro_*` slots;
- direct HiChip GPIO/pinmux addresses used for LCD-based UARTless debugging.

The same initial contribution defines the external core jump table at **0x87000000**, with entry points for `retro_init`, `retro_deinit`, AV info, `retro_run`, `retro_load_game`, region, environment, video, audio and input callbacks, followed by BSS clearing code.

This establishes that by 2023-09-16 Osaka already had the essential external-core/native-frontend contract that later became recognizable as SF2000 multicore. For XGO archaeology this is especially important because our CLASSIC work independently encountered the same family-style concepts: external image at 0x87000000, native callback slots/services, `gp_buf_64m`, `g_retro_game_info`, `g_run_file_size`, and `run_emulator()`.

The commit also contains an on-device LCD debugging implementation using the stock hardware GPIO path, demonstrating that the developers were actively creating instrumentation for a platform without conventional UART output.

### Osaka identity/provenance clue — CONFIRMED source attribution; real-world correlation remains PARTIAL

Several files inherited from Osaka's initial contribution (`crc.c`, `debug.c`, `main.c`, and `video_sf2000.c`) carry the explicit source header **`Copyright (C) 2023 Nikita Burnashev`**. Combined with the independent `osaka (@bnister)` attribution, the source tree now gives us two strong archival handles for the same SF2000 development stream: Osaka/bnister and the source-header name.

External web traces exist for a programmer named Nikita Burnashev in older low-level/software-development contexts, including a Game Boy Advance programming credit and compression/tooling work. These are **not yet sufficient to assert that every historical Nikita Burnashev record is the same person as SF2000 Osaka/bnister**. Preserve that distinction until independently corroborated.

## Osaka follow-on discoveries preserved in commit history — CONFIRMED

The repository's commit messages preserve a sequence of work that likely originated in Discord/experimental exchanges before being integrated:

- 2023-11-01: Osaka implementation for cache flushing a specific address range.
- 2023-11-06: reverted to full cache flush because range-specific flushing was not stable; commit explicitly thanks Osaka.
- 2023-11-08: Osaka workaround for a MAME2000 linker problem; `--build-id` was required to obtain the desired `.text` LMA/VMA behavior.
- 2023-11-08: Osaka tearing fix added as a build option.
- 2023-11-18/19: Osaka patches increasing the buffer used for save-state thumbnail images, intended to support displays up to 640x480x2.
- 2023-11-20: Caprice32 patches include Osaka's misaligned-access fix.
- 2023-11-20: joint kobil + Osaka fixes for fake-08 and Caprice32.
- 2023-11-21: `clock()` fix attributed to Osaka.

This shows Osaka was not merely porting individual cores. His work repeatedly addressed the native/runtime boundary: cache coherency, linker/load layout, display synchronization, save-state frontend buffers, alignment faults and platform timing.

## kobil follow-on work preserved in commit history — CONFIRMED

Preserved commits attribute to kobil:

- working VICE x64 build;
- changes reaching Wolf3D initial loading screens;
- repeated upstream GitLab synchronization into madcock's mirror;
- an on-screen FPS-display branch;
- joint fixes with Osaka.

A particularly important 2024-03-23 upstream-sync commit (`7998e068b6ade53a2f9dd56c4a08d63b7eeaa88b`) documents a gpSP dynarec failure mechanism: dynamically generated code changes `$gp`, while the stock IRQ/interrupt handlers expect the original stock `$gp`. The fix patches the path before `irq_handler` to restore the original stock `$gp` value. The commit explicitly states that the patch came from kobil's GitLab repository. This is direct family-runtime evidence for the significance of `$gp` ownership across external/dynamic code and native interrupt handling.

That observation is highly relevant to XGO, where our own external-core/CLASSIC work independently required explicit stock/core `$gp` transitions. It should be treated as a family-platform precedent, not proof that every XGO address or patch location is identical.

## Release-note attribution

Surviving multicore release notes preserve a division of labor that is otherwise easy to lose:

- Osaka/bnister: research and low-level development; PicoDrive/Sega CD/32X work; Genesis Plus GX; stereo-to-mono mixing; video fixes and stock scaling mode.
- kobil/kobily: multicore internals; unusual MAME2000 build/toolchain work; FPS display; options/logging behavior; substantial `core_api` work/cleanup.
- adcockm/madcock: multicore core integration, release packaging and documentation, plus other core work.
- ommokazza: NTSC overscan fix.

A contemporaneous prerelease archive compiled by adcockm explicitly labels the division as `osaka (@bnister) research and low-level developer`, `kobil (@kobily) multicore developer (internals)`, and `adcockm multicore developer (cores)`. This is stronger evidence for role separation than inferring roles from commit ownership alone.

## Discord as missing primary record — CONFIRMED

Multiple surviving project READMEs explicitly direct developers to the Retro Handhelds Discord development channel/thread for current information. Contemporary SF2000 documentation also links particular technical discoveries directly to Discord discussions. A later user guide complains that much multicore information remained scattered through Discord chats, independently corroborating the archival problem.

A surviving 4PDA SF2000 thread preserves the actual Discord channel/message anchors that were being circulated with multicore instructions:

- general SF2000 discussion: message/channel anchor `1092831839955193987`;
- test-build discussion: `1147949255911297155`;
- **SF2000 Dev** development channel: `1099465777825972347`.

The 4PDA instructions explicitly tell users to keep development discussion in the SF2000 Dev channel and link kobil's GitLab repository alongside those Discord anchors. This is useful archival evidence that the Discord dev channel was not merely casual support: it was the designated development venue surrounding the GitLab project.

The same surviving 4PDA material describes multicore as a **modification of the factory firmware**, explicitly warning users not to call it a CFW, and identifies **kobil as the main author/developer**. A later preserved 4PDA header states that contact with kobil had been lost since **August 2024**. Treat that latter statement as community-reported provenance rather than independently verified biography.

Therefore Git history and release notes should be treated as a surviving projection of a richer development conversation, not the complete record.

## GB300 propagation — CONFIRMED

The GB300 branch gives unusually good evidence of how SF2000 knowledge propagated to another HCSEMI-family product.

`tzubertowski/gb300_multicore` explicitly says the port would not exist without Osaka's work in the Retro Handhelds Discord. Independent GB300 documentation states that **osaka (`bnister`) and Prosty (`_prosty`) brought multicore to GB300 v1 on 2024-04-27**. A contemporaneous 2024-04-28 community announcement says Osaka figured out the patches necessary to make the SF2000 multicore modification work on GB300.

Later GB300 v2 documentation expands the porting credits to Osaka, Prosty, Karl Ellis, Mutandone and the original SF2000 multicore developers, especially kobil. This shows the family knowledge continuing to evolve rather than a one-time binary transplant.

GB300 tooling also preserves later Osaka firmware research: a July 2024 tool release incorporated Osaka's newer VTxx patch and removed earlier VT02/VT03 workarounds, allowing `.nfc` VTxx ROMs, including headerless VT03, to work through the revised patch. This demonstrates that Osaka/bnister continued investigating the stock emulator/firmware layer after multicore itself was already established.

## Architectural interpretation — STRONG

The accumulated evidence supports a more precise description of SF2000 multicore than 'custom firmware'. The work exploits and extends an existing stock firmware/frontend environment: stock services, libretro-like callbacks, runtime globals and interrupt handling remain relevant while external core images are introduced. The 4PDA community's explicit distinction between multicore and CFW independently matches this technical architecture.

This matters for family archaeology because later ports can inherit the *contract* without replacing the complete native environment. It also explains why cache behavior, `$gp`, stock IRQ assumptions, native save-state buffers and product-specific display/input adaptations remain important even when a new emulator core itself is portable.

## XGO relevance discovered so far

The most important convergence is now historical as well as technical. The family contract used in our XGO CLASSIC experiments was not an arbitrary modern reconstruction. Osaka/bnister's September 2023 initial SF2000 multicore code already exposed:

`g_retro_game_info` / `g_run_file_size` / `gp_buf_64m` / `gfn_retro_*` / native callbacks / `run_emulator()` / external core at 0x87000000.

Later kobil work documents the `$gp` conflict between dynamic core execution and stock interrupt handlers. Together these provide a development-history explanation for several mechanisms independently observed while adapting family multicore ideas to XGO.

The newly recovered chronology is also important: Osaka's initial code is dated **seven days before** the public creation date of kobil's GitLab project. That makes the pre-GitLab Discord/experimental phase a concrete missing chapter rather than a vague possibility.

The identification of Osaka with bnister now joins two previously separate histories: early stock-firmware reverse engineering and later multicore low-level development. This makes the likely path less like `stock researchers -> unrelated multicore developers` and more like a continuous research program in which the same low-level investigator moved from mapping stock behavior to exploiting the native frontend contract and then porting that knowledge to GB300/DY19.

## Next targets

1. Recover the pre-September-16-2023 path that produced Osaka/bnister's initial symbol map and 0x87000000 contract.
2. Use the recovered Discord anchors (`1099465777825972347` especially) to search quotes, reposts, screenshots, message links and archives from the SF2000 Dev channel.
3. Determine whether Osaka/bnister or another developer first identified `gp_buf_64m`, `run_emulator`, and the native `gfn_retro_*` table.
4. Trace the November 2023 cache-flush experiments and MAME2000 linker discussion.
5. Trace the March 2024 kobil `$gp`/IRQ discovery back to discussion or experimental commits.
6. Diff Osaka's later DY19 adaptation against the SF2000 contract to identify which portions were family-generic versus product-specific.
7. Correlate GB300 adaptation changes to LCD, input, memory, and native callback differences.
8. Search `Nikita Burnashev` as an archival provenance key while keeping real-world identity correlation separate from confirmed Osaka/bnister handle identity.
9. Recover as much of kobil's GitLab commit chronology as possible, especially the first week after project creation on 2023-09-23.
10. Trace Prosty/_prosty's role in the GB300 port and determine which product-specific patches were Osaka's versus Prosty's.

## Source anchors

- https://github.com/madcock/sf2000_multicore
- https://github.com/madcock/sf2000_multicore/commit/bdd02b0cd23e3005a6b3100278b445bf4dbcfd7c
- https://github.com/madcock/sf2000_multicore/commit/7998e068b6ade53a2f9dd56c4a08d63b7eeaa88b
- https://github.com/madcock/sf2000_multicore_cores/releases
- https://gitlab.com/kobily/sf2000_multicore
- https://github.com/vonmillhausen/sf2000
- https://github.com/tzubertowski/gb300_multicore
- https://github.com/nummacway/gb300
- https://github.com/nummacway/gb300-sf2000-tool
- https://github.com/Trademarked69/dy19_multicore
- https://4pda.to/forum/index.php?showtopic=1067862
- https://www.reddit.com/r/DataFrog/comments/17cj3zo/
- https://www.reddit.com/r/SBCGaming/comments/1cfin56/

Research log begun 2026-09-17.
