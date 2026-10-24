#!/usr/bin/env python3
"""Preserve the pre-SPSC passive phantom-JUMP evidence, without overclaiming.

P3 had no active DATA sink but produced spontaneous JUMP on physical XGO.
Cross-compare static native PHY initialization against the latest responder.
This is HW history + SRC equivalence for the override register, NOT a
measured RC delay or proof of cable-equivalent electrical behavior.
"""
from pathlib import Path
import re
import unittest

P3 = Path("tools/rp2040-xgo-p3-usbphy/main.c")
TRIAL = Path("integrations/gp2040ce-xgo-test01/candidates/offline-test44-spsc-xy-native-turbo-hold/XGODriver.cpp")
HW = Path("experiments/rp2040-usbphy-p3-passive.md")


def override_flags(source):
    m = re.search(r"usb_hw->phy_direct_override\s*=\s*([^;]+);", source)
    assert m, "Direct PHY override initialization missing"
    return frozenset(re.findall(r"USB_USBPHY_DIRECT_OVERRIDE_[A-Z_]+_BITS", m[1]))


class TestPassiveJumpBaseline(unittest.TestCase):
    def test_passive_hardware_witness_did_not_serialize_button_bits(self):
        p3 = P3.read_text()
        history = HW.read_text()
        self.assertIn("Player 2 intermittently performs JUMP without user input.", history)
        self.assertIn("P3 native-USB-PHY passive probe", history)
        self.assertNotIn("data_sink(", p3)
        self.assertIn("uclr->phy_direct=USB_USBPHY_DIRECT_TX_DP_OE_BITS|USB_USBPHY_DIRECT_TX_DM_OE_BITS;", p3)

    def test_static_phy_override_flags_match_active_responder(self):
        p3 = P3.read_text()
        trial = TRIAL.read_text()
        flags = override_flags(p3)
        self.assertEqual(len(flags), 10)
        self.assertEqual(flags, override_flags(trial))
        for source in (p3, trial):
            self.assertRegex(source, r"usb_hw->main_ctrl\s*=\s*0;")
            self.assertRegex(source, r"usb_hw->sie_ctrl\s*=\s*0;")
            self.assertRegex(source, r"usb_hw->phy_direct\s*=\s*0;")
            self.assertIn("USB_USB_MUXING_TO_PHY_BITS", source)
            self.assertIn("USB_USB_MUXING_SOFTCON_BITS", source)

    def test_active_candidate_does_not_force_data_high(self):
        source = TRIAL.read_text()
        self.assertIn("inline void data_release() { clear_alias->phy_direct = USB_USBPHY_DIRECT_TX_DP_OE_BITS; }", source)
        self.assertIn("inline void data_sink() { set_alias->phy_direct = USB_USBPHY_DIRECT_TX_DP_OE_BITS; }", source)
        self.assertIn("data_release();\n}", source)
        # No source assertion establishes which electrical loading occurs
        # in the ordinary P3 cable versus the special Frankie controller cable.

    def test_cables_are_documented_as_different(self):
        history = HW.read_text()
        live = Path("tools/rp2040-xgo-live-controller/README.md").read_text()
        self.assertIn("ordinary micro-USB cable", history)
        self.assertIn("Frankie V2 Jr", live)
        self.assertIn("2 and 4 share WHITE", live)


if __name__ == "__main__":
    unittest.main(verbosity=2)
