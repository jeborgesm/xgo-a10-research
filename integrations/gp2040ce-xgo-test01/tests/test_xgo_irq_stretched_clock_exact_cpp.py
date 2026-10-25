#!/usr/bin/env python3
"""Exact C++ GP2040 responder versus synthetic XGO interrupt-stretched clocks.

Unlike a missing RP-observed pulse, this mock actually lengthens the host
CLOCK level while leaving all 12 transitions intact. This is only a
conditional MODEL; actual XGO interrupt durations are unmeasured.
"""
from pathlib import Path
import shutil
import subprocess
import tempfile
from test_responder_compiled_mock import extract
from test_exact_xgo_rearm_two_frames import GLOBALS, MOCK, SOURCE

# Each existing wave-form expression is preserved, but we insert a 25us
# host CPU pause on one selected clock phase before normal scan continues.
MARKER = "    double t=now-frame*cadence;\n"
assert MOCK.count(MARKER)==1
STALLED = MOCK.replace(MARKER, MARKER + r'''
    if(frame==0 && ((fault>=20 && fault<=31)||(fault>=40 && fault<=50))) {
      bool pause_low=fault<40;
      int index=pause_low?(int)fault-20:(int)fault-40;
      double pause_start=1.2+index*period+low_width;
      if(t>=pause_start && t<pause_start+25.0)
        return !pause_low;
      if(t>=pause_start+25.0)t-=25.0;
    }
''')
# The preceding host-bit decoder samples nominal offsets, not delayed
# host instruction sample times. Do not use host_word(frame0) as evidence.
MAIN = r'''
int main(int argc,char**argv){
  if(argc!=2)return 90;
  fault=(unsigned)std::atoi(argv[1]);
  if(fault!=0 && !(fault>=20&&fault<=31)
      && !(fault>=40&&fault<=50))return 91;
  published_mask.store(1u<<4); // real physical A stays held
  bool first=emit_frame();
  double finished=now;
  bool second=emit_frame();
  uint16_t next_host_word=host_word(1);
  uint32_t errors=xgo_diag_clock_timeouts.load();
  unsigned failed=xgo_diag_last_failure_slot.load();
  std::printf("fault=%u first=%d first_done=%.2f "
              "second=%d second_word=%04x clock_error=%u last_slot=%u\n",
              fault,first,finished,second,next_host_word,errors,failed);
  if(!second || next_host_word!=0x0080)return 1;
  if(fault==0){
    if(!first || errors || failed)return 2;
  }else if(fault>=20 && fault<=31){
    unsigned pulse=fault-20; // 0-based, physical CLOCK number=pulse+1
    if(first)return 3;
    if(pulse<11){
      if(errors!=1 || failed!=pulse+1)return 4;
    } else {
      // After all 12 FALL transitions, protected final HIGH timeout
      // returns failed but omits xgo_diag_clock_timeouts increment.
      if(errors || failed)return 5;
    }
  } else {
    unsigned pulse=fault-40;
    // Delay occurs in HIGH phase preceding NEXT FALL.
    if(first||errors!=1||failed!=pulse+2)return 6;
  }
  std::puts("PASS C++ exact source, clock pause fault and next-frame recovery");
}
'''
def run():
    assert shutil.which('g++'), "Need host C++ compiler"
    actual=extract(SOURCE.read_text())
    with tempfile.TemporaryDirectory() as tmp:
        source=Path(tmp)/"test.cpp"
        exe=Path(tmp)/"test"
        source.write_text(GLOBALS+STALLED+actual+MAIN)
        result=subprocess.run(["g++","-std=c++17","-O2","-Wall","-Wextra",
                               "-Werror",str(source),"-o",str(exe)],
                              capture_output=True,text=True)
        if result.returncode:raise RuntimeError(result.stderr)
        for scenario in [0,*range(20,32),*range(40,51)]:
            case=subprocess.run([str(exe),str(scenario)],
                                capture_output=True,text=True)
            print(case.stdout.strip())
            if case.returncode:raise RuntimeError(
                f"CASE {scenario} FAILED={case.returncode}:\n"
                +case.stdout+"\n"+case.stderr)
    print("PASS: all 23 synthetic host-IRQ pulse/gap cases; "
          "actual XGO IRQ timings remain OPEN")

if __name__=="__main__":run()
