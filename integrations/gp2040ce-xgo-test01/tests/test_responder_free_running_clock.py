#!/usr/bin/env python3
"""Compile the actual Test49 emit_frame() against a free-running host CLOCK.

Unlike the older scripted-edge mock, CLOCK and LOAD advance independently of
the responder. The harness can inject hypothetical firmware stalls and DATA
settling time. No such fault duration is asserted as an XGO measurement.

Run: python3 integrations/gp2040ce-xgo-test01/tests/test_responder_free_running_clock.py
"""
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path('integrations/gp2040ce-xgo-test01/candidates')
SOURCES = (
    ('Test49', ROOT / 'test49-attack-edge-provenance/XGODriver.cpp'),
    ('postamble-only', ROOT / 'offline-terminal-postamble/XGODriver.cpp'),
    ('SPSC-RAM', ROOT / 'offline-spsc-ram-hotpath/XGODriver.cpp'),
)

PRELUDE = r"""
#include <atomic>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <stdexcept>
using std::memory_order_relaxed;

std::atomic<uint32_t> xgo_diag_load_timeouts{0};
std::atomic<uint32_t> xgo_diag_release_timeouts{0};
std::atomic<uint32_t> xgo_diag_clock_timeouts{0};
std::atomic<uint32_t> xgo_diag_clock_low_failures{0};
std::atomic<uint32_t> xgo_diag_clock_high_failures{0};
std::atomic<uint32_t> xgo_diag_last_failure_slot{0};
std::atomic<uint32_t> xgo_diag_clock_failure_slots[13]{};
std::atomic<uint32_t> xgo_diag_load_low_last_us{0};
std::atomic<uint32_t> xgo_diag_load_low_max_us{0};
std::atomic<uint32_t> xgo_diag_right_attack_attempts{0};
std::atomic<uint32_t> xgo_diag_right_attack_failures{0};
std::atomic<uint32_t> xgo_diag_active_attempts{0};
std::atomic<uint32_t> xgo_diag_active_failures{0};
std::atomic<uint32_t> xgo_diag_fail_after_success{0};
std::atomic<uint32_t> xgo_diag_consecutive_active_failures{0};
std::atomic<uint32_t> xgo_diag_max_active_failure_streak{0};
std::atomic<uint16_t> published_mask{0};
std::atomic<uint16_t> pending_press_edges{0};
std::atomic<uint32_t> attack_edge_generation[6]{};
uint32_t consumed_attack_edge_generation[6]{};
uint16_t attack_pulse_mask=0;
uint32_t attack_pulse_start_us=0;
bool previous_active_success=false;
uint32_t active_failure_streak=0;
constexpr uint16_t ATTACK_BITS=0x003fu;
constexpr uint32_t ATTACK_PULSE_US=18000;
constexpr uint32_t EDGE_TIMEOUT_US=18;
constexpr uint32_t LOAD_TIMEOUT_US=20000;

bool emit_frame();

struct Host {
    double us=0;
    bool sink=false;
    double load_begin=12.0;
    double load_end=19.2;      // 7.2 us LOW, within P0 HW 6.8-7.5 us.
    double first_fall=20.4;    // 1.2 us after release, within P0 HW 0.9-1.3 us.
    double period=4.0;        // ~2us low + ~2us high from P0.
    double half=2.0;
    double sample_slot0_delta=.10; // HYPOTHETICAL: exact host sample offset unmeasured.
    double gpio_recover_delay=0;   // HYPOTHETICAL delay after LOAD release.
    double irq_entry_delay=0;      // HYPOTHETICAL delay after detecting LOAD-low.
    double after_fire_high_delay=0;// HYPOTHETICAL wait-clock return gap after slot5.
    unsigned clock_high_returns=0;
    int sample_index=0;
    uint16_t decoded=0;
} host;

bool host_load_low_at(double t) {
    return t >= host.load_begin && t < host.load_end;
}
bool bus_low_at(double t) {
    return host.sink || host_load_low_at(t) ||
        (t >= host.load_end && t < host.load_end + host.gpio_recover_delay);
}
double sample_at(int slot) {
    if (slot==0) return host.load_end + host.sample_slot0_delta;
    return host.first_fall + (slot-1)*host.period + host.half + 0.10;
}
void advance(double duration) {
    if (duration < 0) throw std::runtime_error("negative model time");
    const double until=host.us + duration;
    while (host.sample_index < 12 &&
           sample_at(host.sample_index) <= until) {
        // DATA low means button asserted; host drives LOAD low only before slot0.
        if (bus_low_at(sample_at(host.sample_index)))
            host.decoded |= uint16_t(1u << host.sample_index);
        ++host.sample_index;
    }
    host.us=until;
}
uint32_t time_us_32() {
    uint32_t val = uint32_t(std::floor(host.us));
    advance(0.08);
    return val;
}
uint32_t save_and_disable_interrupts() {
    advance(host.irq_entry_delay);
    return 0;
}
void restore_interrupts(uint32_t) {}
void data_release() { host.sink=false; advance(.08); }
void data_sink() { host.sink=true; advance(.08); }
bool clock_high_at(double t) {
    if (t < host.first_fall) return true;
    double x = t - host.first_fall;
    if (x >= 12.0*host.period) return true; // Finished 12 clock pulses.
    return std::fmod(x, host.period) >= host.half;
}
bool wait_data(bool expected, uint32_t deadline) {
    const uint32_t started=time_us_32();
    for (;;) {
        bool level=!bus_low_at(host.us);
        advance(.12);
        if (level==expected) return true;
        if ((uint32_t)(time_us_32()-started)>deadline) return false;
    }
}
bool wait_clock(bool expected, uint32_t deadline) {
    const uint32_t started=time_us_32();
    for (;;) {
        const bool level=clock_high_at(host.us);
        advance(.12);
        if (level==expected) {
            if (expected) {
                ++host.clock_high_returns;
                if (host.clock_high_returns==5)
                    advance(host.after_fire_high_delay);
            }
            return true;
        }
        if ((uint32_t)(time_us_32()-started)>deadline) return false;
    }
}
void require(bool value,const char *what) {
    if (!value) throw std::runtime_error(what);
}
void init_host(uint16_t pressed, double delay=0, double recovery=0,
               double after_fire_high=0) {
    host=Host{};
    host.irq_entry_delay=delay;
    host.gpio_recover_delay=recovery;
    host.after_fire_high_delay=after_fire_high;
    published_mask.store(pressed);
    pending_press_edges.store(pressed & ATTACK_BITS);
    for (unsigned bit=0; bit<6; ++bit) {
        attack_edge_generation[bit].store((pressed >> bit) & 1u);
        consumed_attack_edge_generation[bit]=0;
    }
    attack_pulse_mask=0;
}
"""

MAIN = r"""
int main() {
    constexpr uint16_t RIGHT=1u<<11, FIRE=1u<<5, JUMP_R=1u<<0, START=1u<<7;
    // Each complete frame has 12 explicit host sample moments independent
    // of when the responder polls CLOCK. The mock does not force the next
    // requested event to occur, unlike the earlier scripted-edge mock.
    int passed=0, nominal_failures=0;
    for (int mask=0;mask<4096;++mask) {
        init_host(uint16_t(mask));
        bool complete=emit_frame();
        if (!complete || host.decoded!=mask)
            ++nominal_failures;
        else
            ++passed;
    }
    // A 4-6us timeout is shorter than some simulated ordinary wait/check
    // schedules; report the modeled nominal regression rather than treating
    // every timeout budget as proven safe for this virtual CPU.
    if (EXPECT_NOMINAL_PASS) {
        require(nominal_failures==0,"Nominal free-running host handshake failed");
    } else {
        require(nominal_failures>0,
                "Expected modeled over-tight CLOCK timeout to fail normal polling");
        std::printf("tight-timeout control: %d/4096 nominal failures on synthetic host\\n",
                    nominal_failures);
        return 0;
    }
    init_host(RIGHT|FIRE);
    require(emit_frame(),"RIGHT+FIRE clean frame should complete");
    require(host.decoded==(RIGHT|FIRE),"RIGHT+FIRE clean host mismatch");

    // Synthetic threshold lag: although software emits no R, the
    // independent host initially samples DATA as LOW immediately after
    // releasing its LOAD-low pulse. It subsequently rises before CLOCK.
    init_host(RIGHT|FIRE,0,.35);
    require(emit_frame(),"Synthetic slot0 settle lag should complete");
    require(host.decoded==(RIGHT|FIRE|JUMP_R),
            "Synthetic slow DATA rise must cause isolated slot0 false jump");

    // Model a CPU stall after completing FIRE slot5 CLOCK-high handshake.
    // A sufficiently long stall leaves FIRE asserted while host advances
    // through SELECT/START clock cycles. Later level-based clock wait
    // accepts some FUTURE low phase as the expected next slot.
    init_host(RIGHT|FIRE,0,0,9.0);
    bool completed=emit_frame();
    require((host.decoded&START)!=0,
            "Delayed FIRE release should assert host START in synthetic case");
    require((host.decoded&JUMP_R)==0,
            "The delayed-FIRE START counterexample should not assert R");
    const uint16_t late_fire_decoded=host.decoded;
    const uint32_t late_fire_clock_errors=xgo_diag_clock_timeouts.load();

    // Sweep hypothetical Core1 stalls in quarter-microsecond increments.
    // They are NOT claimed to be measured firmware execution delays.
    // The host's 12 CLOCK pulses continue regardless of responder progress.
    double first_fire_delay_causing_START=-1;
    double first_load_prep_delay_causing_START=-1;
    unsigned fire_false_actions=0, prep_false_actions=0;
    unsigned fire_host_wrong_but_reported_ok=0;
    for (int q=0; q<=64; ++q) {
        const double hypothetical_delay=q*0.25;
        init_host(RIGHT|FIRE,0,0,hypothetical_delay);
        bool ok=emit_frame();
        if (host.decoded & START) {
            if (first_fire_delay_causing_START<0)
                first_fire_delay_causing_START=hypothetical_delay;
            ++fire_false_actions;
        }
        if (ok && host.decoded != (RIGHT|FIRE))
            ++fire_host_wrong_but_reported_ok;
    }
    for (int q=0; q<=80; ++q) {
        const double hypothetical_delay=q*0.25;
        init_host(RIGHT|FIRE,hypothetical_delay,0,0);
        xgo_diag_clock_timeouts.store(0);
        xgo_diag_last_failure_slot.store(0);
        bool done=emit_frame();
        if (host.decoded & START) {
            if (first_load_prep_delay_causing_START<0)
                std::printf("first prep START: delay=%.2fus decoded=0x%03x "
                            "complete=%d last_failure_slot=%u clock_errors=%u\\n",
                            hypothetical_delay,unsigned(host.decoded),int(done),
                            unsigned(xgo_diag_last_failure_slot.load()),
                            unsigned(xgo_diag_clock_timeouts.load()));
            if (first_load_prep_delay_causing_START<0)
                first_load_prep_delay_causing_START=hypothetical_delay;
            ++prep_false_actions;
        }
    }
    // Compare the independent host's final-slot failure classification against
    // wrong-button decoding. A slot-12 error is NOT automatically a bad bit.
    unsigned slot12_without_wrong_bit=0,slot12_with_wrong_bit=0;
    unsigned slot12_with_false_START=0, slot11_with_false_START=0;
    for (int q=0;q<=100;++q) {
        init_host(RIGHT|FIRE,q*0.25,0,0);
        xgo_diag_clock_timeouts.store(0);
        xgo_diag_last_failure_slot.store(0);
        (void)emit_frame();
        if (xgo_diag_clock_timeouts.load()) {
            const auto last=xgo_diag_last_failure_slot.load();
            if (last==12) {
                if (host.decoded==(RIGHT|FIRE)) ++slot12_without_wrong_bit;
                else ++slot12_with_wrong_bit;
                if (host.decoded & START) ++slot12_with_false_START;
            }
            if (last==11 && (host.decoded & START)) ++slot11_with_false_START;
        }
    }
    std::printf("model diagnostic correlation: S12 failures with clean host "
                "word=%u; S12 failures with mismatched host word=%u; "
                "S12+falseSTART=%u; S11+falseSTART=%u\\n",
                slot12_without_wrong_bit,slot12_with_wrong_bit,
                slot12_with_false_START,slot11_with_false_START);
        require(first_fire_delay_causing_START>0 && first_fire_delay_causing_START<=9.0,
            "Expected a reproducible late-FIRE false START in sweep");
    std::printf("synthetic sweep: first FIRE-processing gap yielding START=%.2fus "
                "(%u cases); first LOAD-prep gap yielding START=%.2fus "
                "(%u cases); complete-but-wrong FIRE-gap cases=%u\n",
                first_fire_delay_causing_START,fire_false_actions,
                first_load_prep_delay_causing_START,prep_false_actions,
                fire_host_wrong_but_reported_ok);
    std::printf("source=C++ masks=%d; synthetic false-R=YES; "
                "synthetic late-FIRE START=YES; latter frame complete=%d, "
                "decoded=0x%03x, clock timeouts=%u\n",
                passed, int(completed), unsigned(late_fire_decoded),
                unsigned(late_fire_clock_errors));
}
"""

def extract(source):
    # Strip only the platform residency macro for the host-native simulator.
    source=source.replace('bool __no_inline_not_in_flash_func(emit_frame)() {',
                          'bool emit_frame() {')
    start=source.index('bool emit_frame() {')
    end=source.index('\n}\n\n} // namespace',start)+2
    function=source[start:end]
    assert 'wait_clock(false, EDGE_TIMEOUT_US)' in function
    assert 'if (!complete) require_idle_high = true;' in function
    return function

def main():
    if not shutil.which('g++'):
        raise RuntimeError('g++ host compiler required')
    with tempfile.TemporaryDirectory(prefix='xgo-clock-') as tmp:
        for label, path in SOURCES:
            source=path.read_text()
            for timeout in (18, 8, 6, 4):
                variant=f"{label}-edge-timeout-{timeout}us"
                cpp=Path(tmp)/(variant+'.cpp')
                prelude=PRELUDE.replace(
                    'constexpr uint32_t EDGE_TIMEOUT_US=18;',
                    f'constexpr uint32_t EDGE_TIMEOUT_US={timeout};')
                assert prelude != PRELUDE or timeout == 18
                cpp.write_text(prelude+'\n'+extract(source)+'\n'+MAIN.replace(
                    'EXPECT_NOMINAL_PASS', 'false' if timeout<=6 else 'true'))
                exe=Path(tmp)/(variant+'.exe')
                c=subprocess.run(['g++','-std=c++17','-O2','-Wall','-Wextra',
                                  '-Werror',str(cpp),'-o',str(exe)],
                                  capture_output=True,text=True)
                if c.returncode:
                    raise RuntimeError(variant+' failed to compile:\n'+c.stderr)
                r=subprocess.run([str(exe)],capture_output=True,text=True)
                if r.returncode:
                    raise RuntimeError(variant+' timing scenario failed:\n'+r.stderr)
                print(variant+': '+r.stdout.strip())
    print('LIMIT: virtual CLOCK/timing and injected stalls, not live hardware proof')

if __name__=='__main__':
    main()
