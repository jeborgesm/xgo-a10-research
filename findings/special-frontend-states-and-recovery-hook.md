# XGO special frontend states and recovery-hook surface

Date: 2026-09-06
Branch: `research-game-list-scanning`

Status: **special frontend states substantially labeled; startup recovery hook identified; refresh trigger still intentionally uncommitted**

## State map

The main frontend state byte is `gp-0x0df4` / runtime `0x80c33980`.

Direct dispatch around `0x80357768` treats states 13, 14, and 15 specially while ordinary list states follow the catalog browser path.

Combined with the resource table and persistence behavior, the current map is:

```text
0..11  normal game categories
12     Favorites
13     History
14     User Menu / Setup
15     Search
```

### Why state 12 = Favorites

Resource-table list ID 12 resolves to `Falas.clk`, already proven to be the Favorites database. State 12 remains on the ordinary indexed-list browsing side rather than taking one of the explicit 13/14/15 special branches.

### Why state 13 = History

Resource-table list ID 13 resolves to `Hisas.boa`, already proven to be the History database. State 13 takes a dedicated branch because History is record-backed rather than a normal fixed string catalog.

### Why state 14 = User Menu / Setup

The state-14 path directly manipulates persisted frontend settings:

- `gp-0x0d7c` language state;
- `gp-0x5f40` TV-system state;
- display reconfiguration after the TV-system toggle.

The same state-14 handler transitions to state 15 and records 14 as the return state, proving Search is launched from User Menu / Setup.

External GB300-family documentation independently describes the same User Menu items: Search, Language, User games, and Television system. This is family corroboration, not the authority for the XGO state addresses.

### Why state 15 = Search

The state-15 path directly references `SearchKey: %s`, uses the dedicated search-slot language table, builds 4-byte `{list_id, game_index}` result records, and returns to state 14.

## The existing User Games menu action

Within state 14, the selected User Menu item is tracked separately from the main frontend state.

The handler has distinct branches for:

- language selection;
- TV-system toggle;
- Search transition;
- the remaining first/default User Games action.

The default User Games branch returns through the normal frontend path rather than creating another persistent-settings editor.

This fits the family UI description: User Games is a navigation action into the freely scanned ROM area, not a setting that needs its own persisted word.

### Design implication

Do not hijack the existing User Games action blindly. It already has a user-visible semantic role.

For the first proof, a hidden diagnostic chord while on the User Menu is lower risk than altering menu row count/layout. A later polished implementation can add an explicit Refresh Games action only after the stock User Menu renderer and selection bounds are fully mapped.

## Earliest safe transaction-recovery hook

The normal once-per-session User-ROM scanner call occurs at:

`0x80359404 -> 0x80353ae0`

By this point:

- the SD card and Resources filesystem are operational;
- frontend file I/O is working;
- the one-shot ROMS scan has not yet run;
- built-in FC/SFC/etc. catalogs have not yet been browsed in the normal startup path.

Therefore the control point immediately before the existing `tsmfk.tax` regeneration is an excellent recovery hook for future built-in catalog transactions.

Proposed ordering:

```text
startup
  -> SD/resources available
  -> check catalog transaction marker
  -> if incomplete: validate/restore/finish triplet
  -> then run stock ROMS -> tsmfk.tax scanner
  -> continue stock frontend
```

This avoids adding a separate startup task and guarantees recovery occurs before the user can enter a built-in list.

## Why recovery should remain independent of the normal scanner

The native scanner has a one-shot flag specifically for User Games. Reusing that flag for built-in recovery would conflate two independent responsibilities.

A future recovery routine should have its own small transaction marker and only return control to the untouched stock scanner after the built-in triplet is known consistent.

## Current preferred first proof

Still use the metadata-only FC append for already-present `Bomber Man 2.zfc`, but do not yet make the updater permanent.

The first firmware-side proof should separate two questions:

1. can the stock browser consume a stable-appended synchronized triplet on hardware?
2. can XGO safely perform that append itself from an explicit command?

The lowest-risk sequence is therefore:

- first hardware-test the already-generated static triplet on a disposable SD clone, with no runtime writer;
- only after browse/search/launch behavior passes, add the on-device writer/transaction logic.

This prevents debugging filesystem mutation and catalog semantics simultaneously.

No firmware candidate is produced by this finding.