#!/usr/bin/env python3
"""SRC + HW-constrained MODEL: replay true P0 burst HIGH-window budget.

Actual protected XGO-CE emit_frame() body is extracted and compiled.
The P0 derived waveform has mean low 33.1/12us and mean intervening
high (48.1-33.1)/11us, from a SINGLE complete 10MHz hardware capture.
Only modeled polling/read costs are swept. NO timing in this test is a
measurement of RP2040's real USB-PHY read polling cadence.
"""
from pathlib import Path
import shutil
import subprocess
import tempfile
from test_responder_compiled_mock import extract
from test_exact_xgo_frame_phase import GLOBALS, MOCK, MAIN as PREVIOUS_MAIN, SOURCE

# Source timing model is injected through fake GPIO functions, not through
# production emit_frame(). Each fake time_us_32 / clock_level / data_level
# advances a tunable virtual time. Do NOT infer any clock cycles from this.
PHYS_LOW=(2.7,2.8,2.7,3.0,2.8,2.5,2.5,3.0,2.7,2.7,2.9,2.8)
assert len(PHYS_LOW)==12
LOW_TOTAL=sum(PHYS_LOW)
P0_BURST=48.1
HIGH_TOTAL=P0_BURST-LOW_TOTAL
P0_HIGH=HIGH_TOTAL/11
P0_LOW=LOW_TOTAL/12
P0_PERIOD=(P0_BURST-P0_LOW)/11
assert abs(P0_HIGH-1.36363636)<1e-6

mock=MOCK
assert mock.count("constexpr double first_fall=1.2, low_width=2.0, period=4.0;")==1
mock=mock.replace("constexpr double first_fall=1.2, low_width=2.0, period=4.0;",
                  "constexpr double first_fall=1.2;\n"
                  "double low_width=2.0, period=4.0;\n"
                  "double observation_us=.035, arming_phase_us=0;")
assert mock.count("now+=0.035;")==3
mock=mock.replace("now+=0.035;", "now+=observation_us;")

# The original trial() sets now=-6. This is harmless when frames finish, but
# failure sets static require_idle_high: use a fresh *process* for each risky
# point, so every physical mask/time window begins as a clean independent run.
MAIN = r'''
int main(int argc,char**argv){
  if(argc!=5)return 90;
  int mode=std::atoi(argv[1]);       // 0 = older ideal 2/2; 1 = P0-derived
  observation_us=std::atof(argv[2]);
  arming_phase_us=std::atof(argv[3]);
  uint16_t mask=(uint16_t)std::strtoul(argv[4],nullptr,0);
  if(mode==1){
    low_width=P0_LOW;
    period=P0_PERIOD;
  }
  now=-6.0+arming_phase_us;
  data_rise=0;sink=false;history.clear();
  published_mask.store(mask);
  xgo_diag_clock_timeouts.store(0);
  xgo_diag_last_failure_slot.store(0);
  bool ok=emit_frame();
  uint16_t decoded=received(), expected=to_host(mask);
  std::printf("%d %d %04x %04x %u %u\n",
    mode,ok,decoded,expected,xgo_diag_clock_timeouts.load(),
    xgo_diag_last_failure_slot.load());
  return 0; // Python reports failures as observations, not test harness errors
}
'''
MAIN = (f"constexpr double P0_LOW={P0_LOW:.12f};\n"
        f"constexpr double P0_PERIOD={P0_PERIOD:.12f};\n"
        + "#include <cstdlib>\n" + MAIN)

def compile_mock(tmp):
    c=tmp/"probe.cpp"; exe=tmp/"probe"
    c.write_text(GLOBALS+mock+extract(SOURCE.read_text())+
                 PREVIOUS_MAIN.split("static uint16_t const masks[12]")[0]+
                 # Host reconstruction helpers are defined by the previous
                 # source test; extract just its helpers before test main.
                 PREVIOUS_MAIN.split("int main(){")[0]+MAIN)
    result=subprocess.run(["g++","-std=c++17","-O2","-Wall","-Wextra",
                           "-Werror",str(c),"-o",str(exe)],
                          capture_output=True,text=True)
    if result.returncode:
        raise RuntimeError("compile exact source:\n"+result.stderr)
    return exe

def execute(exe,mode,step,phase,mask):
    x=subprocess.run([str(exe),str(mode),str(step),str(phase),hex(mask)],
                     text=True,capture_output=True)
    if x.returncode:
        raise RuntimeError(x.stderr or x.stdout)
    m,ok,read,want,err,slot=x.stdout.strip().split()
    return (ok=="1",read==want,int(read,16),int(err),int(slot))

def run():
    assert shutil.which("g++")
    print(f"HW P0: 12 LOW sum {LOW_TOTAL:.1f}us in {P0_BURST:.1f}us burst; "
          f"11 HIGH sum {HIGH_TOTAL:.1f}us; mean LOW {P0_LOW:.3f}us, "
          f"mean HIGH {P0_HIGH:.3f}us; mean FALL period {P0_PERIOD:.3f}us")
    profiles=[("ideal-2/2",0),("P0-average-2.76/1.36",1)]
    steps=[.035,.10,.20,.35,.50,.70,1.00,1.50]
    phases=[0,.1,.2,.3,.4,.5,.6,.7,.8,.9,1.0,1.1,1.2]
    masks=[0,1<<4,1<<5,(1<<0)|(1<<4),1<<11,0xfff]
    first_bad={}
    with tempfile.TemporaryDirectory() as td:
        exe=compile_mock(Path(td))
        for label,mode in profiles:
            for step in steps:
                bad_word=bad_frame=clock_err=0
                examples=[]
                for phase in phases:
                    for mask in masks:
                        ok,correct,word,err,slot=execute(exe,mode,step,phase,mask)
                        bad_word+=not correct
                        bad_frame+=not ok
                        clock_err+=bool(err)
                        if (not ok or not correct) and len(examples)<2:
                            examples.append((phase,hex(mask),hex(word),err,slot))
                if bad_word or bad_frame:
                    first_bad.setdefault(label,(step,bad_word,bad_frame))
                print(f"{label:23s} modeled_step={step:4.3f}us "
                      f"n={len(phases)*len(masks):3d} wrong_words={bad_word:3d} "
                      f"failed_frames={bad_frame:3d} clock_errors={clock_err:3d} "
                      f"examples={examples}")
        assert "P0-average-2.76/1.36" in first_bad, (
            "Expected a high modeled observation step to expose some window limits")
        print("PASS: compiled protected responder, P0-derived waveform compared to older model")
        print("LIMIT: modeled observation step NOT measured native RP2040 loop latency")
        print("LIMIT: mean HIGH from one historical P0 frame, NOT current Frankie waveform")
if __name__=="__main__":run()
