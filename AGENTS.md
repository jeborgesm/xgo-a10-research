# XGO Archaeology — repository instructions for every future assistant

## NON-NEGOTIABLE: GP2040-CE is a transparent physical controller

Before touching RP2040/GP2040-CE XGO controller firmware, read
`integrations/gp2040ce-xgo-test01/CONTROLLER-TRANSPARENCY-CONTRACT.md`
and `integrations/gp2040ce-xgo-test01/HANDOFF-CURRENT.md`.

**User-established invariant:** GP2040-CE reports actual physical pressed,
held and released states. It does **not** manufacture attack pulses, shorten
physical holds, synthesize turbo, or interpret any button differently because
of the game or emulator. The XGO owns all turbo/repeat, logical-game mapping,
and game-specific behavior. This applies to **all** face/shoulder buttons and
all games, not only X/Y or Contra.

Do not repeat the historical mistake of applying an 18ms one-shot pulse to
R/L/A/B while exempting X/Y. **Test44 and its SPSC/X-Y derived firmware
are historical test baselines, NOT correct controller-semantic designs.**
A green serial, SRAM or linked ELF test does not override this invariant.

For future candidate releases: demonstrate physical hold over many host scans,
release on the next sampled host scan, exact mapping of all twelve wire bits,
no game-dependent output logic, and no firmware-level turbo/pulse rewriter.
Run `python3 integrations/gp2040ce-xgo-test01/tests/test_controller_transparency_contract.py --candidate PATH`
as an initial *static* gate and follow it with dynamic host simulation and
full linked RP2040 audit. Do not distribute a candidate if this gate fails.

Preserve Test44 recovery UF2, Frankie V2 Jr wiring, and XGO `bisrv.asd`.
Historical hardware findings and their HW/BIN/SRC/MODEL/OPEN distinctions
remain valid evidence, not permission to override the invariant.
