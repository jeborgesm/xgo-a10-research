# GB300 v1 native key-map behavior and XGO resource false friends

Status: **STRONG FAMILY BEHAVIORAL REFERENCE; IMPORTANT RESOURCE-NAME COLLISION IDENTIFIED**

## Headline

The GB300 v1 documentation gives substantially more exact information about the stock native mapper than the earlier resource-only reconstruction, including the exact on-disk record values, autofire representation, and several reproducible bugs in the manufacturer's editor.

At the same time, a fresh comparison against the captured XGO SD card shows that opaque resource filenames cannot be treated as semantic identities across family branches: XGO contains `hctml.ers`, but its contents are a full-screen CAPCOM PLAY SYSTEM 1 image rather than GB300's six-button highlight strip.

This makes `gpapi.bvs` unusually valuable because its *semantics*, not just its filename, independently match across XGO hardware and GB300 documentation.

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

The on-device editor indicates autofire with a `T` prefix/suffix in the displayed key name.

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

## Important new caution: opaque resource names are not semantic identities

The captured XGO SD image contains both:

```text
Resources/gpapi.bvs
Resources/hctml.ers
```

XGO hashes/sizes:

```text
gpapi.bvs
  size   614400 bytes
  SHA256 fa8a1af7699d66d07bb482f4f498f81e22e8e8481c4cbdc68d1bb3319ce3358f

hctml.ers
  size   614400 bytes
  SHA256 ebeb2e6670f7e2d567bf296770dd62e9c3d7453f4d8cef97c203b576148e2ba3
```

Both decode as 640x480 little-endian RGB565 images.

But XGO's `hctml.ers` is visually a **CAPCOM PLAY SYSTEM 1** full-screen image with character artwork. It is *not* GB300's documented `hctml.ers` six-button highlight strip.

GB300's file with the same opaque name is documented as a 320x2256 RGB565 strip containing six device images with one ABXY/shoulder button highlighted.

Therefore:

> filename equality inside this firmware family is insufficient evidence of functional equality.

The random-looking Windows-like resource names were reused/reassigned between branches.

## Why `gpapi.bvs` is still exceptional

`gpapi.bvs` does not rest on filename matching alone.

For XGO:

- it is a 640x480 controller-layout image;
- firmware references it in the pause-menu background table;
- it occupies index 4 immediately after the four normal pause pages;
- a one-instruction bound patch makes it appear on physical hardware exactly as the fifth pause page.

For GB300 v1:

- public documentation independently identifies `gpapi.bvs` as the fifth pause-menu-selected background;
- the bottom pause item is the working `Joystick` mapper.

So `gpapi.bvs` has cross-family *semantic* convergence in addition to filename convergence.

## Implication for the lift strategy

Resource-name fingerprints remain useful, but they must now be ranked:

```text
Tier A: name + matching dimensions/content + matching UI position/behavior
Tier B: name + matching dimensions/content
Tier C: name only
```

`gpapi.bvs` is Tier A.

XGO `hctml.ers` vs GB300 `hctml.ers` is a demonstrated Tier-C false friend and must not be used as evidence of shared code without independent xrefs/content checks.

For the GB300 binary lift, the safest anchors remain:

1. `gpapi.bvs` fifth-page renderer/action path;
2. literal `KeyMapInfo.kmp` file path/writer;
3. six-state UI index arithmetic;
4. the documented L/R and GBA permutation bugs;
5. 24-byte-per-player / 48-byte-per-system mapping-block arithmetic;
6. odd/even autofire field behavior.

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

Directly documented for GB300 v1:

- fifth pause-menu item is `Joystick`;
- `gpapi.bvs` is the fifth-selected pause background;
- exact KeyMapInfo block layout and logical values;
- autofire field behavior;
- optical/persistence permutation bugs.

New direct local-XGO evidence:

- XGO also contains `hctml.ers`, but its visual contents are unrelated to GB300's file of the same name.

Still pending:

- native GB300 executable xrefs/function graph;
- exact confirm/cancel/navigation event assignments;
- exact code ancestry between GB300's active position-5 handler and XGO's missing branch.
