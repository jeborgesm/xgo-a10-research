#!/usr/bin/env python3
"""SRC regression: current transparent A vs P3 passive native USB PHY.

This is a register configuration/code-path comparison, not analog impedance
measurement or claim that P3 ordinary cable equals current Frankie V2 Jr.
"""
from pathlib import Path
import re

PASSIVE=Path("tools/rp2040-xgo-p3-usbphy/main.c")
CURRENT=Path("integrations/gp2040ce-xgo-test01/candidates/offline-test44-transparent-controller/XGODriver.cpp")
P3_LOG=Path("experiments/rp2040-usbphy-p3-passive.md")
CABLE=Path("tools/rp2040-xgo-live-controller/README.md")
OVERRIDE_RE=re.compile(r"USB_USBPHY_DIRECT_OVERRIDE_([A-Z_]+)_BITS")

REQUIRED={
    "TX_DIFFMODE_OVERRIDE_EN","TX_PD_OVERRIDE_EN","RX_PD_OVERRIDE_EN",
    "TX_DM_OVERRIDE_EN","TX_DP_OVERRIDE_EN",
    "TX_DM_OE_OVERRIDE_EN","TX_DP_OE_OVERRIDE_EN",
    "DP_PULLUP_EN_OVERRIDE_EN","DP_PULLDN_EN_OVERRIDE_EN",
    "DM_PULLDN_EN_OVERRIDE_EN",
}

def override_names(source):
    match=re.search(r"usb_hw->phy_direct_override\s*=\s*([^;]+);",source)
    assert match, "Direct override initialization missing"
    return set(OVERRIDE_RE.findall(match.group(1)))

def main():
    p3=PASSIVE.read_text()
    current=CURRENT.read_text()
    log=P3_LOG.read_text()
    cable=CABLE.read_text()
    for label,source in (("P3 passive",p3),("approved transparent A",current)):
        assert override_names(source)==REQUIRED,(label,override_names(source)^REQUIRED)
        assert "USB_USBPHY_DIRECT_OVERRIDE_DM_PULLUP_OVERRIDE_EN_BITS" not in source
        for init in ("usb_hw->main_ctrl", "usb_hw->sie_ctrl",
                     "usb_hw->phy_direct"):
            assert re.search(re.escape(init)+r"\s*=\s*0\s*;",source),label
        assert "USB_USB_MUXING_TO_PHY_BITS" in source
        assert "USB_USB_MUXING_SOFTCON_BITS" in source
        assert "USB_USBPHY_DIRECT_RX_DP_BITS" in source
        assert "USB_USBPHY_DIRECT_RX_DM_BITS" in source
    assert "data_sink(" not in p3, "P3 not a transmit source"
    assert "USB_USBPHY_DIRECT_TX_DP_OE_BITS|USB_USBPHY_DIRECT_TX_DM_OE_BITS" in p3
    assert "inline void data_sink() { set_alias->phy_direct = USB_USBPHY_DIRECT_TX_DP_OE_BITS; }" in current
    assert "inline void data_release() { clear_alias->phy_direct = USB_USBPHY_DIRECT_TX_DP_OE_BITS; }" in current
    assert "Player 2 intermittently performs JUMP without user input." in log
    assert "froze the XGO" in log  # historical P3-v3 DM pull-up override hardware regression
    assert "2 and 4 share WHITE" in cable
    assert "ordinary micro-USB cable" in log
    assert "Frankie V2 Jr" in cable
    print("PASS SRC: exact ten USBPHY overrides, initialized SIE/PHY/MUX, "
          "receiver always on; P3 never sinks DATA")
    print("PASS HW archives: P3 passive electrical phantom jump; "
          "DM-pullup override trial froze XGO")
    print("OPEN: native PHY analog loading, DM pullup state under SIE, "
          "cable electrical equivalence, DATA rise at first XGO R sample")
    print("NO PHY reconfiguration justified, especially not DM-pullup override")

if __name__=="__main__":
    main()
