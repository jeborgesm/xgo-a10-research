#!/usr/bin/env python3
"""Fail-closed source-contract checks for experimental Test17 (not hardware proof)."""
from pathlib import Path
import re
import unittest

BASE = Path(__file__).resolve().parents[1]
DRIVER = BASE / "candidates/test17-direct-gpio-offline/XGODriver.cpp"
OVERLAY = BASE / "apply.py"
WORKFLOW = Path(__file__).resolve().parents[3] / ".github/workflows/gp2040ce-xgo-test17-offline.yml"

class Test17Gates(unittest.TestCase):
 def test_source_selection(self):
  s=WORKFLOW.read_text()
  self.assertIn("candidates/test17-direct-gpio-offline/XGODriver.cpp",s)
  self.assertIn("cmp integrations/gp2040ce-xgo-test01/candidates/test17-direct-gpio-offline",s)
  self.assertIn("README-DO-NOT-FLASH",s)
 def test_direct_gpio_authority(self):
  s=DRIVER.read_text()
  self.assertIn("const uint16_t mask = read_xgo_direct_mask();",s)
  self.assertNotIn("published_mask.load(",s)
  self.assertEqual(s.count("sio_hw->gpio_in"),1)
  self.assertRegex(s,r"constexpr uint8_t xgo_slot_gpio\[12\]\s*=\s*\{12,11,10,13,6,7,16,17,2,3,5,4\}")
 def test_phy_isolation(self):
  s=DRIVER.read_text()
  self.assertIn("USB_USBPHY_DIRECT_RX_DM_BITS",s)
  self.assertIn("USB_USBPHY_DIRECT_TX_DP_OE_BITS",s)
  self.assertIn("save_and_disable_interrupts()",s)
  self.assertIn("restore_interrupts(irq_state)",s)
 def test_web_config_still_present(self):
  s=OVERLAY.read_text()
  self.assertIn('www/src/Data/InputBootModes.ts',s)
  self.assertIn('www/src/Locales/en/SettingsPage.jsx',s)
  self.assertIn('GP2040_BOARDCONFIG=Pico',s)
 def test_no_silent_elf_failure(self):
  s=WORKFLOW.read_text()
  self.assertIn("arm-none-eabi-objdump -d",s)
  self.assertIn("arm-none-eabi-nm -C",s)
  self.assertNotIn("xgo-test17-disassembly.txt || true",s)
if __name__=="__main__":unittest.main()
