# XGO A10 / GP2040-CE — NON-NEGOTIABLE controller transparency contract

**Effective: 2026-10-24. Authority: explicit user design decision.**
**Status: binding architecture requirement for all future RP2040/controller work.**

## Invariant — exact intended behavior

> **GP2040-CE must function as a controller, not as an emulator-specific input interpreter.**
>
> **When a physical button is pressed, report it as pressed. While it is held,
> keep reporting pressed. When it is released, report released.**
>
> **The XGO decides whether that input means a single punch, continuous
> shooting, repeated jumping, turbo, or any other emulator/game action.**

This rule applies to **every button** (X, Y, L, R, A, B, directions,
SELECT, START, and any supported controller inputs) across **every** XGO
frontend and emulator. Never special-case particular attack buttons based
on their roles in a ROM or XGO default keymap.

### Ownership boundary

- **GP2040-CE owns:** acquiring the *real physical* Gamepad pressed state,
  maintaining a defined physical-to-wire-bit mapping, safely publishing a
  coherent snapshot, and serializing the current state on the 12-slot XGO
  synchronous DATA/CLOCK protocol.
- **XGO owns:** logical-game keymaps (embedded and per-ROM `.kmp`), turbo
  generation, repeat rate, attack semantics, gameplay action, auto-fire,
  and how a game treats an extended button hold.
- **Never in GP2040-CE XGO transport:** synthetic turbo cadence, fixed
  attack pulse windows, fabricated releases, conditional no-repeat rules,
  cross-game behavior heuristics, remapping by emulator, or distinctions
  such as "X/Y held but R/L/A/B pulse".

**Formal target at each host scan:** for each physical input `b`, the
corresponding transmitted bit equals the last coherently sampled input
state of `b`. Repeated scans while held continue to assert the bit. Once
release is sampled, subsequent transmissions release the bit. This is the
protocol-level target, subject only to real input-scan/synchronization
latency and host scan timing; no emulated game meaning participates.

### Short taps vs genuine holds

An actual physical tap shorter than the Core0 sampling or host scan interval
may require separate investigation. **That cannot justify rewriting held
button states into bounded pulses.** Any proposed capture/reconciliation
mechanism must preserve real holds/releases unchanged, be justified by
observed timing, and receive review before implementation. Do not silently
introduce a game- or button-specific workaround.

### Historical mistake — do not repeat

Original protected Test44:
```cpp
constexpr uint16_t ATTACK_BITS = 0x003fu;
const uint16_t attacks = snapshot & ATTACK_BITS;
const uint16_t mask = (physical & ~ATTACK_BITS) | attack_pulse_mask;
```

All six attack inputs were forwarded as ~18ms edge pulses, not actual held
levels. The coherent-SPSC prototype kept this behavior. The subsequently
issued X/Y-only firmware attempted to fix XGO's native NES turbo by exempting
X and Y while **continuing to truncate R/L/A/B**, which was an incorrect
architectural exception. Both forms violate this contract even when serial
timing tests, SRAM compilation, and host simulations pass.

**Street Fighter II hardware observation:** holding X or Y led to super-fast
LP/MP, whereas other attacks appeared once. That result cannot be used to
infer that XGO treats X/Y specially in Street Fighter: the controller had
*forced the other four attack signals to end after 18ms*. The XGO's own
keymap/turbo logic must be evaluated from transparent input, not from our
contaminated output.

**Contra hardware observation:** unexpected jumps persist despite SRAM/SPSC
work. This is an independent OPEN failure; do not hide it with remapping,
pulse suppression, X/Y exceptions, or an invented controller turbo policy.

### Mandatory future acceptance

A new candidate is eligible for firmware packaging only after:

1. **Source contract:** no XGO game behavior, repeat/turbo synthesis, fixed
   attack pulse mask, button-specific hold rewriting or emulator lookup.
   Map actual Core0 state to **all 12** stable wire slots.
2. **Dynamic contract:** drive each attack individually held for many scan
   periods, then release, and check the *actual transmitted* wire mask;
   test short taps, simultaneous multi-button holds, pressed/released
   sequences, D-pad and START/SELECT. Full mask-space must not fabricate
   buttons. Verify entire Core0 publication and Core1 serialization, not
   merely extracted `emit_frame()`.
3. **Serial/electrical contract:** independent XGO CLOCK model, nominal
   12-bit phase and slot0 boundary, recovery after aborted transactions,
   and linked SRAM/IRQ audit; preserve Test44 rollback and Frankie wiring.
4. **Hardware acceptance:** verify expected controller responsiveness with
   Street Fighter II and Contra **without asserting that turbo is owned by
   GP2040-CE**. Independently report existing unwanted Contra jump.
5. **Gate:** run
   `python3 integrations/gp2040ce-xgo-test01/tests/test_controller_transparency_contract.py --candidate <candidate-XGODriver.cpp>`.
   This is a narrow static preflight, **not** a proof of correctness. The
   dynamic behavioral checks above are still mandatory.

**Current result:** NO previously built Test44/SPSC/X-Y-exception UF2 meets
this contract. Keep their historical test results and Test44 rescue binary
but never label their protocol semantics approved. No new transparent
controller firmware has yet been validated.

Only an explicit subsequent user decision may amend this invariant.
