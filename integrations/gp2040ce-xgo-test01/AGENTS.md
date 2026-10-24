# Mandatory GP2040-CE / XGO controller contract

**STOP and read `CONTROLLER-TRANSPARENCY-CONTRACT.md` before changes.**

The user explicitly designated this as an **unbreakable project rule** on
2026-10-24:

> GP2040-CE must function as a controller, not as an emulator-specific input
> interpreter. When a button is pressed it reports pressed, while held it
> reports held, and after release it reports released. XGO alone decides
> whether that means one punch, turbo, continuous shooting, repeated jumping,
> or any other game behavior.

Applies to **all** buttons and console cores (Street Fighter II is an
important counterexample to NES-derived policy). No attack button may have
its hold artificially ended by the RP2040. No special-casing X/Y. No 18ms
pulse-on-press output. No game-aware or host-turbo-aware logic in firmware.
Controller-to-wire mapping and microsecond electrical serialization are
transport concerns; host interpretation is not.

**Current named candidates are NONCOMPLIANT:** Test44, coherent-SPSC,
and the X/Y-only fix all still artificially pulse at least one attack button.
Keep as evidence/rollback only; DO NOT present as correct final architecture.

Use `tests/test_controller_transparency_contract.py --candidate PATH` to
fail closed on known violations before compiling. Static screening alone is
not runtime/hardware proof; verify all button holds/release transitions
through complete GP2040 `process` and XGO serial simulation for any new
candidate. Never trade accurate held input for short-tap responsiveness.
