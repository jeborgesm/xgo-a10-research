#!/usr/bin/env python3
"""Polish03 source gate: only RP2040 internal *DP DATA* Rpu2 is enabled.

No external resistor, no XGO/GOLD edits, no game-specific buttons, no
DM/CLOCK pull-up, no active HIGH. A passing gate does not prove XGO
electrical tolerances or actual ghost suppression until owner hardware test.
"""
from pathlib import Path
import re
import unittest

ROOT=Path("integrations/gp2040ce-xgo-test01")
PRE=ROOT/"candidates/offline-test44-transparent-controller/XGODriver.cpp"
NEW=ROOT/"candidates/offline-polish03-dp-rpu2/XGODriver.cpp"

def strip_comments(s):
    return re.sub(r"/\*.*?\*/|//[^\n]*","",s,flags=re.S)

class Polish03Rpu2Contract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pre=PRE.read_text()
        cls.new=NEW.read_text()

    def test_only_one_phy_register_assignment_differs(self):
        old="usb_hw->phy_direct = 0;"
        new="usb_hw->phy_direct = USB_USBPHY_DIRECT_DP_PULLUP_EN_BITS;"
        self.assertEqual(self.pre.count(old),1)
        self.assertEqual(self.new.count(new),1)
        reverted=self.new.replace(new,old)
        self.assertEqual(
            re.findall(r"\w+|[^\s\w]",strip_comments(reverted)),
            re.findall(r"\w+|[^\s\w]",strip_comments(self.pre)),
            "Executable Polish03 diverged from HW-tested transparent driver"
        )

    def test_weak_pullup_selection_and_ordering(self):
        s=self.new
        self.assertEqual(s.count("usb_hw->phy_direct = USB_USBPHY_DIRECT_DP_PULLUP_EN_BITS;"),1)
        self.assertLess(s.index("usb_hw->phy_direct = USB_USBPHY_DIRECT_DP_PULLUP_EN_BITS;"),s.index("usb_hw->phy_direct_override ="))
        self.assertNotIn("USB_USBPHY_DIRECT_DP_PULLUP_HISEL_BITS",s)
        self.assertNotIn("USB_USBPHY_DIRECT_OVERRIDE_DP_PULLUP_HISEL_OVERRIDE_EN_BITS",s)
        self.assertNotIn("USB_USBPHY_DIRECT_OVERRIDE_DM_PULLUP_OVERRIDE_EN_BITS",s)
        self.assertNotIn("USB_USBPHY_DIRECT_DM_PULLUP_EN_BITS",s)
        self.assertIn("USB_USBPHY_DIRECT_OVERRIDE_DP_PULLUP_EN_OVERRIDE_EN_BITS",s)
        self.assertIn("USB_USBPHY_DIRECT_OVERRIDE_DP_PULLDN_EN_OVERRIDE_EN_BITS",s)
        self.assertIn("USB_USBPHY_DIRECT_OVERRIDE_DM_PULLDN_EN_OVERRIDE_EN_BITS",s)
        self.assertIn("usb_hw->sie_ctrl = 0;",s)
        self.assertIn("usb_hw->main_ctrl = 0;",s)
        self.assertIn("USB_USB_MUXING_TO_PHY_BITS",s)

    def test_open_drain_12_slot_protocol_untouched(self):
        s=self.new
        for required in (
            "constexpr uint32_t EDGE_TIMEOUT_US = 18;",
            "inline void data_release() { clear_alias->phy_direct = USB_USBPHY_DIRECT_TX_DP_OE_BITS; }",
            "inline void data_sink() { set_alias->phy_direct = USB_USBPHY_DIRECT_TX_DP_OE_BITS; }",
            "const uint16_t mask = physical;",
            "published_mask.store(snapshot, std::memory_order_release);",
            "complete = wait_data(true, EDGE_TIMEOUT_US);",
            "const bool hk_slot0 = (mask & 1u) != 0;"
        ):
            self.assertIn(required,s)
        self.assertNotIn("CLOCK_TIMEOUT_US",s)
        self.assertNotIn("TX_DP = 1",s)
        self.assertNotIn("attack_pulse_mask",s)

    def test_electrical_load_nominal_only(self):
        # Theory/design check, NOT a claim about measured XGO pad current:
        # at 3.15V supply, standard USB 2.3k pull draws ~1.37mA
        # when LOAD drives DATA to ideal 0V; this does not establish
        # H1512 L0 sink capability or exact electrical backfeed paths.
        nominal_milliamps=3.15/2300*1000
        self.assertGreater(nominal_milliamps,1.3)
        self.assertLess(nominal_milliamps,1.5)

if __name__=="__main__":
    unittest.main(verbosity=2)
