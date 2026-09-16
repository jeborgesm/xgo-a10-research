# SF2000 community archaeology — people-outward pass

Date: 2026-09-16
Branch: `research-a10-hardware-lineage`

## Goal

Instead of searching for `XGO firmware`, trace the people who originally reverse-engineered SF2000 firmware behavior and ask what devices, SDKs, forks, repositories, and Discord-derived findings they pursued afterward.

This is motivated by the XGO A10 firmware's strong SF2000-family fingerprints: `bisrv.asd`, per-game `.kmp` behavior, stock libretro-style frontend/core contract, catalog/resource conventions, and HC15xx/B210-family evidence.

## Reconstructed researcher graph

### bnister / Discord `osaka`

This is the strongest person-outward lead.

Documented SF2000 discoveries attributed to bnister include:

- discovering game-specific `.kmp` key-binding support;
- locating default emulator mappings inside `bisrv.asd`;
- firmware CRC32 research/code used by patchers;
- GBA BIOS path/workaround discoveries;
- audio-format testing/research;
- substantial low-level hardware/firmware investigation.

Public GitHub repositories under `bnister` show that the work did not stop at simple SF2000 tooling. Relevant repositories include:

- `bnister/sf2000_hcrtos`
- `bnister/sf2000_hcrtos_RetroArch`
- `bnister/sf2000_hcrtos_tgbdual`
- `bnister/sf2000_multicore`
- `bnister/sf2000-collection`

Most important: `bnister/sf2000_hcrtos` is a preservation/fork trail into the HiChip/HC-FreeRTOS/HCRTOS environment rather than merely an SF2000 utility.

The modern `Data-Frog-Central/NocturnalRTOS` documentation explicitly describes SF2000/GB300 and `other similar devices` as using HiChip Semiconductor's HC-FreeRTOS SDK platform, identifies SF2000 as HCSEMI B210, and points to bnister's HCRTOS backup.

This makes bnister/osaka the highest-value individual to trace for any Discord-era mention of later HCSEMI/B210/HC15xx derivatives.

### notv37

Documented contributions include:

- decoding the button-bit mappings building on bnister's discovery of mapping storage;
- audio sample-rate/discovery math;
- emulator-version/source identification with bnister.

The public SF2000 button-mapping tool preserves an exact Discord message URL credited to `@notv37`:

`https://discord.com/channels/741895796315914271/1099465777825972347/1104285497804738640`

This is valuable archaeological metadata even if Discord content itself is inaccessible: it identifies server/channel/message coordinates that can be searched in quotes, mirrors, screenshots, forks, archives, or references.

### adcockm / GitHub `madcock`

Documented SF2000 contributions include unusually deep arcade investigation: supported ROM-set mixture, metadata, playable-set DATs, and later multicore work.

Public GitHub footprint is extensive and strongly technical:

- `madcock/sf2000_multicore`
- `madcock/sf2000_multicore_cores`
- `madcock/SF2000_Builds`
- `madcock/sf2000-fbalpha`
- many SF2000-targeted libretro-core forks, including MAME2000 and FBA/CPS variants.

The multicore Makefile contains historical local paths under `/home/adcockm/...`, strongly linking the Discord researcher identity `adcockm` with the public GitHub `madcock` work.

This is especially relevant to XGO because our CLASSIC/MAME2000 and CPS investigations repeatedly converged on this same multicore lineage.

### taizou / GitHub `tzlion`

Taizou authored FROGTOOL and reverse-engineered the stock built-in ROM-list/catalog resources. This is directly relevant to XGO because our catalog-refresh work independently encountered the same family design idea: static built-in catalog resources rather than simply scanning ROM folders.

Public repositories include:

- `tzlion/frogtool`
- handheld/Game Boy reverse-engineering/tooling repositories unrelated to SF2000.

No public XGO/A10/DY10 continuation was found in the repository list during this pass.

### additional named researchers worth following

The SF2000 documentation/version history preserves other Discord-era names tied to specific discoveries:

- `kid_sinn#9691` — `nvinf.hsp` game-count behavior;
- `luke7352` — `bisrv.asd` corrections/inspection;
- `_prosty` / Prosty — with bnister/osaka, brought multicore to GB300 v1 and later GB300 v2;
- Karl Ellis and Mutandone — contributions to later GB300 multicore work.

These names expand the people-first graph beyond the four most obvious researchers.

## Important continuation discovered: SF2000 -> GB300

The people-outward method produced a concrete historical continuation:

- Discord user osaka (`bnister`) and Prosty (`_prosty`) ported multicore to GB300 v1 on 2024-04-27;
- the same pair ported it to GB300 v2 on 2024-10-05, with contributions from Karl Ellis and Mutandone.

This demonstrates that at least one core SF2000 researcher explicitly continued following sibling/derivative cheap handheld hardware after the initial SF2000 work.

That is exactly the behavioral pattern we hoped to establish. It does not yet connect them to XGO A10, but it substantially strengthens the rationale for mining their Discord/GitHub trail for other later siblings.

## Direct XGO/A10 search against researcher repositories

Targeted GitHub code searches across the obvious bnister and madcock SF2000 repositories for:

- `XGO`
- `A10`
- `DY10`
- `HC15`
- `HC1512`
- `H1512`

produced no useful direct hit in this pass.

This is negative evidence only. It does not search private/deleted Discord material, repository history outside indexed default branches, private repositories, issue comments not surfaced by code search, or files that use only generic device descriptions.

## High-value Discord coordinates recovered

Retro Handhelds Discord server ID visible in preserved tool source:

`741895796315914271`

SF2000-related channel ID in the notv37 attribution:

`1099465777825972347`

Specific preserved message ID:

`1104285497804738640`

These numeric IDs should be treated as durable search fingerprints. Search engines, archive captures, screenshots, bots, quote mirrors, forks, and copied documentation may preserve references even when the original Discord message is inaccessible.

## Interpretation

The people-outward hypothesis is validated as a research method even though this first pass did not expose an A10 message.

The strongest finding is that the SF2000 research community did not remain confined to SF2000: bnister/osaka and collaborators explicitly moved into GB300 variants and into the underlying HC-FreeRTOS/HCRTOS SDK/platform. The community also produced stock-firmware modification, multicore ports, emulator archaeology, catalog tooling, mapping research, audio research, and custom-firmware experiments.

Therefore a later Games Power/XGO derivative could plausibly have been discussed as `another similar device`, a board/SoC name, or a generic cheap handheld rather than `XGO A10`.

## Next people-outward pivots

1. Mine GitHub issue/commit/branch history for bnister's HCRTOS and multicore repositories, not only current default-branch code search.
2. Search the recovered Discord server/channel/message numeric IDs on the public web and archives.
3. Search `osaka`, `bnister`, `_prosty`, `notv37`, `adcockm`, `madcock`, `taizou`, `kid_sinn`, `luke7352`, Karl Ellis, and Mutandone together with generic phrases: `game power bank`, `Games Power`, `10000mAh`, `HCSEMI`, `B210`, `HC15`, `HC1512`, `H1512`, `bisrv`, `Archive.sys`, `.kmp`.
4. Follow GB300 v1/v2 work forward chronologically and inspect what additional hardware was tested after October 2024.
5. Inspect forks of `sf2000_hcrtos`, `sf2000_multicore`, `NocturnalRTOS`, and GB300 tools for device-specific branches or abandoned experiments.
6. Search Discord-derived documentation source files for additional raw `discord.com/channels/...` links and recover their coordinates.
7. Search commit messages and issue discussions for phrases such as `similar device`, `new device`, `clone`, `variant`, `B210`, `HCSEMI`, and `hichip`.

## Evidence discipline

No person named here is claimed to have worked on XGO A10. The current result establishes researcher continuity and a concrete SF2000 -> GB300/platform-development path, which justifies deeper person/community archaeology.
