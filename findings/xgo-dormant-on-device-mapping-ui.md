# Dormant on-device button-mapping UI evidence

Status: **STRONG RESOURCE-LINEAGE EVIDENCE; EXECUTABLE ROUTING NOT YET PROVEN**

## Headline

The captured XGO SD card contains a full-screen 640x480 RGB565 resource named:

```text
Resources/gpapi.bvs
```

The file is exactly 614400 bytes (`640 * 480 * 2`) and decodes cleanly as little-endian RGB565.

The decoded screen is unmistakably a controller-action configuration background: it contains a D-pad on the left, six circular action-button positions on the right, the stock XGO/SF2000 in-game-menu visual style, and the localized heading equivalent to **Configure Action**.

This is not a generic controller graphic inferred from filename alone. The actual XGO resource image visually represents the mapping UI we are looking for.

## Upstream SF2000 convergence

Public SF2000 resource archaeology independently identifies the same filename, `gpapi.bvs`, as an **unused in-game menu position associated with a button-layout-changing UI**.

That makes the XGO copy especially significant: the XGO did not merely inherit generic emulator code; it retained the exact dormant UI background associated upstream with button-layout configuration.

This is consistent with other XGO evidence already recovered:

```text
%s/save/%s.kmp         present in firmware
set_keymap()           present and executable
48-byte per-game KMP   matches pre-May SF2000 family layout
Resources/Test.zsf     present
KeyMapInfo.kmp         absent
```

The combined picture is now:

```text
mapping UI artwork survives on XGO SD card
            +
per-game .kmp runtime survives in XGO firmware
            +
stock keymap compiler survives in XGO firmware
```

The remaining unknown is whether the menu/controller code that connects the UI to the `.kmp` writer also survives and is merely unreachable, or whether only the resource and lower-level mapping machinery remain.

## Direct XGO resource evidence

Recovered card path:

```text
Resources/gpapi.bvs
```

Properties:

```text
size:   614400 bytes
format: RGB565 little-endian
shape:  640x480
```

Decoded content:

- stock dark-blue in-game-menu background;
- D-pad graphic;
- six configurable circular button positions;
- left-side selection arrow;
- localized mapping/configuration title.

The firmware also contains the literal filename:

```text
0x009a3020  gpapi.bvs
```

and the firmware's resource-name pointer table contains a pointer to it at file offset approximately:

```text
0x00a3c328 -> 0x809a3020 -> "gpapi.bvs"
```

This establishes that the resource is represented in the firmware's resource-name table, not merely orphaned on the SD card.

Important limitation: a filename-table entry does **not** yet prove an executable code path actually selects that resource at runtime.

## Contrast with later mapping UI

The XGO card does **not** contain the later SF2000 May-era mapping resource set such as the known `lk7tc.bvs` / `ztrba.nec` assignment-label assets, nor does it contain `Resources/KeyMapInfo.kmp`.

Therefore the most promising target is not the later global-per-system SF2000 mapper. It is the older/dormant **in-game mapping screen represented by `gpapi.bvs`**, which fits the XGO's surviving per-ROM `.kmp` architecture much better.

## Why this matters

If the routing code survives, the ideal XGO architecture may already exist in latent form:

```text
game running
    |
Select + Start
    |
stock in-game menu
    |
button/action configuration
    |
write /<system>/save/<rom>.kmp
    |
set_keymap()
```

That would be superior to a Windows-only mapper because it would preserve the stock handheld workflow and naturally provide per-game mappings.

Even if the original route has been compiled out, the surviving full-screen resource means we may be able to reuse the stock artwork and existing input/menu framework instead of inventing a mapping UI from scratch.

## Next static targets

1. Locate code references to the resource-name table entry for `gpapi.bvs`, not merely the filename string.
2. Identify the stock in-game menu's item-count / selection dispatch table and determine whether there is a dormant menu slot corresponding to the upstream 'position 5' description.
3. Trace any branch from that slot to controller-map state structures or the 48-byte `.kmp` buffer.
4. Search for file-write construction using `%s/save/%s.kmp`; current `run_emulator` read-side behavior is known, but the writer is the crucial missing link.
5. Determine whether the dormant screen can be exposed by changing a menu item count/table entry rather than injecting a new UI.
6. Only after the control-flow path is understood, design a minimally invasive hardware probe.

## Evidence boundary

We can now say with confidence:

> The physical XGO resource set contains a genuine controller-action configuration screen, and the XGO firmware knows the `gpapi.bvs` resource name while retaining the per-game `.kmp` runtime machinery.

We cannot yet say:

> The XGO has a callable hidden mapping menu that can already save `.kmp` files.

That is the next thing to prove.