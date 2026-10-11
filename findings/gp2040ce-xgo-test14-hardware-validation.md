# Test14 — hardware validation checkpoint

Date: 2026-10-10
Branch: `research-gp2040ce-xgo-integration`
Firmware build: [GitHub Actions run 38098786893](https://github.com/jeborgesm/xgo-a10-research/actions/runs/38098786893)
Build commit: `fb911825123f07ea8fe12e4bdf881583a76de146`
Artifact: `xgo-gp2040ce-test14-UNTESTED` (artifact ID 11687143460; name reflects build-time status, not later hardware result)

## HW — user-reported observations

User tested the Test14 firmware and reported:

> "That one is good, booted showed the inputs (xbox style) no rapid fire or mixed. I like it! :D"

Interpretation limited to what was reported:
- **HW PASS:** device booted
- **HW PASS:** OLED showed button inputs using Xbox-style labels
- **HW PASS:** no unwanted rapid-fire behavior observed during user's test
- **HW PASS:** no mixed-button behavior observed during user's test
- **HW PASS (implicit):** XGO recognized inputs in the user's gameplay test

## SRC — implemented change

- Core 1 runs the XGO USB-PHY direct serial responder continuously.
- Core 0 maps GP2040-CE gamepad state and publishes an atomic 12-bit button snapshot.
- GP2040-CE auxiliary add-ons (including OLED) run cooperatively on Core 0 for XGO mode.
- Other input modes retain their existing Core 1 auxiliary scheduling.

## INF — interpretation and limits

This is the first reported hardware success of the isolated-responder design and supports the hypothesis that the earlier Test13 failure involved responder scheduling interference. It does not prove OLED was the sole cause, or that all input sequences, long-duration stability, Web Config, configuration saves, USB-host functions, or non-XGO modes are regression-free.

## Protection and next steps

**Protect Test14 as the new XGO hardware-proven gameplay baseline.** Preserve the exact artifact and SHA; do not overwrite or casually change it. Retain Test10 as earlier playable rollback.

Follow-up validation before merge/release:
1. Long held Start/punch/direction and simultaneous combinations.
2. Prolonged gameplay with OLED and Input History enabled.
3. Web Config entry, settings save, reboot and recovery; review Core 1 flash-lockout implications.
4. Other input modes and auxiliary peripherals, as applicable.
5. Confirm clean rollback and recoverability.

No additional firmware modification is implied by this hardware checkpoint.
