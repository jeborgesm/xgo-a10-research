#!/usr/bin/env python3
"""Real Polish02 emit_frame C++ vs 25us synthetic host-IRQ CLOCK stretches.

This verifies only CLOCK wait tolerance, not DATA voltage or idle ghost cure.
The old 18us protected responder must remain protected and continue to FAIL
these synthetic long-clock cases; this candidate only changes CLOCK timeout.
"""
from pathlib import Path
import shutil
import subprocess
import tempfile

from test_responder_compiled_mock import extract
from test_xgo_irq_stretched_clock_exact_cpp import GLOBALS, STALLED

ROOT=Path("integrations/gp2040ce-xgo-test01/candidates")
PROTECTED=ROOT/"offline-test44-transparent-controller/XGODriver.cpp"
CANDIDATE=ROOT/"offline-polish02-clock-tolerance/XGODriver.cpp"

MAIN=r"""
int main(int argc,char**argv){
  if(argc!=2)return 90;
  fault=(unsigned)std::atoi(argv[1]);
  if(fault!=0 && !(fault>=20&&fault<=31)
      && !(fault>=40&&fault<=50))return 91;
  published_mask.store(1u<<4); // A stays held across BOTH real XGO scans
  const bool first=emit_frame();
  const double first_done=now;
  const bool second=emit_frame();
  uint16_t next_word=host_word(1);
  uint32_t errors=xgo_diag_clock_timeouts.load();
  uint32_t failed=xgo_diag_active_failures.load();
  std::printf("case=%u first=%d second=%d next=%04x clkerr=%u "
              "active_fail=%u t0=%.2f\n",
              fault,first,second,next_word,errors,failed,first_done);
  if(!first || !second || next_word!=0x0080 || errors || failed)
    return 1;
  std::puts("PASS physical held state survives IRQ-stretched CLOCK");
}
"""

def compile_cpp(src,out):
    cpp=out.with_suffix(".cpp")
    # extract() selects emit_frame() only; preserve its source-defined global
    # CLOCK timeout when linking the host C++ harness.
    header=GLOBALS
    if src==CANDIDATE:
        assert "constexpr uint32_t CLOCK_TIMEOUT_US = 48;" in src.read_text()
        header+="constexpr uint32_t CLOCK_TIMEOUT_US = 48;\n"
    cpp.write_text(header+STALLED+extract(src.read_text())+MAIN)
    build=subprocess.run(
        ["g++","-std=c++17","-O2","-Wall","-Wextra","-Werror",
         str(cpp),"-o",str(out)],text=True,capture_output=True)
    if build.returncode:raise RuntimeError(build.stderr)

def test():
    if not shutil.which("g++"):raise RuntimeError("g++ missing")
    original=PROTECTED.read_text()
    variant=CANDIDATE.read_text()
    old="constexpr uint32_t EDGE_TIMEOUT_US = 18;"
    assert original.count(old)==1
    new="constexpr uint32_t EDGE_TIMEOUT_US = 18;\nconstexpr uint32_t CLOCK_TIMEOUT_US = 48;"
    text=variant.replace(new,old).replace("wait_clock(false, CLOCK_TIMEOUT_US)","wait_clock(false, EDGE_TIMEOUT_US)").replace("wait_clock(true, CLOCK_TIMEOUT_US)","wait_clock(true, EDGE_TIMEOUT_US)")
    # Comments intentionally differ; compare executable code after stripping comments.
    import re
    def strip_comments(x):
        return re.sub(r"/\*.*?\*/|//[^\n]*","",x,flags=re.S)
    assert re.findall(r"\w+|[^\s\w]",strip_comments(text))==re.findall(r"\w+|[^\s\w]",strip_comments(original)),"Polish02 changed more than CLOCK waits"
    assert variant.count("wait_data(true, EDGE_TIMEOUT_US)")==1,"DATA release budget must stay 18us"
    assert variant.count("CLOCK_TIMEOUT_US")==5,"expected four CLOCK checks + declaration"
    scenarios=[0,*range(20,32),*range(40,51)]
    with tempfile.TemporaryDirectory() as td:
        folder=Path(td)
        oldexe=folder/"old"
        newexe=folder/"new"
        compile_cpp(PROTECTED,oldexe)
        compile_cpp(CANDIDATE,newexe)
        old_fail=0
        for scen in scenarios:
            r=subprocess.run([str(newexe),str(scen)],capture_output=True,text=True)
            print("Polish02",r.stdout.strip().replace("\n"," | "))
            if r.returncode:raise RuntimeError("Candidate case "+str(scen)+": "+r.stdout+r.stderr)
            if scen:
                old=subprocess.run([str(oldexe),str(scen)],capture_output=True,text=True)
                old_fail += (old.returncode != 0)
        assert old_fail>=20,("Protected responder unexpectedly survives most 25us pauses",old_fail)
        print(f"PASS Polish02 {len(scenarios)} exact-C++ cases; original fails {old_fail}/23 stretched cases")
        print("LIMIT: synthetic host IRQ duration 25us is not measured on user's XGO")
        print("LIMIT: no claim of ghost-jump repair or current PHY DATA analog behavior")

if __name__=="__main__":test()
