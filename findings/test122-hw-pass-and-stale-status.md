# Test122 HW result — native Setup selector suppression

Date: 2026-09-21
Status: **HW PASS with one bounded residual status-message artifact**

## Candidate identity

Derived from exact HW-proven Test119.

Firmware SHA-256:
`6378e4a9cbf560afa53c38836826c294c9b2316310d65eb9860894c221cb2f0d`

LCFG CRC-32/MPEG-2:
`0x0EFF6110`

Candidate ZIP SHA-256:
`21c3b9e6c871e67d85e334154b7157e12597f918911a76acc5932faa0647c78d`

Source:
`tools/refresh_selector/build_test122_from_test119.py`

## Hardware result

User report:
- successful test;
- REFRESH GAMES remains responsive;
- underlying blue Setup selector borders are gone;
- B closes REFRESH GAMES correctly;
- rest of expected behavior works.

This promotes the producer-side suppression mechanism to **HW**:
- state-14 native 172x172 compositor at `0x80353250` is the source of the unwanted underlying selector;
- conditionally bypassing only `0x80359B3C..0x80359B64` while `selector_active != 0` is safe on hardware;
- Test119 lifecycle/input/overlay can remain intact.

## Residual artifact — OPEN

When the selector is closed with B, `No New Games` is displayed on ordinary Setup and remains visible until another Setup option is selected.

Important constraints:
- B itself performs no Refresh operation;
- therefore the message is stale/persistent status state being rendered after the selector closes, not evidence that B executed a scan;
- do not clear it by arbitrary text painting;
- trace the preserved Refresh status owner/draw path and clear/expiry contract before changing firmware.

The visual blue-border problem is closed. Status cleanup is the next bounded investigation.
