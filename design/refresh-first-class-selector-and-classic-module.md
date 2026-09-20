# Refresh UX direction: independent modules and first-class section selector

This is the forward architecture note after closing the MD Refresh investigation.

## Product requirement

Refresh must stop behaving like an incidental Settings-page hack.

The desired user-facing model is a first-class Refresh feature with an explicit section selector.

Target sections:

    REFRESH GAMES

    Famicom
    Super Famicom
    Mega Drive
    Game Boy
    Game Boy Color
    Game Boy Advance
    Arcade
    Classic

No Refresh All action is required.

CLASSIC must resurface as an independent Refresh module. It must not be folded into a stock-console scanner or hidden behind the current settings-page selection hack.

## Logical architecture

                         REFRESH GAMES
                              |
          +-------------------+-------------------+
          |                   |                   |
       STOCK               ARCADE             CLASSIC
          |                   |                   |
    +-----+------+            |             independent
    | | | | | | |            |             CLASSIC refresh
   FC SFC MD GB GBC GBA       |             contract
    | | | | | | |            |
    +-----+------+            |
          |                   |
          +---------+---------+
                    |
              common status UI
                    |
          +---------+----------+
          |                    |
       Updated             No changes
          |
        Failed

Each selector entry dispatches only its own module.

## Required separation

Selection/UI and refresh implementation are different layers:

    first-class Refresh UI
             |
             v
       selector/list ID
             |
             v
      module dispatcher
       /     |      \
    stock  Arcade  Classic
      |       |       |
      v       v       v
    module-specific refresh contract
             |
             v
       common result contract

Do not make the renderer responsible for scanning/import logic.

Do not make CLASSIC pretend to be a stock TAX/NEC/BVS list if its proven contract differs.

## CLASSIC historical requirements to preserve

The existing CLASSIC implementation already established important behavior that must survive resurfacing:
- first-class CLASSIC list;
- generalized CLASSIC importer from Test47 lineage;
- normalized /cores/classic-mame2000/core.xgc;
- CLASSIC Save/Load from Test52;
- independent CLASSIC ROM folder /CLASSIC/bin/;
- CLASSIC wrapper/catalog contract;
- stable no-change Refresh behavior reached before branch closure;
- Volume OSD and stock console behavior must remain intact.

The obsolete Pac-Man/Ms. Pac-Man investigation is not a prerequisite for Refresh UX work.

## UI direction

Do NOT return to:
- custom User Menu renderer experiments;
- mapper-style modal that hard-froze;
- guessed dormant list/page resources;
- Test90/Test91 inferred REFRESH page/resource injection;
- direct CLASSIC jump to 0x80A38000 (Test92 hard lock).

Instead, investigate an existing native list/menu grammar capable of displaying a variable list of textual choices and returning a selected index.

Preferred visual behavior:

    +--------------------------------+
    |         REFRESH GAMES          |
    |--------------------------------|
    | > Famicom                      |
    |   Super Famicom                |
    |   Mega Drive                   |
    |   Game Boy                     |
    |   Game Boy Color               |
    |   Game Boy Advance             |
    |   Arcade                       |
    |   Classic                      |
    +--------------------------------+

The exact appearance should follow an existing native XGO menu/list implementation rather than a newly drawn modal.

## Archaeology plan

Before firmware changes:
1. inventory native menus that already render 6+ selectable text rows;
2. identify their item-table format, selection cursor state, scrolling behavior, callback/return contract, and backing resource dependencies;
3. prefer a menu whose item labels can live in existing firmware/code data without introducing guessed Resources files;
4. determine whether eight entries fit natively or require scrolling;
5. identify a safe entry point from the existing Refresh command;
6. map each selected index to an independent module;
7. recover the proven CLASSIC Refresh invocation contract rather than direct-jumping its internal bootstrap;
8. preserve common Refresh result/status handling.

## Evidence discipline

The selector architecture above is DESIGN, not XGO-proven architecture.

Any native menu chosen to implement it must first be established through BIN/HW evidence.

Do not promote a family/upstream menu implementation into XGO fact without matching binary evidence.

## Immediate research target

Find the best existing XGO-native selectable-list implementation and map its ABI/resource contract.

In parallel, reconstruct the last hardware-proven CLASSIC Refresh dispatcher/invocation path from the Test45-Test52/Test72 lineage so CLASSIC can become an independent module again.
