# GB300 v1 native key-map behavior and XGO resource false friends

Status: **STRONG FAMILY BEHAVIORAL REFERENCE; RESOURCE-SLOT REPURPOSING IDENTIFIED**

## Headline

The GB300 v1 documentation gives substantially more exact information about the stock native mapper than the earlier resource-only reconstruction, including the exact on-disk record values, autofire representation, and several reproducible bugs in the manufacturer's editor.

A fresh comparison against the captured XGO SD card also exposes an important branch-development pattern: opaque resource filenames were not stable semantic names. In at least one case, GB300 appears to have **repurposed an older SF2000/XGO resource slot for the native mapper**.

The strongest example is `hctml.ers`:

- XGO: 640x480 RGB565 CAPCOM PLAY SYSTEM 1 / Arcade main-menu artwork;
- public SF2000 documentation: 640x480 RGB565 **Arcade main menu background**;
- GB300 v1: 320x2256 RGB565 **six physical-button highlight images used by the key-map editor**.

GB300 v1 has no Arcade system. That makes the simplest lineage interpretation that a now-unused Arcade resource identity was reused for mapping UI data.

This is useful for the binary lift because it tells us to look for **repurposed resource indices/code paths**, not merely newly-added mapper filenames.

`gpapi.bvs` remains exceptional because its semantics, pause-menu position, and dimensions converge independently across XGO and GB300.

## GB300 v1 KeyMapInfo layout

Public GB300 v1 archaeology documents that `KeyMapInfo.kmp` does not exist by default and is created after the user assigns a non-standard mapping.

Each emulated console contributes:

```text
24 bytes player 1
24 bytes repeated immediately (likely player 2)
```

The physical save order for the normal systems is:

```text
X, Y, L, A, B, R
```

GBA is the family exception:

```text
L, R, X, A, B, Y
```

This closely matches the earlier SF2000 mapping-tool source and the 48-byte XGO per-game record model.

## Exact logical values in the later/native family mapper

GB300 v1 documentation gives the logical values presented/used by the stock map system.

### FC

```text
0x0800 = A
0x0000 = B
0x0A00 = FDS Turn Disk
0x0B00 = FDS Eject/Insert
```

### PCE

```text
0x0800 = I
0x0000 = II
```

### SFC

```text
0x0800 = A
0x0000 = B
0x0A00 = X
0x0B00 = Y
0x0900 = L
0x0100 = R
```

### MD/SMS

```text
0x0800 = A
0x0000 = B
0x0A00 = X
0x0B00 = Y
0x0100 = C
0x0900 = Z
```

SMS interprets `0x0000` as button 1 and `0x0100` as button 2.

### GB/GBC

```text
0x0800 = A
0x0000 = B
```

### GBA

```text
0x0800 = A
0x0000 = B
0x0A00 = L
0x0B00 = R
```

These byte-oriented values are the later firmware's persisted representation and should not be blindly substituted for the XGO runtime/libretro IDs. Their value here is that they expose exactly which choices the manufacturer's native editor attempted to present for each console family.

## Autofire behavior is exactly documented

After each 16-bit button value comes a 16-bit autofire field:

```text
odd value  -> autofire on (normally 0x0100)
even value -> autofire off (normally 0x0000)
```

The on-device editor indicates autofire with a `T` in the displayed key name.

This is a direct behavioral match for the XGO machine-code result where each 4-byte record consists of a logical target plus a turbo/autofire flag.

## Manufacturer editor bugs are useful binary fingerprints

GB300 v1 documentation gives unusually specific bugs in the stock key-map editor:

1. For all emulators except GBA, the editor's optical representation swaps physical R and L.
2. SFC compensates by swapping the stored L/R values, causing defaults to *look* correct while custom mappings become confusing.
3. For GBA, the optical representation swaps physical L with X and R with Y.
4. GBA persistence compensates by swapping the corresponding values.
5. Several logical values can be selected/displayed even when the target emulator does not implement them.

These are not just user-facing defects. They give us excellent fingerprints for a binary lift:

```text
UI index order != persistence index order
```

with branch-specific permutations that can help identify the relevant table or function in disassembly.

## Fifth pause-menu position is independently reinforced

GB300 resource documentation identifies:

```text
gpapi.bvs = pause menu, fifth entry selected
```

and describes the bottom pause-menu entry as `Joystick`.

It further describes `mczwq.ikb` as a six-device-logo strip that is shown/hidden when DOWN navigation reaches/leaves the bottom `Joystick` item.

That is unusually close to the XGO hardware result:

```text
stock bound: indices 0..3
one-instruction bound patch: indices 0..4
index 4: gpapi.bvs controller-layout screen
no stock action handler
```

This remains the strongest evidence that the later working mapper descended from the same family UI position as XGO's stranded screen.

## GB300 mapper resource set is physically confirmed in preserved stock files

The public `znx-x/gb300-firmware` repository preserves the stock GB300 v1 resource files and gives exact file sizes/hashes.

Key mapper assets include:

```text
gpapi.bvs
  size 614400
  git blob a6243e32b4e5867ba1318954093411bffd962be5

hctml.ers
  size 1443840
  git blob 2785fbb8d0f615a74c546a5e51c13920123ff1c9

lk7tc.bvs
  size 39936
  git blob 94b06d16c9045145de26bdf587c10a0a67f88e17

mczwq.ikb
  size 430080
  git blob f711c296e2a9660259288debe70d1de66cfefe36

ztrba.nec
  size 40960
  git blob f1187703869518bea6327499a0685eff5442c2f6
```

The XGO captured Resources directory contains only the first two names from this set:

```text
gpapi.bvs  -> yes
hctml.ers  -> yes, but old Arcade meaning
lk7tc.bvs  -> absent
mczwq.ikb  -> absent
ztrba.nec  -> absent
KeyMapInfo.kmp -> absent
```

This is consistent with an older/incomplete mapper shell rather than the completed GB300 native editor.

## Resource-slot repurposing: stronger than a generic 'false friend'

XGO hashes/sizes:

```text
gpapi.bvs
  size   614400 bytes
  SHA256 fa8a1af7699d66d07bb482f4f498f81e22e8e8481c4cbdc68d1bb3319ce3358f

hctml.ers
  size   614400 bytes
  SHA256 ebeb2e6670f7e2d567bf296770dd62e9c3d7453f4d8cef97c203b576148e2ba3
```

Both XGO files decode as 640x480 little-endian RGB565.

XGO's `hctml.ers` is visually a **CAPCOM PLAY SYSTEM 1** full-screen image with character artwork.

Public SF2000 archaeology independently identifies `hctml.ers` as the **Arcade main menu background**, also 640x480 RGB565. Therefore XGO and the normal SF2000 branch agree on the original semantic role.

GB300 v1 instead uses the same opaque filename for a 320x2256 RGB565 strip containing six device images with one ABXY/shoulder button highlighted for the key-map editor.

GB300 v1 notably has no Arcade system.

The likely branch evolution is therefore:

```text
older/common branch / SF2000 / XGO
hctml.ers -> Arcade main-menu background

                 GB300 v1 removes Arcade
                           |
                           v
GB300 v1 repurposes hctml.ers resource identity
             -> key-map physical-button highlight strip
```

This is not yet executable-code proof that the same numeric resource-table index was reused, but it is a strong resource-layer clue and gives us a new comparison strategy.

## XGO firmware resource-table positions

The XGO executable's resource pointer table directly references:

```text
0x80a3c328 -> 0x809a3020 -> gpapi.bvs
0x80a3c444 -> 0x809a32bc -> hctml.ers
```

`gpapi.bvs` is in the tight pause-page cluster:

```text
0x80a3c318 -> dism.cef
0x80a3c31c -> d2d1.hgp
0x80a3c320 -> bisrv.nec
0x80a3c324 -> pwsso.occ
0x80a3c328 -> gpapi.bvs
```

`hctml.ers`, by contrast, lives later among the system/main-menu background resource group rather than beside `gpapi.bvs`.

That makes a useful future GB300 binary comparison question:

> Did GB300 keep the same resource-table slot for `hctml.ers` and simply change the asset/use, or did its entire resource table get reorganized?

The answer can help distinguish local feature grafting from broader frontend refactoring.

## Why `gpapi.bvs` is still exceptional

`gpapi.bvs` does not rest on filename matching alone.

For XGO:

- it is a 640x480 controller-layout image;
- firmware references it in the pause-menu background table;
- it occupies index 4 immediately after the four normal pause pages;
- a one-instruction bound patch makes it appear on physical hardware exactly as the fifth pause page.

For GB300 v1:

- preserved stock files contain a same-size 614400-byte `gpapi.bvs`;
- public documentation independently identifies it as the fifth pause-menu-selected background;
- the bottom pause item is the working `Joystick` mapper.

So `gpapi.bvs` has cross-family *semantic* convergence in addition to filename convergence.

## Implication for the lift strategy

Resource-name fingerprints must now be ranked:

```text
Tier A: name + matching dimensions/content + matching UI position/behavior
Tier B: name + matching dimensions/content
Tier C: name only
```

`gpapi.bvs` is Tier A.

`hctml.ers` is more interesting than a simple Tier-C mismatch because the evidence suggests intentional **resource repurposing** when GB300 dropped Arcade.

For the GB300 binary lift, the safest anchors remain:

1. `gpapi.bvs` fifth-page renderer/action path;
2. literal `KeyMapInfo.kmp` file path/writer;
3. six-state UI index arithmetic;
4. the documented L/R and GBA permutation bugs;
5. 24-byte-per-player / 48-byte-per-system mapping-block arithmetic;
6. odd/even autofire field behavior;
7. loads of the repurposed `hctml.ers` and new `lk7tc.bvs`/`mczwq.ikb`/`ztrba.nec` assets.

## XGO adaptation remains unchanged

Do not transplant later `KeyMapInfo.kmp` persistence.

Use the manufacturer's later native editor behavior as the controller template while retaining XGO's older, more useful per-game persistence:

```text
XGO pause index 4 / gpapi.bvs
        +
recovered family mapper state machine
        +
XGO current-game system context
        +
XGO 48-byte per-game mapping buffer
        +
XGO set_keymap()
        +
XGO existing %s/save/%s.kmp writer
```

## Evidence boundary

Hardware-proven on XGO:

- index 4 renders the controller-layout `gpapi.bvs` screen when the menu bound is increased;
- no interactive handler is active there.

Directly documented/preserved for GB300 v1:

- fifth pause-menu item is `Joystick`;
- `gpapi.bvs` is the fifth-selected pause background;
- exact KeyMapInfo block layout and logical values;
- autofire field behavior;
- optical/persistence permutation bugs;
- physical mapper resource files and sizes.

Direct local-XGO evidence:

- XGO `hctml.ers` is the older Arcade/CPS1 full-screen resource;
- XGO lacks the later GB300 mapper support assets `lk7tc.bvs`, `mczwq.ikb`, and `ztrba.nec`.

Cross-family inference, strongly supported but not executable-proven:

- GB300 likely repurposed the old Arcade `hctml.ers` identity for its mapper after dropping Arcade.

Still pending:

- native GB300 executable xrefs/function graph;
- exact confirm/cancel/navigation event assignments;
- exact code ancestry between GB300's active position-5 handler and XGO's missing branch.
