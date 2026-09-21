# Test85 selector state recovery and CLASSIC resurface dispatch plan

Date: 2026-09-20
Branch: `research-classic-refresh-resurface`
Status: **offline closure; no hardware candidate**

## Finding 1 — Test85 did not create a durable module-selection ABI

The recovered Test85/Test97 lineage shows that the ugly selective UI and the executable dispatcher were coupled more tightly than the previous shorthand "selected module variable" implied.

The firmware hook at `0x807DB67C` jumps to `0x80A386BC`. By that point the native Refresh function has already created its full `0xB0` frame and initialized `0x807DB92C/0x807DB930`.

The selective dispatcher then directly decides which helper sequence to run. There is no evidence of a clean, persistent, independently-owned "Refresh module ID" global that can simply be retained while deleting the Settings-page UI.

This corrects the previous working assumption that the Test85 selection state itself might be reusable as a standalone ABI.

## Finding 2 — the useful Test85 artifact is the post-workspace dispatch location

The useful inheritance is architectural:

```text
native Refresh entry
   |
   v
full native frame
   |
   v
workspace initialization
   |
   v
0x807DB67C   <--- proven module-dispatch interception point
```

Test85 proved that this point can redirect execution while preserving the native Refresh entry context. Its problems came from the module-specific execution paths and UX, not from the existence of the interception point itself.

For CLASSIC, the correct dispatch action at this point is exceptionally small:

```text
CLASSIC:
    s5 = 0
    jump 0x80A38000
```

No helper runner should be inserted between the native frame and CLASSIC.

## Finding 3 — selected stock systems and CLASSIC should share a new tiny ABI

Instead of carrying forward Test85 UI state, define one explicit volatile selection byte/word owned by the new Refresh UI/dispatcher contract:

```text
0 FC
1 SFC
2 MD
3 GB
4 GBC
5 GBA
6 Arcade
7 CLASSIC
```

The UI writes the module ID immediately before entering the native Refresh function. The Refresh function consumes it at `0x807DB67C` after its own frame/workspace initialization.

This keeps presentation and execution independent:

```text
+-----------------------------+
| Native-looking UI           |
| returns module ID 0..7      |
+--------------+--------------+
               |
               | one module ID
               v
+-----------------------------+
| Native Refresh entry        |
| owns frame/workspace        |
+--------------+--------------+
               |
               v
+-----------------------------+
| dispatcher @ post-workspace |
+------+----------------------+
       |
       +--> stock module
       |
       +--> CLASSIC
               |
             s5=0
               |
               v
          0x80A38000
               |
               v
       /CLASSIC/refresh.xgc
```

The selection variable is **ephemeral command state**, not a persistent setting.

## Why not reuse a normal frontend state/global blindly

The main frontend state at `gp-0x0DF4 / 0x80C33980` has established meanings:
- 0..11 game lists;
- 12 Favorites;
- 13 History;
- 14 User Menu;
- 15 Search.

Overloading that byte with Refresh module IDs would collide with real frontend navigation semantics.

Likewise, the User Menu selection has established 0..2 semantics in stock and was widened by the old custom UI experiments. It should not become the long-term module ABI.

The new command state should live in a dedicated proven-safe scratch/global slot or in an execution path that passes the value without persistence. Exact storage address remains OPEN until the native menu grammar is selected.

## CLASSIC resurface module gate is now logically closed

For the CLASSIC module itself, no new runtime algorithm is needed.

Required execution:

```text
UI chooses CLASSIC
      |
      v
set command ID = 7
      |
      v
enter native Refresh 0x807DB5CC
      |
      v
native frame + workspace
      |
      v
dispatch at 0x807DB67C
      |
      v
s5 = 0
      |
      v
jump 0x80A38000
      |
      v
proven external CLASSIC helper
      |
      v
native Games Updated / No New Games / Refresh Failed
      |
      v
native epilogue
```

This specifically avoids the Test92 continuation/stack mismatch.

## Important stock-module warning

Do not generalize the old Test85 helper sequence to all stock systems yet.

Test85/Test97 standalone helper execution exposed heap/lifecycle concerns, and MD now has the separate Test106 hardened transaction path. Therefore the future dispatcher must map each module to its currently proven execution contract rather than assume one universal runner.

Current execution-policy table:

```text
FC       proven Test75 enrichment lineage; exact selective adapter TBD
SFC      proven Test74 enrichment lineage; exact selective adapter TBD
MD       Test106 hardened two-stage transaction path
GB       propagation not yet authorized
GBC      propagation not yet authorized
GBA      propagation not yet authorized
Arcade   stock path; selective refresh contract TBD
CLASSIC  proven continuation path now closed
```

This is another reason to keep module ID and module execution separate.

## UI direction

The old Settings selector can now be discarded conceptually. Nothing in the CLASSIC runtime design depends on its renderer, labels, page geometry, or widened User Menu row behavior.

Next target is exclusively native menu grammar archaeology:
1. inventory stock screens with >=6 selectable textual rows;
2. prefer one whose labels are rendered from strings/tables rather than baked full-screen Resources bitmaps;
3. recover selection return/callback contract;
4. determine whether eight rows fit or whether stock scrolling is available;
5. feed only the selected module ID into the Refresh command ABI above.

The final desired presentation remains:

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

No Refresh All.
