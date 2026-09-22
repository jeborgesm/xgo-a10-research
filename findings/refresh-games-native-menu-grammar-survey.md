# Refresh Games native-menu grammar survey — first pass

Date: 2026-09-20
Branch: `research-classic-refresh-resurface`
Status: **offline survey; no firmware candidate**

## Goal

Find a stock XGO interaction grammar suitable for eight selectable textual Refresh modules without reviving the Test83/Test85 Settings-page diagnostic UI or inventing a new bitmap-heavy modal.

Target:

```text
REFRESH GAMES

Famicom
Super Famicom
Mega Drive
Game Boy
Game Boy Color
Game Boy Advance
Arcade
Classic
```

## Stock surfaces reviewed

### 1. User Menu / Setup — REJECT as final selector

State 14 is a three-card bitmap UI:
- User Games
- Language
- TV System

Selection is tracked independently from frontend state. Earlier Test05/05b/05c widened this to a fourth card and had to:
- rewrite six 640x480 localized bitmaps;
- alter selector geometry;
- alter wrap bounds;
- relocate NTSC/PAL text;
- expand redraw geometry.

This is exactly the class of UI the current work is meant to leave behind.

**Decision:** keep stock User Menu only as the launch surface for `REFRESH GAMES`; do not use its card grammar for the eight-module selector.

### 2. Search state — useful list semantics, poor direct reuse

State 15 has a genuine variable result list. Search builds up to 200 four-byte `{list_id, game_index}` records and returns to state 14.

Advantages:
- variable-length selection/list semantics are native;
- list items ultimately resolve through normal catalog-name display;
- existing navigation already handles substantially more than eight items.

Disadvantages:
- records are semantically game references, not arbitrary command strings;
- rendering depends on catalog list IDs/game indices;
- hijacking fake game records would couple Refresh commands to catalog resources and risk list-index semantics.

**Decision:** do not manufacture fake search records. Search proves the firmware already has native variable-list navigation, but its backing model is wrong for commands.

### 3. Ordinary game browser — strong visual/navigation grammar, wrong data ownership

Normal list states already provide:
- vertical selectable rows;
- count-based navigation;
- scrolling/page/base-position state;
- localized/catalog-backed text;
- selection cursor/highlight;
- confirm/cancel behavior.

The browser count cache begins at `0x80D2894C`; list position/base array at `0x80D289CC`.

Advantages:
- native visual language;
- eight items are trivial;
- navigation/scroll behavior is mature.

Disadvantages:
- ordinary browser rows are catalog entries and launch games;
- faking a new list ID/resource triplet repeats the dangerous Test90/Test91 guessed-resource failure mode;
- a synthetic catalog would blur UI and command execution ownership.

**Decision:** borrow the visual/navigation grammar, not a fake catalog/list ID.

### 4. Stock text primitive — ACCEPT as rendering primitive

`0x803528A4` is already hardware-used by our proven timed Refresh status work and draws text using the stock font/rendering path.

Known call shape from the Test06b/Test07 lineage includes:
- native font/context pointer from `gp`;
- x/y coordinates;
- stock text/style arguments;
- caller-provided string.

This means arbitrary command labels do **not** require six full-screen localized bitmap resources and do not require guessed catalog files.

**Decision:** use the stock text primitive for command labels while preserving native background/footer/input grammar.

## Emerging selector architecture

The lowest-risk UI architecture is now:

```text
stock User Menu
      |
      | REFRESH GAMES action
      v
native-owned selector state
      |
      +-----------------------------+
      | stock background grammar    |
      | stock font 0x803528A4       |
      | 8 command strings           |
      | one highlighted selection   |
      +-----------------------------+
      |
      | confirm => module ID 0..7
      | cancel  => User Menu
      v
native Refresh entry 0x807DB5CC
      |
      v
post-workspace dispatcher 0x807DB67C
```

This is deliberately **not** the old Settings card UI and deliberately **not** a fake game catalog.

## What remains OPEN before implementation

The stock text primitive alone does not establish a safe input loop.

Still required:
1. identify an existing native state/input loop whose Up/Down/Confirm/Cancel semantics can be reused without stealing a game-list state;
2. identify its selection storage lifetime;
3. identify a redraw entry that can host eight stock-font rows without interfering with footer/OSD;
4. prove clean return to state 14 on Cancel;
5. prove Confirm can hand a module ID to native Refresh without direct-calling module internals.

Do not build a firmware candidate until these are closed.

## Evidence discipline

- User Menu bitmap/card geometry: **BIN + prior HW**
- Search result model/capacity: **BIN**
- ordinary browser count/base-position arrays: **BIN + HW**
- stock text primitive `0x803528A4`: **BIN + prior HW**
- proposed stock-font command selector: **DESIGN**
- exact reusable input-loop/state slot: **OPEN**
