# Controller acceptance contract — one action per press (2026-10-15)

## User-defined requirement (authoritative)

> the correct behavior is to do the action as soon as the button is detected pressed. then do anything uinilt it is detected going from unpressed to pressed again. that is what i expect. don't come back saying that the game does something ewhen holding a button because it should not.

Interpret typo 'then do anything' in context as **then do nothing** until the next unpressed-to-pressed transition.

## Required observable behavior for each of six attacks

1. **Unpressed -> pressed:** exactly one immediate action.
2. **Held pressed:** no further action, irrespective of duration.
3. **Pressed -> unpressed:** re-arm, no attack.
4. **Next unpressed -> pressed:** exactly one new action.
5. No substitutions or mixed attacks: the physical button must never generate another attack identity.
6. Multi-button presses should not invent extra transitions.

This is a behavioral contract, **not proof that a particular pulse-width or host sampling method implements it**. Firmware candidate must ensure the host observes one valid press event and a release while the physical button remains held, with re-arming only after a physical release. A one-frame pulse may be missed if the host does not scan during that frame; the implementation must account for host polling/handshake and latency before hardware testing.

## Hardware status

Test28 is protected because HK behaves correctly (single action on hold) and HK taps register. Tests29/30/31 failed to solve punch mixing; Test31 also caused unwanted HK hold repeat. Do not attribute repeated attacks to acceptable game hold behavior. All modifications must remain GP2040-CE controller-side; no XGO BIOS, emulator, game mapping, or turbo changes.
