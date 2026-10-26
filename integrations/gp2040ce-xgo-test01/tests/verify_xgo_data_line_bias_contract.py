#!/usr/bin/env python3
"""Forensic XGO DATA released-HIGH bias ownership audit (read-only).

Default run is SRC-only and works in Actions. Pass --stock-original
/path/to/XGoAnalisis.zip for exact SHA-pinned original firmware MIPS opcode
verification. Neither method measures an analog voltage or an XGO pull-up.
"""
import argparse
import hashlib
import re
import struct
import zipfile
from pathlib import Path

DRIVER = Path("integrations/gp2040ce-xgo-test01/candidates/offline-test44-transparent-controller/XGODriver.cpp")
EXPECTED_DRIVER_SHA1 = "cccb985a05baa8bb9078b6e336eb5f991c1a7a8f"
EXPECTED_STOCK_SHA256 = "869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf"
# These are original MIPS little-endian words, NOT synthesized binaries.
WORDS = {
  0x35d7a0: 0x36700058,  # s0 = 0xB8800058: L port GPIO direction
  0x35d7c8: 0x35490001,  # set L0 direction bit during LOAD
  0x35d7cc: 0xae090000,  # write L direction
  0x35d804: 0x367f0054,  # ra = 0xB8800054: L port output latch
  0x35d818: 0xafe30000,  # write L0 output low
  0x35d858: 0x8e0c0000,  # read L direction
  0x35d85c: 0x240dfffe,  # clear L0 direction bit
  0x35d860: 0x018d5824,  # mask L0 direction
  0x35d864: 0xae0b0000,  # write direction: L0 input/released
  0x35d87c: 0x36710050,  # s1 = 0xB8800050: L input read
  0x35d890: 0x8e390000,  # read L0 physical DATA before first clock
}

def check_driver():
    text=DRIVER.read_text()
    assert "inline bool data_level() { return (usb_hw->phy_direct & USB_USBPHY_DIRECT_RX_DP_BITS) != 0; }" in text
    assert "inline bool clock_level() { return (usb_hw->phy_direct & USB_USBPHY_DIRECT_RX_DM_BITS) != 0; }" in text
    assert "usb_hw->phy_direct = 0;" in text
    assert "USB_USBPHY_DIRECT_OVERRIDE_DP_PULLUP_EN_OVERRIDE_EN_BITS" in text
    assert "USB_USBPHY_DIRECT_OVERRIDE_DP_PULLDN_EN_OVERRIDE_EN_BITS" in text
    assert "USB_USBPHY_DIRECT_OVERRIDE_DM_PULLDN_EN_OVERRIDE_EN_BITS" in text
    assert "USB_USBPHY_DIRECT_OVERRIDE_DM_PULLUP_OVERRIDE_EN_BITS" not in text
    assert re.search(r"inline void data_release\(\)\s*\{\s*clear_alias->phy_direct\s*=\s*USB_USBPHY_DIRECT_TX_DP_OE_BITS;\s*\}",text)
    assert re.search(r"inline void data_sink\(\)\s*\{\s*set_alias->phy_direct\s*=\s*USB_USBPHY_DIRECT_TX_DP_OE_BITS;\s*\}",text)
    assert "USB_USBPHY_DIRECT_TX_DP_BITS" not in text, "Do not add active-high DATA"
    # Regular protected idle serializer never sinks DATA for all-released bits.
    assert "if (mask & (1u << slot)) data_sink(); else data_release();" in text
    assert "if (hk_slot0)" in text and "data_sink();" in text
    print("PASS SRC: native DP=DATA / DM=CLOCK, DP pull-up forced OFF by active override")
    print("PASS SRC: released DATA uses TX_DP_OE=0 Hi-Z, pressed DATA sinks LOW only")
    print("PASS SRC: DM pull-up control is NOT similarly overridden (historical change froze XGO)")
    print("OPEN: voltage HIGH source/strength, XGO-side pull configuration, and analog rise time")

def check_original(path):
    path=Path(path)
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z: image=z.read("bios/bisrv.asd")
    else:
        image=path.read_bytes()
    sha=hashlib.sha256(image).hexdigest()
    assert sha==EXPECTED_STOCK_SHA256,(sha,EXPECTED_STOCK_SHA256)
    for off,want in WORDS.items():
        actual=struct.unpack_from("<I",image,off)[0]
        assert actual==want,(hex(off),hex(actual),hex(want))
    print(f"PASS BIN: original stock SHA256 and {len(WORDS)} MIPS words match")
    print("PASS BIN: XGO L0 host DATA OUTPUT LOW during LOAD -> L0 INPUT -> early L0 read")
    print("LIMIT: these GPIO direction/latch/read instructions do not identify a pull-up")
    print("LIMIT: stock image is not GOLD; no analog GPIO high-threshold observed")

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--stock-original",type=Path,
        help="optional original XGoAnalisis.zip containing bios/bisrv.asd")
    args=p.parse_args()
    check_driver()
    if args.stock_original:check_original(args.stock_original)
    else:print("BIN optional: supply --stock-original to verify actual original XGO image")
if __name__=="__main__":main()
