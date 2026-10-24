#!/usr/bin/env python3
"""Pin the pre-diagnostic GP2040-CE OLED and XGO pressed-input footer.

Original upstream ButtonLayoutScreen.cpp: 3d1f32f... Git blob
197d8ee7ee8a0ee055d86440dd26350d4d0221be.
The XGO Test13 overlay adds INPUT_MODE_XGO statusBar label.
This derivative forces visible history in XGO mode while preserving
both original left and right graphical button layouts.

Optional --upstream PATH performs BYTE-EXACT derivation verification on
the pinned full GP2040-CE checkout AFTER apply.py ran.
"""
from pathlib import Path
import argparse
import re
import unittest

ROOT=Path("integrations/gp2040ce-xgo-test01")
P=ROOT/"candidates/offline-test44-transparent-controller/ButtonLayoutScreen.cpp"

class TestRestoredControllerDisplay(unittest.TestCase):
    def test_history_always_visible_only_in_xgo(self):
        s=P.read_text()
        self.assertIn(
            "isInputHistoryEnabled = (DriverManager::getInstance().getInputMode() == INPUT_MODE_XGO) ||",
            s)
        self.assertIn(
            "bool inputHistoryEnabled = (DriverManager::getInstance().getInputMode() == INPUT_MODE_XGO) ||",
            s)
        self.assertIn("getRenderer()->drawText(0, 7, footer);",s)
        self.assertIn("processInputHistory();",s)
        self.assertIn("footer = historyString;",s)

    def test_normal_selected_dpad_and_button_layouts_not_suppressed(self):
        s=P.read_text()
        for wanted in (
            "LayoutManager::getInstance().getLayoutA()",
            "LayoutManager::getInstance().getLayoutB()",
            "pushElement(currLayoutLeft[elementCtr]);",
            "pushElement(currLayoutRight[elementCtr]);",
            "getProcessedGamepad()->pressedB1()",
            "getProcessedGamepad()->pressedB2()",
            "getProcessedGamepad()->pressedB3()",
            "getProcessedGamepad()->pressedB4()",
            "getProcessedGamepad()->pressedL1()",
            "getProcessedGamepad()->pressedR1()",
            'case INPUT_MODE_XGO: statusBar += "XGO"; break;',
        ):
            self.assertIn(wanted,s)
        self.assertNotIn("for (elementCtr = 0; inputMode != INPUT_MODE_XGO",s)

    def test_no_diagnostic_oled_replacement(self):
        s=P.read_text()
        self.assertNotIn("XGODiagnostics.h",s)
        self.assertNotIn("SERIAL DIAG",s)
        self.assertNotIn("XGO44",s)
        self.assertNotIn("xgo_diag_",s)
        self.assertEqual(s.count("void ButtonLayoutScreen::drawScreen()"),1)

def validate_upstream(upstream):
    base=Path(upstream)/"src/display/ui/screens/ButtonLayoutScreen.cpp"
    assert base.is_file(),base
    s=base.read_text()
    # apply.py already installs XGO's label; otherwise this is untouched
    # upstream display source.
    pairs=[
      ("isInputHistoryEnabled = Storage::getInstance().getDisplayOptions().inputHistoryEnabled;",
       """// XGO controller mode always shows the pressed-button history in the bottom
    // row, while preserving the normal selected left/right graphical layouts.
    // Non-XGO modes retain their stored display preference.
    isInputHistoryEnabled = (DriverManager::getInstance().getInputMode() == INPUT_MODE_XGO) ||
        Storage::getInstance().getDisplayOptions().inputHistoryEnabled;"""),
      ("bool inputHistoryEnabled = Storage::getInstance().getDisplayOptions().inputHistoryEnabled;",
       """bool inputHistoryEnabled = (DriverManager::getInstance().getInputMode() == INPUT_MODE_XGO) ||
            Storage::getInstance().getDisplayOptions().inputHistoryEnabled;"""),
    ]
    for old,new in pairs:
        assert s.count(old)==1, "Unexpected upstream ButtonLayoutScreen anchor"
        s=s.replace(old,new)
    assert P.read_text()==s, (
        "OLED derivative is not exactly pinned Test13 stock display plus "
        "two XGO-only footer-enabling edits"
    )
    print("PASS: OLED exactly upstream Test13 layout + two XGO-only history changes")

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--upstream", type=Path)
    args=parser.parse_args()
    if args.upstream:validate_upstream(args.upstream)
    tests=unittest.defaultTestLoader.loadTestsFromTestCase(TestRestoredControllerDisplay)
    result=unittest.TextTestRunner(verbosity=2).run(tests)
    raise SystemExit(0 if result.wasSuccessful() else 1)
