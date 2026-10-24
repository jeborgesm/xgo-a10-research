#!/usr/bin/env python3
"""Pin and host-exercise the ACTUAL upstream-derived SSD1306 drawBuffer().

The XGO firmware moves the OLED to Core0, where a synchronous whole-screen
I2C write blocks the physical input scan. This test checks that the proposed
XGO-only revision writes ONE of eight display pages per loop and preserves
the non-XGO original path. The exact hardware I2C baud rate and any bus
stretching remain hardware/configuration-dependent.
"""
from pathlib import Path
import subprocess
import tempfile
import shutil
import re
import unittest

SRC=Path("integrations/gp2040ce-xgo-test01/candidates/offline-transparent-page-oled/tiny_ssd1306.cpp")
BASE_BLOB="ecc750d00324a6da368f6d78d9afa40c4eb0e632" # Verified pinned GP2040-CE I2C display implementation.

def extract_method(src):
    begin="void GPGFX_TinySSD1306::drawBuffer(uint8_t* pBuffer) {"
    end="void GPGFX_TinySSD1306::rotatePoint("
    assert src.count(begin)==1 and src.count(end)==1
    return src[src.index(begin):src.index(end)]

MOCK=r"""
#include <cstdint>
#include <cstring>
#include <vector>
#include <stdexcept>
#include <cstdio>
#include <algorithm>
using std::uint16_t;
using std::uint8_t;
enum {INPUT_MODE_XGO=18,INPUT_MODE_XINPUT=2};
class DriverManager {
public:
    int inputMode=INPUT_MODE_XGO;
    static DriverManager& getInstance() {static DriverManager d;return d;}
    int getInputMode() const {return inputMode;}
};
struct FakeI2C {
    struct Tx {uint8_t addr;std::vector<uint8_t> bytes;bool nostop;};
    std::vector<Tx> writes;
    int write(uint8_t address,uint8_t* data,uint16_t length,bool nostop) {
        writes.push_back(Tx{address,std::vector<uint8_t>(data,data+length),nostop});
        return length;
    }
};
struct FakeOptions {FakeI2C* i2c;uint8_t address;};
class GPGFX_TinySSD1306 {
public:
    enum CommandOps{PAGE_ADDRESS=0x22,COLUMN_ADDRESS=0x21,SET_START_LINE=0x40};
    enum ScreenAlternatives{SCREEN_132x64=8};
    static constexpr uint16_t MAX_SCREEN_WIDTH=128;
    static constexpr uint16_t MAX_SCREEN_HEIGHT=64;
    static constexpr uint16_t MAX_SCREEN_SIZE=1024;
    uint8_t frameBuffer[1024]{};
    uint8_t framePage=0;
    uint8_t screenType=3;
    FakeOptions _options;
    std::vector<uint8_t> commands;
    void sendCommand(uint8_t command) {commands.push_back(command);}
    void drawBuffer(uint8_t* pBuffer);
};
void check(bool ok,const char *message) {
    if(!ok)throw std::runtime_error(message);
}
"""

MAIN=r"""
int main(){
  FakeI2C i2c;
  GPGFX_TinySSD1306 screen;
  screen._options={&i2c,0x3c};
  for(int i=0;i<1024;++i)screen.frameBuffer[i]=uint8_t(i/128+1);
  auto& dm=DriverManager::getInstance();
  dm.inputMode=INPUT_MODE_XGO;
  for(unsigned step=0;step<24;++step) {
    auto before=i2c.writes.size();
    auto cmd=screen.commands.size();
    screen.drawBuffer(nullptr);
    const unsigned page=step%8;
    check(i2c.writes.size()==before+1,"XGO must send ONE I2C page per poll");
    const auto& tx=i2c.writes.back();
    check(tx.bytes.size()==129,"SSD1306 XGO page should be 129 bytes");
    check(tx.bytes[0]==0x40,"SSD1306 data marker missing");
    for(unsigned k=1;k<=128;++k)
      check(tx.bytes[k]==uint8_t(page+1),"Wrong framebuffer page/data transmitted");
    check(screen.commands.size()==cmd+6,"SSD1306 page commands count differs");
    auto start=screen.commands.begin()+cmd;
    check(std::vector<uint8_t>(start,start+6)==
          std::vector<uint8_t>({0x22,uint8_t(page),uint8_t(page),0x21,0,127}),
          "Wrong SSD1306 page/column address");
    check(screen.framePage==((page+1)%8),"One-page round robin wrapped incorrectly");
  }
  std::printf("PASS SSD1306: 24 real method calls, 8 pages ×3, 129-byte XGO I2C writes\n");

  i2c.writes.clear();screen.commands.clear();screen.framePage=0;
  screen.screenType=GPGFX_TinySSD1306::SCREEN_132x64;
  for(unsigned step=0;step<16;++step) {
    const auto before=i2c.writes.size(),cmd=screen.commands.size();
    screen.drawBuffer(nullptr);
    auto page=step%8;
    check(i2c.writes.size()==before+1,"SH1106 page not 1 transfer");
    const auto& tx=i2c.writes.back();
    check(tx.bytes.size()==131,"SH1106 original 131-byte footprint changed");
    check(tx.bytes[0]==0x40,"SH1106 data marker missing");
    for(unsigned k=1;k<=128;++k)
      check(tx.bytes[k]==uint8_t(page+1),"SH1106 wrong page");
    check(screen.commands.size()==cmd+3,"SH1106 commands count");
    auto start=screen.commands.begin()+cmd;
    check(std::vector<uint8_t>(start,start+3)==
          std::vector<uint8_t>({uint8_t(0xB0+page),0,0x10}),
          "SH1106 selected page differs from upstream");
  }
  std::printf("PASS SH1106: 16 real method calls, 131-byte paged transfers\n");

  // Other input modes retain preexisting, full-buffer SSD1306/SH1106 path.
  dm.inputMode=INPUT_MODE_XINPUT;
  i2c.writes.clear();screen.commands.clear();screen.framePage=0;
  screen.screenType=3;
  screen.drawBuffer(nullptr);
  check(i2c.writes.size()==1 && i2c.writes[0].bytes.size()==1025,
        "Non-XGO SSD1306 original 1025-byte frame changed");
  check(screen.commands.size()==6,"Non-XGO SSD1306 command sequence changed");
  i2c.writes.clear();screen.commands.clear();screen.screenType=8;
  screen.drawBuffer(nullptr);
  check(i2c.writes.size()==8,"Non-XGO SH1106 must send all 8 pages");
  for(const auto& tx:i2c.writes)
    check(tx.bytes.size()==131,"Non-XGO SH1106 legacy transfer changed");
  std::printf("PASS non-XGO: byte-count and transaction count unchanged\n");

  // Deterministic transfer timing LOWER BOUNDS. No claim of measured rates.
  const double bits_per_byte=9, baud=400000;
  const double old_data_ms=1025*bits_per_byte*1000/baud;
  const double new_data_ms=131*bits_per_byte*1000/baud;
  check(old_data_ms>23.0 && new_data_ms<3.0,
        "Transfer-size reduction insufficient for 16ms host poll");
  std::printf("MODEL 400kHz: old 1025-byte data >=%.3f ms, "
              "new 131-byte page >=%.3f ms (commands/overhead excluded)\n",
              old_data_ms,new_data_ms);
  return 0;
}
"""

class TestOledBottleneckSource(unittest.TestCase):
    def test_xgo_page_route_and_nonxgo_legacy(self):
        s=SRC.read_text()
        m=extract_method(s)
        self.assertIn("DriverManager::getInstance().getInputMode() == INPUT_MODE_XGO",m)
        self.assertIn("framePage = (page + 1) % (MAX_SCREEN_HEIGHT / 8)",m)
        self.assertIn("const uint8_t* pixels = (pBuffer == NULL) ? frameBuffer : pBuffer",m)
        self.assertIn("MAX_SCREEN_WIDTH + 1, false",m)
        self.assertIn("MAX_SCREEN_WIDTH + 3, false",m)
        self.assertIn("uint16_t bufferSize = MAX_SCREEN_SIZE;",m)
        self.assertEqual(m.count("void GPGFX_TinySSD1306::drawBuffer"),1)

    def test_no_input_or_serializer_rewrite(self):
        s=SRC.read_text()
        self.assertNotIn("published_mask",s)
        self.assertNotIn("attack_pulse_mask",s)
        self.assertNotIn("USB_USBPHY_DIRECT_",s)
        other=Path("integrations/gp2040ce-xgo-test01/candidates/offline-test44-transparent-controller/XGODriver.cpp").read_text()
        self.assertIn("const uint16_t mask = physical;",other)

def main():
    tests=unittest.defaultTestLoader.loadTestsFromTestCase(TestOledBottleneckSource)
    if not unittest.TextTestRunner(verbosity=2).run(tests).wasSuccessful():raise SystemExit(1)
    if not shutil.which("g++"):raise RuntimeError("g++ required")
    body=extract_method(SRC.read_text())
    with tempfile.TemporaryDirectory(prefix="xgo-oled-page-mock-") as d:
        p=Path(d)/"test.cpp";exe=Path(d)/"test"
        p.write_text(MOCK+"\n"+body+"\n"+MAIN)
        cmd=subprocess.run(["g++","-std=c++17","-O2","-Wall","-Wextra","-Werror",str(p),"-o",str(exe)],capture_output=True,text=True)
        if cmd.returncode:raise RuntimeError("Exact source OLED test compilation failure:\n"+cmd.stderr)
        run=subprocess.run([str(exe)],capture_output=True,text=True)
        if run.returncode:raise RuntimeError(f"Exact source OLED test FAIL ({run.returncode}):\n{run.stdout}\n{run.stderr}")
        print(run.stdout)

if __name__=="__main__":main()
