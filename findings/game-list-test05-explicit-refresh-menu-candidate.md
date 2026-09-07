# Game-List Test05 — explicit Refresh Games User Menu candidate

Date: 2026-09-07
Branch: `research-game-list-refresh-implementation`

Status: **implementation complete; private-vault composition pending**

## Why Test05 exists

Test04 is hardware-confirmed and proves XGO can rewrite the synchronized built-in catalog triplet on-device, invalidate the cached count, and return to the untouched stock browser.

Test04 deliberately used `User Menu -> User Games` as a semantic proof trigger. That is not the desired shipping UX because opening User Games should not have a hidden catalog-mutation side effect.

Test05 isolates the next question:

> Can the stock User Menu safely expose an explicit fourth `REFRESH` command?

Test05 performs **no catalog writes**.

## Protected firmware input

Exact Audio OSD v8 golden baseline:

```text
ZIP SHA-256
ba3dad99471c6144fd8f6e9f5891bc88d44b955c5de8a21df905d0d396cdb83a

firmware SHA-256
4b8f7af994d16371a2664a3d46c983e52ffd1aefbebc5b5a4a9ae63dc6cbe954
```

The Test04 golden is preserved independently and is not modified.

## Stock User Menu geometry recovered

The stock setup screen is a 640x480 RGB565 bitmap with three 159x159 menu cards.

The dynamic selection cursor remains a stock 172x172 overlay.

The selector renderer loads the current User Menu selection and originally computes:

```text
x = 52 + 186 * selection
y = 151
```

Therefore simply widening the valid selection from `0..2` to `0..3` would place selection 3 off-screen.

## Test05 layout

The six localized User Menu bitmaps are rearranged into a 2x2 grid:

```text
User Games     Language
TV System      REFRESH
```

The selector remains 172x172 and is placed using:

```text
x = 100 + 256 * (selection & 1)
y =  20 + 224 * ((selection & 2) / 2)
```

Selector coordinates:

```text
0 -> (100,  20)
1 -> (356,  20)
2 -> (100, 244)
3 -> (356, 244)
```

Existing three labels are moved using their OEM localized raster glyphs. The fourth Test05 label is intentionally universal ASCII `REFRESH` in all six languages; localization of the new command is polish, not part of this gate.

## Navigation bounds

Stock wrap limit:

```text
0..2
```

Test05:

```text
0..3
```

Patched anchors:

```text
0x80359aa4  up-wrap terminal value 2 -> 3
0x80359e60  forward/down terminal value 2 -> 3
```

Navigation remains the existing linear selector for this proof. True 2D directional semantics are deliberately deferred so Test05 changes only the minimum necessary surface.

## Selector-render patch

Original coordinate math begins at:

```text
0x80359b1c
```

Eight existing instructions are replaced with deterministic 2x2 coordinate math.

The original sequence also loaded `t9=172` for the cursor dimensions. Because those instruction slots are now coordinate math, Test05 explicitly uses the still-live `a3=172` value for the two 172px dimension arguments:

```text
0x80359b4c  sw a3,20(sp)
0x80359b64  sw a3,16(sp)
```

This was caught before candidate packaging.

## Explicit row-3 dispatch

Rows 0 and 1 remain handled by untouched stock branches.

The original row-2/fallback branch at:

```text
0x80359ea8
```

is redirected into the already-proven deep safe cave:

```text
0x807dab98..0x807dbb9f
```

Test05 stub behavior:

```text
selection 2 -> exact stock TV System path 0x80359eb0
selection 3 -> mark User Menu dirty and redraw; NO FILE I/O
other       -> original fallback 0x80356bfc
```

Stub:

```text
56 bytes
SHA-256 23d57760e7b249802d2e1b97069a820d92a4494c6b87570160d3f45377b0fd2d
```

## Private UI-source provenance

The setup bitmaps are proprietary stock resources and are not committed to the public research repository.

Private source bundle:

```text
setup-ui-stock-source.zip
313,765 bytes
SHA-256 16d4ee25357d725ddc574c86b69f5b570c73deb83dab8f2b98056ed31ab37843
```

It contains only:

```text
qasf.bel
dxkgi.ctp
itiss.ers
esent.bvs
awusa.tax
vssvc.nec
vidca.bvs
```

The public deterministic builder asserts every source member hash.

## Deterministic candidate expectations

Local deterministic composition against the exact protected firmware bytes produced:

```text
candidate firmware SHA-256
30de1ecc9819f0e669a872cd642e23098506a6411f2ce0de74b4dedfc1a0ae21

candidate ZIP size
4,908,988 bytes

candidate ZIP SHA-256
766071faec548b04deffef4e97ba900c965aa09686a05195d6bbda997b7961a4
```

Modified setup bitmap hashes:

```text
dxkgi.ctp 97f97a7210ba2ed798b24d8f304d76592f496a84297c7f81253d7b9f3b4f029a
itiss.ers e5fa0f4fddf0bae698c063431aba28e0ecd7a37d639044275a302d06b5dd53de
esent.bvs 2b6bf9af415ffead889128d74728213d55ded17f4b57f4c048690bb4a3f8103a
awusa.tax  6c1d67cf609bcd82bc7ea97e1be2957a00a4f4a129a14857eff12830c92f41e4
vssvc.nec  21e22fb196716f6cd294f33f90307932a132d80160ec6125cae400ba4ad755ad
vidca.bvs  066b856062498489f275c2c41dfdead6967153ded267ffdec4b0e0086752c637
```

The private-vault build must reproduce these values before hardware use.

## Hardware gate

1. Open User Menu and confirm all four options are visible in a 2x2 layout.
2. Navigate repeatedly both directions; verify clean `0 <-> 3` wrap and no off-screen/corrupt cursor.
3. User Games retains normal stock behavior.
4. Language retains normal stock behavior.
5. TV System retains normal stock behavior.
6. Selecting REFRESH repeatedly stays on User Menu and performs no catalog mutation.
7. SFC/game-list count remains whatever it was before Test05.
8. Reboot and repeat navigation.

No Test05 candidate may be promoted to `golden/` until hardware passes.

## Reproducer

`tools/game_lists/build_test05_explicit_refresh_menu.py`


## Private-vault composition complete — exact hardware candidate ready

The Test05 private-vault composition completed successfully on 2026-09-07 from the exact protected Audio OSD v8 baseline plus a freshly reconstructed compact source bundle containing the seven hash-asserted stock setup resources.

Verified compact UI source bundle:

```text
setup-ui-stock-source-new.tar.xz
size 94,664 bytes
SHA-256 6a1264b9ebf49f4bb28f2185168ca400fbc883a9bacfde6874796baaf813701c
```

All seven source member hashes matched the deterministic builder's stock-resource assertions. The previously interrupted `staging/test05-ui-source-20260907/` transfer was not reused.

Exact Test05 hardware candidate:

```text
xgo-game-list-test05-explicit-refresh-menu.zip
size 4,908,988 bytes
SHA-256 766071faec548b04deffef4e97ba900c965aa09686a05195d6bbda997b7961a4
firmware SHA-256 30de1ecc9819f0e669a872cd642e23098506a6411f2ce0de74b4dedfc1a0ae21
stub SHA-256 23d57760e7b249802d2e1b97069a820d92a4494c6b87570160d3f45377b0fd2d
```

The private CI gate reproduced every expected modified bitmap hash, exact candidate size/hash, exact firmware hash, and passed `unzip -t`. The candidate is archived at the private-vault root (binary archive commit `ea4faae`) and exposed as a CI artifact for hardware retrieval. It is **not golden** pending hardware confirmation.

Next action: hardware Test05 only. Do not attach the Test04 writer yet. The gate is the explicit four-option UI, navigation, preservation of the original three menu actions, and harmless REFRESH stub behavior with no catalog mutation.
