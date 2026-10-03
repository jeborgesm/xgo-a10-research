# Test C candidate — L15-gated internal-speaker mono fold

Date: 2026-10-02
Branch: `research-audio-mono-routing`
Status: **AUDITED HW CANDIDATE**

## Parent
Exact HW-PASS Test A firmware:
`060093e8fd2a3fa559c9b43e207c4bb495de82e87519b672a799d19b304b20b7`

## Closed polarity [BIN]
At `0x8035C734` stock reads GPIO_L_INPUT. It extracts bit 15 and at `0x8035C760` branches to the TV block when the bit is zero. Nonzero follows the LCD block. The same bit is cached at GP-30360.

Thus:
- L15=1: LCD/internal mode
- L15=0: TV/AV mode

## HW basis
Channel-isolation probes proved FBA gameplay is audible from digital channel 0/left on the built-in speaker; right-only FBA gameplay was silent.

## Candidate policy
At the existing pre-ring callback seam:
- L15=1: `L'=(L>>1)+(R>>1); R'=R`
- L15=0: preserve `L,R` unchanged.

This exactly follows the maintained-family single-speaker fold shape in internal mode while deliberately preserving stock stereo-shaped PCM in TV/AV mode.

## Patch surface
- callback call site `0x8035E800`: redirect to shim
- verified zero padding `0x807DBB08..0x807DBB3F`: 56-byte leaf/tail shim
- LCFG CRC field only

No rate, scheduler, FBA producer quantum, ring geometry, queue threshold, volume, Audio OSD, SNES or Refresh change.

Source:
`tools/audio/build_mono_internal_l15.py`

## Exact candidate
Firmware SHA-256:
`f5e2a91dced95b60ab7988952ea3a7aa1c2460c97b3644e2ea815b77b58d07aa`

LCFG CRC-32/MPEG-2:
`0x5C4C610F`

ZIP SHA-256:
`a654cff6973bafa889f08aa4d0313f89f46d2ee2bdd483269a55d84ecb316d38`

## HW question
With no AV cable, do SFII and Cadillacs retain normal audio with right-channel information now folded into the audible internal channel, without crackle/distortion/regression?

If convenient, inserting the AV cable is a secondary check: TV/AV mode should bypass the fold and preserve original L/R transport.
