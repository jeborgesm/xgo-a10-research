#!/usr/bin/env python3
"""Compile actual protected XGODriver::emit_frame with a synthetic chronological host.

Neither timings nor DATA voltage are measurements of Frankie V2 Jr. The
CLOCK-first policy exists here ONLY as an in-memory test replacement.
"""
from pathlib import Path
import shutil
import subprocess
import tempfile
from test_responder_compiled_mock import PRELUDE, extract

SOURCE = Path('integrations/gp2040ce-xgo-test01/candidates/offline-test44-transparent-controller/XGODriver.cpp')
GLOBALS = PRELUDE.split('struct Step')[0].replace('IS_NATIVE_TURBO_HOLD','false')
MOCK = r'''
#include <cmath>
struct Sink { double t; bool low; };
std::vector<Sink> history;
double now=-6, data_rise=0;
bool sink=false;
constexpr double first_fall=1.2, low_width=2.0, period=4.0;
uint32_t time_us_32(){now+=0.035;return (uint32_t)(1000000+std::floor(now));}
uint32_t save_and_disable_interrupts(){return 0;}
void restore_interrupts(uint32_t){}
void data_release(){if(sink)history.push_back({now,false});sink=false;}
void data_sink(){if(!sink)history.push_back({now,true});sink=true;}
bool data_level(){now+=0.035;return !(now<data_rise||sink);}
bool clock_level(){
  now+=0.035;
  if(now<first_fall||now>=first_fall+12*period)return true;
  return std::fmod(now-first_fall,period)>=low_width;
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
'''
MAIN = r'''
static uint16_t const masks[12] = {0x1000,0x2000,0x4000,0x0800,0x0080,0x0040,
                                   0x0020,0x0010,0x0008,0x0004,0x0002,0x0001};
bool low_at(double t){
  if(t<data_rise)return true;
  bool state=false;
  for(auto &x:history){if(x.t>t)break;state=x.low;}
  return state;
}
uint16_t received(){
  uint16_t m=0;
  for(int slot=0;slot<12;slot++){
    double t=slot==0?.1:first_fall+(slot-1)*period+low_width+.2;
    if(low_at(t))m|=masks[slot];
  }
  return m;
}
uint16_t to_host(uint16_t physical){
  uint16_t raw=0;
  for(int bit=0;bit<12;bit++)if(physical&(1u<<bit))raw|=masks[bit];
  return raw;
}
struct Result{bool ok;uint16_t host;uint32_t clk;uint32_t slot;};
Result trial(uint16_t mask,double rise){
  now=-6;data_rise=rise;sink=false;history.clear();
  published_mask.store(mask);
  xgo_diag_clock_timeouts.store(0);
  xgo_diag_last_failure_slot.store(0);
  bool success=emit_frame();
  return {success,received(),xgo_diag_clock_timeouts.load(),
          xgo_diag_last_failure_slot.load()};
}
int main(){
  for(uint16_t m=0;m<4096;m++){
    auto r=trial(m,0);
    if(!r.ok||r.host!=to_host(m)){
      std::printf("FAIL policy=%d mask=%03x ok=%d host=%04x expect=%04x\n",
          CLOCK_FIRST,m,r.ok,r.host,to_host(m));return 1;
    }
  }
  std::printf("PASS policy=%d: all 4096 ideal masks\n",CLOCK_FIRST);
  // R0 pressed takes the protected early-sink path, which does NOT gate
  // the later bits on DATA HIGH. Even there the host can sample a false Y
  // when the external line remains low into the second bit's sample.
  auto held_r_a=trial((1u<<0)|(1u<<4),3.6);
  std::printf("policy=%d HELD_R_A rise=3.6 host=%04x ok=%d clkerr=%u\\n",
      CLOCK_FIRST,held_r_a.host,held_r_a.ok,held_r_a.clk);
  if(!held_r_a.ok||held_r_a.host!=0x3080||held_r_a.clk)return 6;
  for(double rise:{0.,.3,.7,2.1,3.0,3.6}){
    auto r=trial(1<<4,rise);
    std::printf("policy=%d rise=%.1f host=%04x ok=%d clkerr=%u slot=%u\n",
      CLOCK_FIRST,rise,r.host,r.ok,r.clk,r.slot);
    if(rise==0 && (!r.ok||r.host!=0x0080))return 2;
    if((rise==.3||rise==.7||rise==2.1||rise==3.0)
       &&(!r.ok||r.host!=0x1080))return 3;
    if(rise==3.6){
      if(CLOCK_FIRST){if(!r.ok||r.host!=0x3080||r.clk)return 4;}
      else{if(r.ok||r.host!=0x3040||r.clk!=1||r.slot!=12)return 5;}
    }
  }
  std::puts("LIMIT: this is a synthetic timeline, not current physical DATA measurement");
}
'''

def run():
    if not shutil.which('g++'): raise RuntimeError('g++ missing')
    source=SOURCE.read_text()
    original=extract(source)
    # The only experimental change: IN MEMORY. Never write to production source.
    old='complete = wait_data(true, EDGE_TIMEOUT_US);\n  if (complete) data_release();'
    assert original.count(old)==1
    policies=[('protected', original, 'false'),
              ('hypothetical_clock_first',
               original.replace(old,'complete = true;\n  data_release();'),'true')]
    for name,code,flag in policies:
        with tempfile.TemporaryDirectory() as tmp:
            c=Path(tmp)/'main.cpp'; exe=Path(tmp)/'main'
            c.write_text(GLOBALS+MOCK+code+MAIN.replace('CLOCK_FIRST',flag))
            result=subprocess.run(['g++','-std=c++17','-O2','-Wall','-Wextra',
                                   '-Werror',str(c),'-o',str(exe)],
                                  text=True,capture_output=True)
            if result.returncode: raise RuntimeError(name+' COMPILE:\n'+result.stderr)
            result=subprocess.run([str(exe)],text=True,capture_output=True)
            print(name+':\n'+result.stdout)
            if result.returncode: raise RuntimeError(name+' TEST:\n'+result.stderr)
    print('PASS: exact repository emit_frame() body, both policies; zero firmware writes')

if __name__=='__main__': run()
