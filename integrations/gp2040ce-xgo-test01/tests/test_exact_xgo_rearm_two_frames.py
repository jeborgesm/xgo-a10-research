#!/usr/bin/env python3
"""Actual protected emit_frame() C++ with two synthetic XGO host transactions.

Read-only: host GPIO timebase and PHY observation faults are simulated.
No firmware artifact is changed, and all failure modes are deliberately injected.
"""
from pathlib import Path
import shutil
import subprocess
import tempfile
from test_responder_compiled_mock import PRELUDE, extract

SOURCE = Path("integrations/gp2040ce-xgo-test01/candidates/offline-test44-transparent-controller/XGODriver.cpp")
GLOBALS = PRELUDE.split("struct Step")[0].replace("IS_NATIVE_TURBO_HOLD", "false")
MOCK = r'''
#include <cmath>
#include <cstdlib>
struct Event { double t; bool sink; };
std::vector<Event> events;
double now=-6;
bool sink=false;
unsigned fault=0;
constexpr double cadence=16030.0;
constexpr double low_width=2.0;
constexpr double period=4.0;
static const uint16_t wirebits[12]={
  0x1000,0x2000,0x4000,0x0800,0x0080,0x0040,
  0x0020,0x0010,0x0008,0x0004,0x0002,0x0001};
uint32_t time_us_32(){now+=0.035;return (uint32_t)(1000000+std::floor(now));}
uint32_t save_and_disable_interrupts(){return 0;}
void restore_interrupts(uint32_t){}
void data_release(){if(sink)events.push_back({now,false});sink=false;}
void data_sink(){if(!sink)events.push_back({now,true});sink=true;}
bool host_load(double t){
  for(int frame=0;frame<2;frame++){
    double start=frame*cadence;
    if(t>=start-5.0 && t<start)return true;
  }
  return false;
}
bool data_level(){now+=0.035;return !host_load(now)&&!sink;}
bool clock_level(){
  now+=0.035;
  for(int frame=0;frame<2;frame++){
    double t=now-frame*cadence;
    if(frame==0 && fault==2 && t>=47.2 && t<70.0)return false;
    if(t>=1.2 && t<1.2+12*period){
      int pulse=(int)std::floor((t-1.2)/period);
      bool in_low=std::fmod(t-1.2,period)<low_width;
      // The XGO clock #4 exists on the wire but a synthetic RP2040
      // receive/observation fault hides it from wait_clock().
      if(frame==0 && fault==1 && pulse==3)return true;
      return !in_low;
    }
  }
  return true;
}
bool wait_clock(bool level,uint32_t timeout){
  const uint32_t t=time_us_32();
  while(clock_level()!=level)
    if((uint32_t)(time_us_32()-t)>timeout)return false;
  return true;
}
bool wait_data(bool level,uint32_t timeout){
  const uint32_t t=time_us_32();
  while(data_level()!=level)
    if((uint32_t)(time_us_32()-t)>timeout)return false;
  return true;
}
bool sink_at(double t){
  bool v=false;
  for(auto &e:events){if(e.t>t)break;v=e.sink;}
  return v;
}
uint16_t host_word(int frame){
  uint16_t word=0;
  double start=frame*cadence;
  for(int slot=0;slot<12;slot++){
    double sample=start+(slot?1.2+(slot-1)*period+2.2:0.1);
    if(host_load(sample)||sink_at(sample))word|=wirebits[slot];
  }
  return word;
}
'''
MAIN=r'''
int main(int argc,char**argv){
  if(argc!=2)return 99;
  fault=(unsigned)std::atoi(argv[1]);
  if(fault>2)return 98;
  const uint16_t A=1u<<4;
  published_mask.store(A);
  // Exact source under test invoked twice; the local require_idle_high
  // static persists across both transactions.
  bool first=emit_frame();
  double first_done=now;
  bool second=emit_frame();
  uint16_t first_word=host_word(0),second_word=host_word(1);
  std::printf("fault=%u frame0 success=%d host=%04x done=%0.2f; "
              "frame1 success=%d host=%04x; clkerr=%u last_slot=%u "
              "failures=%u\n",fault,first,first_word,first_done,second,
              second_word,xgo_diag_clock_timeouts.load(),
              xgo_diag_last_failure_slot.load(),
              xgo_diag_active_failures.load());
  if(!second || second_word!=0x0080)return 1;
  if(fault==0){
    if(!first || first_word!=0x0080
       || xgo_diag_active_failures.load()!=0)return 2;
  }
  if(fault==1){
    if(first || xgo_diag_active_failures.load()!=1
       || xgo_diag_clock_timeouts.load()!=1
       || xgo_diag_last_failure_slot.load()!=12)return 3;
    if(first_word==0x0080)return 4;
  }
  if(fault==2){
    // The 12 button bits were transmitted BEFORE the failed trailing HIGH.
    // Protected source returns false, re-arms, but increments no CLK error.
    if(first || first_word!=0x0080
       || xgo_diag_active_failures.load()!=1
       || xgo_diag_clock_timeouts.load()!=0)return 5;
  }
  std::puts("PASS exact emit_frame(), two chronological XGO scans");
  std::puts("LIMIT synthetic PHY and host edges; no live current-A waveform");
}
'''
def run():
    if not shutil.which("g++"): raise RuntimeError("g++ missing")
    src=SOURCE.read_text()
    code=extract(src)
    with tempfile.TemporaryDirectory() as tmp:
        p=Path(tmp)/"main.cpp"; exe=Path(tmp)/"main"
        p.write_text(GLOBALS+MOCK+code+MAIN)
        c=subprocess.run(["g++","-std=c++17","-O2","-Wall","-Wextra",
                          "-Werror",str(p),"-o",str(exe)],
                         capture_output=True,text=True)
        if c.returncode: raise RuntimeError("compile: "+c.stderr)
        for fault in (0,1,2):
            r=subprocess.run([str(exe),str(fault)],capture_output=True,text=True)
            print(r.stdout.strip())
            if r.returncode: raise RuntimeError("fault "+str(fault)+": "+
                                                r.stdout+"\n"+r.stderr)
    print("PASS all: normal, one RP missed CLOCK, and false terminal HIGH timeout")

if __name__=="__main__": run()
