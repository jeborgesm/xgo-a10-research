#!/usr/bin/env python3
"""Compile the REAL GP2040-CE map_mask(), process(), emit_frame() and test
end-to-end physical Gamepad -> atomic publication -> XGO wire sampling.

No synthetic pulse and no emulator semantics. Pinned-source C++ model with
deterministic host clock handshake. Independent free-running CLOCK model is
a second separate gate. Host C++ models do not prove XGO electrical timing.
"""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import importlib.util

ROOT=Path("integrations/gp2040ce-xgo-test01")
CAND=ROOT/"candidates/offline-test44-transparent-controller/XGODriver.cpp"
LEGACY_TEST=ROOT/"tests/test_responder_compiled_mock.py"

spec=importlib.util.spec_from_file_location("xgo_scripted_mock",LEGACY_TEST)
legacy=importlib.util.module_from_spec(spec)
spec.loader.exec_module(legacy)

GAMEPAD= r"""
struct Gamepad {
    uint16_t raw = 0;
    bool pressedR1() const {return !!(raw & (1u << 0));}
    bool pressedB4() const {return !!(raw & (1u << 1));}
    bool pressedB3() const {return !!(raw & (1u << 2));}
    bool pressedL1() const {return !!(raw & (1u << 3));}
    bool pressedB1() const {return !!(raw & (1u << 4));}
    bool pressedB2() const {return !!(raw & (1u << 5));}
    bool pressedS1() const {return !!(raw & (1u << 6));}
    bool pressedS2() const {return !!(raw & (1u << 7));}
    bool pressedUp() const {return !!(raw & (1u << 8));}
    bool pressedDown() const {return !!(raw & (1u << 9));}
    bool pressedLeft() const {return !!(raw & (1u << 10));}
    bool pressedRight() const {return !!(raw & (1u << 11));}
};
struct XGODriver { bool process(Gamepad *); };
std::atomic<uint32_t> xgo_diag_mask_changes{0};
std::atomic<uint32_t> xgo_diag_nonzero_to_zero{0};
std::atomic<uint32_t> xgo_diag_zero_frames{0};
std::atomic<uint32_t> xgo_diag_last_nonzero_mask{0};
std::atomic<uint32_t> xgo_diag_output{0};
uint16_t previous_snapshot = 0;
"""

MAIN=r"""
void real_frame(XGODriver &driver, Gamepad &pad, uint16_t physical,
                bool rearm = false, bool success = true,
                int failure_slot = -1, bool fail_rise = false,
                bool false_r_sample = false) {
    pad.raw = physical;
    check(driver.process(&pad), "GP2040 process rejected Gamepad");
    check(published_mask.load() == physical,
          "Core0 did not publish exact physical mask");
    check(xgo_diag_output.load() == physical, "Processed input diagnostic diverged");
    script.clear();
    cursor = 0; slot_seen = 0; sampled_mask = 0;
    saw_load_low = false; sampled_slot0 = false; sinking = false;
    model_host_sampled_release_too_early = false_r_sample;
    frame_script(physical,rearm,failure_slot,fail_rise,true);
    const bool complete = emit_frame();
    check(complete == success, "Wrong complete/failed serial response");
    check(cursor == script.size(), "Host event sequence not fully consumed");
    check(!sinking, "Never leave DATA asserted after frame/abort");
    if (failure_slot == -1) {
        check(sampled_mask == (physical | (false_r_sample ? 1u : 0u)),
              "Physical mask changed in transit to serial wire");
    } else {
        check(!(sampled_mask & ~physical), "Aborted frame invented a new bit");
    }
}
int main() {
    XGODriver driver;
    Gamepad pad;
    // Every physical input combination goes through the actual GP2040
    // mapping AND process() before the production emit_frame() code.
    for (uint16_t mask=0; mask<4096; ++mask)
        real_frame(driver,pad,mask);
    std::printf("PASS 4096/4096 real Gamepad->process->12-slot serial masks\n");

    // Each individual physical input stays held across 8 independent XGO
    // scans. Release must be represented by the NEXT scan, with no
    // artificial hold, extension, truncation or local turbo oscillator.
    for (unsigned slot=0;slot<12;++slot) {
        const uint16_t held=uint16_t(1u<<slot);
        real_frame(driver,pad,0);
        for(unsigned scan=0;scan<8;++scan) {
            tick += 16000;
            real_frame(driver,pad,held);
        }
        tick += 16000;
        real_frame(driver,pad,0);
    }
    std::printf("PASS 12/12 individually held + released buttons, 8+ scans each\n");

    // Simultaneous chords and independent release of one button, including
    // START/SELECT, all four directions and all six attack buttons.
    for(uint16_t chord: {uint16_t(0x03fu),uint16_t(0xf00u),
                         uint16_t(0x0c0u),uint16_t(0xfffu),
                         uint16_t(0x824u),uint16_t(0x411u)}) {
        for (unsigned scan=0;scan<7;++scan) {
            tick+=16000;
            real_frame(driver,pad,chord);
        }
        for (unsigned bit=0;bit<12;++bit) {
            if (!(chord&(1u<<bit))) continue;
            tick+=16000;
            real_frame(driver,pad,uint16_t(chord & ~(1u<<bit)));
        }
        real_frame(driver,pad,0);
    }
    std::printf("PASS simultaneous chords, independent releases and button directions\n");

    // Distinguish a bona-fide held input from a short press caught by Core0:
    // a press sampled on Core0 can be visible to one next host scan, but
    // it is NOT extended for additional scans after physical release.
    for (unsigned bit=0; bit<12; ++bit) {
        real_frame(driver,pad,uint16_t(1u<<bit));
        real_frame(driver,pad,0);
        real_frame(driver,pad,0);
    }
    std::printf("PASS short captured taps without fabricated pulse window\n");

    constexpr uint16_t RIGHT=(1u<<11),FIRE=(1u<<5),JUMP=(1u<<0),START=(1u<<7);
    check(!((RIGHT|FIRE)&(JUMP|START)),"Mask identities wrong");
    for (unsigned i=0;i<150;++i) {
        tick+=16000;
        real_frame(driver,pad,RIGHT|FIRE);
        real_frame(driver,pad,RIGHT);
        real_frame(driver,pad,RIGHT|FIRE);
        real_frame(driver,pad,RIGHT);
    }
    // Host sampled DATA rise too late. This remains an injected electrical
    // failure, not evidence of an erroneous Gamepad snapshot.
    real_frame(driver,pad,RIGHT|FIRE,false,true,-1,false,true);
    std::printf("PASS 150 RIGHT+FIRE repeats and separate synthetic false-R injection\n");

    // Clock failure must release DATA, rearm after LOAD HIGH, then send
    // the CURRENT physical snapshot. Do not replay old button events.
    for(int slot=1;slot<12;++slot) {
        for(int rise=0;rise<2;++rise) {
            real_frame(driver,pad,RIGHT|FIRE,false,false,slot,rise!=0);
            real_frame(driver,pad,0,true,true);
            real_frame(driver,pad,JUMP|START);
            real_frame(driver,pad,0);
        }
    }
    std::printf("PASS 22 mid-frame aborts, live-state recovery and clean release\n");
}
"""

def extract(src,begin,end):
    a=src.index(begin)
    b=src.index(end,a+len(begin))
    return src[a:b]

def main():
    if not shutil.which("g++"):
        raise RuntimeError("Host g++ is required")
    source=CAND.read_text()
    mapfn=extract(source,"uint16_t map_mask(Gamepad *g) {","// Test03:")
    frame=extract(source,"bool __no_inline_not_in_flash_func(emit_frame)() {","\n}\n\n} // namespace")
    frame=frame.replace("bool __no_inline_not_in_flash_func(emit_frame)() {","bool emit_frame() {")+"\n}"
    process=source[source.index("bool XGODriver::process(Gamepad *gamepad) {"):]
    for banned in ("attack_pulse_mask","ATTACK_PULSE_US","ATTACK_PULSE_BITS",
                   "attack_edge_generation","XGO_NATIVE_TURBO_HOLD_BITS"):
        assert banned not in source,banned
    assert "const uint16_t mask = physical;" in frame
    assert "published_mask.store(snapshot, std::memory_order_release);" in process

    # Legacy host scripted DATA and CLOCK are used unchanged; only source
    # extracted from candidate supplies actual physical publishing logic.
    prelude=legacy.PRELUDE.replace("IS_NATIVE_TURBO_HOLD","false")
    code=(prelude+"\n"+GAMEPAD+"\n"+mapfn+"\n"+frame+
          "\n"+process+"\n"+MAIN)
    with tempfile.TemporaryDirectory(prefix="xgo-transparent-real-cpp-") as d:
        src=Path(d)/"real_controller.cpp"
        exe=Path(d)/"real_controller"
        src.write_text(code)
        p=subprocess.run(["g++","-std=c++17","-O2","-Wall","-Wextra",
                          "-Werror",str(src),"-o",str(exe)],
                         capture_output=True,text=True)
        if p.returncode: raise RuntimeError("Host compilation failed:\n"+p.stderr)
        r=subprocess.run([str(exe)],capture_output=True,text=True)
        if r.returncode: raise RuntimeError(
            f"Extracted real C++ test failed rc={r.returncode}:\n"+
            r.stdout+"\n"+r.stderr)
        print(r.stdout)
    print("LIMIT: Scripted host CLOCK; physical XGO DATA rise/JUMP cause OPEN")

if __name__=="__main__":
    main()
