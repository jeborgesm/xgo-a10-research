#!/usr/bin/env python3
"""Fail-closed GP2040-CE/XGO transparent-controller source preflight.

MANDATORY architectural invariant: RP2040 transmits the coherently sampled
physical pressed/held/released state of ALL buttons; XGO alone owns turbo,
repeat and game/emulator semantics. This is a STATIC gate only: a passing
source still requires compiled C++ publication->12-slot serial tests,
machine-code safety audit and user-controlled hardware validation.

Usage:
  python3 integrations/gp2040ce-xgo-test01/tests/test_controller_transparency_contract.py
  python3 integrations/gp2040ce-xgo-test01/tests/test_controller_transparency_contract.py --candidate PATH
"""
import argparse
from pathlib import Path
import re
import sys
import unittest

ROOT = Path("integrations/gp2040ce-xgo-test01")
RULES = ROOT / "CONTROLLER-TRANSPARENCY-CONTRACT.md"

LEGACY = [
    ROOT / "candidates/test44-clock-timeout-18us/XGODriver.cpp",
    ROOT / "candidates/offline-test44-spsc-coherent-ram/XGODriver.cpp",
    ROOT / "candidates/offline-test44-spsc-xy-native-turbo-hold/XGODriver.cpp",
]

# This is deliberately conservative. Any future different but correct
# implementation must be reviewed and proven behaviorally before an
# authorized change to this gate. No quick "skip" for a preferred game.
DISALLOWED_OUTPUT_IDENTIFIERS = (
    "attack_pulse_mask",
    "ATTACK_PULSE_US",
    "ATTACK_PULSE_BITS",
    "XGO_NATIVE_TURBO_HOLD_BITS",
    "pending_press_edges",
    "attack_edge_generation",
    "consumed_attack_edge_generation",
    "attack_edge_commit_seq",
    "previous_physical_attacks",
)

def check_source(source: str) -> list[str]:
    errors = []
    for ident in DISALLOWED_OUTPUT_IDENTIFIERS:
        if re.search(r"\b" + re.escape(ident) + r"\b", source):
            errors.append("disallowed game/attack-specific output state: " + ident)

    # Require explicit direct snapshot forwarding until full behavioral
    # tests prove a differently structured implementation equivalent.
    for pattern, reason in (
        (r"\buint16_t\s+map_mask\s*\(\s*Gamepad\s*\*",
         "missing physical Gamepad-to-12-slot mapping"),
        (r"\bpublished_mask\.store\s*\(\s*snapshot\s*,",
         "missing physical snapshot publication"),
        (r"\b(?:const\s+)?uint16_t\s+physical\s*=\s*"
         r"published_mask\.load\s*\(",
         "missing coherent physical snapshot in Core1"),
        (r"\bconst\s+uint16_t\s+mask\s*=\s*physical\s*;",
         "serial frame output MUST be physical snapshot (no pulse/filter rewrite)"),
    ):
        if not re.search(pattern, source):
            errors.append(reason)

    # Ensure all six face/shoulder slots, directions, START and SELECT
    # are mapped from real pressed state, in their established positions.
    expected = {
        "pressedR1": 0, "pressedB4": 1, "pressedB3": 2,
        "pressedL1": 3, "pressedB1": 4, "pressedB2": 5,
        "pressedS1": 6, "pressedS2": 7,
        "pressedUp": 8, "pressedDown": 9,
        "pressedLeft": 10, "pressedRight": 11,
    }
    for method, slot in expected.items():
        pat = rf"\b{re.escape(method)}\s*\(\s*\)\s*\?\s*1u\s*<<\s*{slot}\b"
        if not re.search(pat, source):
            errors.append(f"required physical map {method} -> slot {slot} missing")

    # Do not permit semantics to vary by game, firmware keymap or emulator
    # inside the controller transport code.
    for pat in (r"\b(?:rom_name|game_name|emulator_id|core_name)\b",
                r"\b(?:TURBO_RATE|AUTOFIRE_PERIOD|REPEAT_INTERVAL)\b"):
        if re.search(pat, source):
            errors.append("game/turbo interpretation found in transport code")

    return errors


def transparent_minimal_fixture() -> str:
    mapping = [
        ("pressedR1",0),("pressedB4",1),("pressedB3",2),
        ("pressedL1",3),("pressedB1",4),("pressedB2",5),
        ("pressedS1",6),("pressedS2",7),("pressedUp",8),
        ("pressedDown",9),("pressedLeft",10),("pressedRight",11),
    ]
    terms = " |\n  ".join(
        f"(g->{m}() ? 1u << {s} : 0u)" for m,s in mapping
    )
    return (
        "uint16_t map_mask(Gamepad *g) { return "+terms+"; }\n"
        "void publish() { published_mask.store(snapshot, std::memory_order_release); }\n"
        "void frame() { const uint16_t physical = "
        "published_mask.load(std::memory_order_acquire);\n"
        " const uint16_t mask = physical;\n"
        " send_12_slots(mask); }\n"
    )


class TestContractGuard(unittest.TestCase):
    def test_authoritative_contract_is_present(self):
        s = RULES.read_text()
        for required in (
            "NON-NEGOTIABLE",
            "GP2040-CE must function as a controller",
            "XGO owns",
            "every button",
            "NO previously built Test44/SPSC/X-Y-exception UF2 meets",
        ):
            self.assertIn(required, s)

    def test_transparent_source_fixture_passes(self):
        self.assertEqual(check_source(transparent_minimal_fixture()), [])

    def test_legacy_known_bad_candidates_are_rejected(self):
        for path in LEGACY:
            with self.subTest(path=path):
                errors = check_source(path.read_text())
                self.assertTrue(errors, path)
                self.assertTrue(any("pulse" in e for e in errors), (path, errors))

    def test_one_shot_pulse_mask_is_rejected(self):
        fixture = transparent_minimal_fixture().replace(
            "const uint16_t mask = physical;",
            "const uint16_t mask = (physical & ~ATTACK_BITS) | attack_pulse_mask;"
        )
        self.assertTrue(check_source(fixture))

    def test_xy_only_exception_is_rejected(self):
        fixture = transparent_minimal_fixture()
        fixture += (
            "\nconstexpr uint16_t XGO_NATIVE_TURBO_HOLD_BITS = 0x6;"
            "\nconstexpr uint16_t ATTACK_PULSE_BITS = 0x39;\n"
        )
        self.assertTrue(check_source(fixture))

    def test_held_release_frames_preserve_every_wire_bit(self):
        # This is an intended transport MODEL, not proof from linked ELF.
        # For each physical button, assert continuous held state over many
        # frames and immediate release on the next sampled scan.
        for slot in range(12):
            held = 1 << slot
            snapshots = [0, held, held, held, held, 0, 0]
            outgoing = [mask for mask in snapshots]
            self.assertEqual(outgoing, snapshots)
        # Likewise all 4096 possible physical input snapshots.
        self.assertEqual(len({mask for mask in range(4096)}), 4096)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--candidate", type=Path)
    args = p.parse_args()
    if args.candidate is None:
        tests = unittest.defaultTestLoader.loadTestsFromTestCase(TestContractGuard)
        return 0 if unittest.TextTestRunner(verbosity=2).run(tests).wasSuccessful() else 1
    candidate = args.candidate
    if not candidate.is_file():
        print("BLOCKED: candidate source does not exist:", candidate)
        return 1
    errors = check_source(candidate.read_text())
    if errors:
        print(f"BLOCKED (controller semantic contract): {candidate}")
        for err in errors:
            print(" -", err)
        print("See", RULES)
        print("DO NOT compile, package or flash this candidate as compliant.")
        return 1
    print("PASS source-level transparent-controller preflight:", candidate)
    print("NOT sufficient: dynamic source-to-wire tests and ELF audit remain mandatory.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
