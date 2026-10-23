#!/usr/bin/env python3
"""Cortex-M0+ atomic implementation audit: SOURCE + COMPILER REFERENCE ONLY.

Test49 executes atomic work after detecting XGO LOAD-low and before the
host's immediate slot0 read. On ARMv6-M (no LDREX/STREX) library calls can
appear for shared atomic reads and read-modify-writes. This miniature C
compilation is NOT a disassembly of linked GP2040-CE, whose symbols must
be separately checked using the existing full-ELF RAM audit.
"""
from pathlib import Path
import shutil
import subprocess
import tempfile

driver=Path("integrations/gp2040ce-xgo-test01/candidates/test49-attack-edge-provenance/XGODriver.cpp").read_text()
begin=driver.index("bool emit_frame() {")
end=driver.index("} // namespace",begin)
critical=driver[begin:end]
load=critical.index("if (!wait_data(false, LOAD_TIMEOUT_US))")
irq=critical.index("save_and_disable_interrupts()")
masked=critical.index("published_mask.load(std::memory_order_acquire)")
exchange=critical.index("pending_press_edges.exchange(0, std::memory_order_acq_rel)")
compose=critical.index("const uint16_t mask =")
release=critical.index("complete = wait_data(true, EDGE_TIMEOUT_US)")
firstclock=critical.index("if (!wait_clock(false, EDGE_TIMEOUT_US))")
assert load < irq < masked < exchange < compose < release < firstclock
assert "std::atomic<uint16_t> published_mask" in driver
assert "std::atomic<uint16_t> pending_press_edges" in driver
assert "pending_press_edges.fetch_or(rising, std::memory_order_release)" in driver
print("PASS: Test49 masks Core1 interrupts and uses shared uint16 atomics after LOAD acquisition before slot0 / first CLOCK")

clang=shutil.which("clang")
if clang is None:
    print("SKIP: no clang cross compiler for independent ARMv6-M reference")
else:
    c_code=r"""
    typedef unsigned short uint16_t;
    uint16_t load16(uint16_t *p) { return __atomic_load_n(p, __ATOMIC_ACQUIRE); }
    uint16_t exchange16(uint16_t *p) { return __atomic_exchange_n(p, 0, __ATOMIC_ACQ_REL); }
    uint16_t fetch_or16(uint16_t *p,uint16_t bits) { return __atomic_fetch_or(p,bits,__ATOMIC_RELEASE); }
    """
    with tempfile.TemporaryDirectory() as d:
        source=Path(d)/"atomic.c"; asm=Path(d)/"atomic.s"
        source.write_text(c_code)
        r=subprocess.run([clang,"--target=armv6m-none-eabi","-mcpu=cortex-m0plus",
                          "-mthumb","-O2","-S",str(source),"-o",str(asm)],
                         capture_output=True,text=True)
        if r.returncode: raise RuntimeError("ARMv6-M clang reference compilation failed:\n"+r.stderr)
        text=asm.read_text()
        for name in ("__atomic_load_2","__atomic_exchange_2","__atomic_fetch_or_2"):
            assert name in text, f"Clang did not emit reference helper {name}"
        print("PASS ARMv6-M clang reference: uint16 atomic LOAD/EXCHANGE/FETCH_OR compile as __atomic_*_2 calls")
        print("LIMIT: GCC GP2040-CE source/ELF, actual helper memory placement, and latency remain unverified")
