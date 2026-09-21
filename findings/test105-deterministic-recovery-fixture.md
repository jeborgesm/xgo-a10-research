# Test105 deterministic recovery fixture

Status: OFFLINE FIXTURE CONSTRUCTED. Intended for one controlled HW recovery invocation; no deliberate power interruption.

Fixture ZIP SHA-256:
a9e41aa3771da3d89426cced7beb20d5bec28f76439f5052ea7e11f5b98827d7

Base:
- exact Test105 hardware candidate

Added only:
- MD/art/.xgo-cat-tax.bak
- MD/art/.xgo-cat-nec.bak
- MD/art/.xgo-cat-bvs.bak

Recovery generation is the coherent known-good 788-entry MD triplet:
- TAX 22156 bytes SHA d04479d8214233d417ebf1791aa38b030a89b9ee55657c586c997257301bba01
- NEC 15984 bytes SHA 835be147cfb05da648385667da6ad5c81467a281ecfa8f71d60bf50d01d8197c
- BVS 8160 bytes SHA 60acca83cbcd3086a1f27c2f9c2f192474759d1711f0adf8c9b9e3419a3bf1a8

Purpose:
Simulate the durable recovery sentinel that would exist after OLD generation was safely backed up but before transaction cleanup. Current live Resources are left untouched by the package. On the next Refresh, recovery preflight should detect the complete backup triplet, validate it, restore that generation to LIVE, byte-verify restoration, remove the recovery triplet, then continue normal catalog processing.

This is safer than intentionally interrupting a real SD write.

Interpretation:
- responsive normal result followed by healthy MD frontend = recovery preflight executed without destabilizing the device;
- because the ROM set still contains the newer games, the normal catalog pass may immediately rebuild the newer catalog after restoring 788. Therefore the final visible count need not remain 788; the fixture tests recovery mechanics, not permanent downgrade.
- freeze/reboot/Refresh Failed = stop; do not retry.

No firmware changes. No live Resources replacements are included in the fixture itself.
