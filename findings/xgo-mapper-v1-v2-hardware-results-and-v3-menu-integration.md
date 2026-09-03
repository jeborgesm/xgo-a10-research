# XGO mapper v1/v2 hardware results and v3 menu integration

Status: **V1 ARBITRARY SIX-BUTTON REMAPPING HARDWARE-CONFIRMED; V2 EXIT REGRESSION; V3 MENU INTEGRATION REQUIRED**

## Hardware-confirmed mapper core

Hardware testing of v1 proved that the injected mapper can change arbitrary six-button mappings rather than only the original hard-coded A->B proof. In particular, the user successfully changed A->B and B->A from the interactive mapper.

Therefore the following are hardware-confirmed:

- hidden page-4 hook executes safely from the `0x800014a0` cave;
- interactive source selection works;
- interactive logical-target selection works;
- the six-record source addressing is functional;
- the logical encode table is functional for the six standard targets;
- runtime application of an arbitrary changed record is functional;
- the corrected stock writer/persistence architecture remains the valid commit path.

The remaining problems are interaction and renderer integration, not the keymap ABI.

## V1 hardware UX findings

The user reported:

- arbitrary A/B remapping worked;
- the mapper text was overlaid with the stock pause-menu `QUIT`, `LOAD`, and `SAVE` labels;
- moving the yellow markers appeared to affect the mapper state without useful save feedback;
- pressing the intended Start action did not behave as expected;
- an L-button event unexpectedly provided a route out of the mapper.

The important correction is that individual auxiliary button event identities must not be assigned from inference. The stock firmware proves the existing Start+Select entry chord as a combined raw state, but does not by itself prove the names of every standalone event value used by the injected mapper.

## V2 hardware regression

V2 attempted to avoid the uncertain standalone event identities by using the raw Start+Select chord as the commit action and by replacing the mapper resource with an opaque screen.

Hardware result:

- the mapper remained enterable;
- no tested control, including Start and Start+Select, exited the mapper;
- the stock `QUIT`, `LOAD`, and `SAVE` labels still rendered over the mapper screen.

Therefore v2 introduced an exit/commit regression and proved that the stock pause labels are rendered *after* or independently of the `gpapi.bvs` page image. Replacing the page bitmap alone cannot suppress them.

## Renderer evidence

Static inspection of `0x80354640` confirms that the pause renderer performs generic drawing after loading the selected page resource. The section beginning around `0x80354710` initializes a count of three and renders three vertically separated generic entries. This corresponds to the persistent three-item pause-menu presentation seen in hardware.

This explains why an opaque replacement `gpapi.bvs` did not remove the `QUIT / LOAD / SAVE` text: those labels are not simply pixels in `gpapi.bvs`.

## V3 architecture: real MAPPER menu item

The next mapper should stop treating page 4 as a hidden/ghost page. Instead, integrate the mapper as a real fourth pause-menu item below the existing three items:

```text
QUIT
LOAD
SAVE
MAPPER
```

The desired state machine is:

```text
normal pause menu
  -> DOWN selects MAPPER
  -> explicit confirm enters dedicated mapper editor

mapper editor
  -> arrows modify staged mappings with visible feedback
  -> save action commits all staged records
  -> stock writer persists `.kmp`
  -> resume game immediately
```

Key requirements:

1. `MAPPER` must be part of the normal pause-menu list, not a ghost fifth page reached only by overflowing page navigation.
2. Entering/selecting `MAPPER` must not itself alter any keymap record.
3. The dedicated mapper screen must not receive the normal `QUIT / LOAD / SAVE` overlay.
4. Selection changes remain staged until explicit commit.
5. Commit must use an input event whose physical identity is hardware-proven; do not infer standalone Start/Select identities.
6. Commit must enter the already hardware-proven writer/resume path.
7. The mapper screen should use a fully opaque dedicated background and large visible source/target state.

The v2 build should not be used as the basis for further hardware mapping tests except as a historical regression artifact. Preserve the v1 mapping core, then rework menu entry/rendering/commit around the stock pause-menu architecture.