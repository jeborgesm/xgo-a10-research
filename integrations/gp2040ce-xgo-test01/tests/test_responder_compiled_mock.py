#!/usr/bin/env python3
"""Compile and exercise the actual Test49/Candidate C++ emit_frame() body.

Replace the physical pin operations with deterministic scripted inputs. The
production function is extracted directly from the repository source, not
reimplemented in Python. This is a *software handshake mock*, NOT a physical
waveform capture or host-decoder simulation.

Run from repo root: python3 integrations/gp2040ce-xgo-test01/tests/test_responder_compiled_mock.py
Requires host g++.
"""
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path("integrations/gp2040ce-xgo-test01/candidates")
SOURCES = (
    ("Test49", ROOT / "test49-attack-edge-provenance/XGODriver.cpp", True),
    ("native-postamble-candidate", ROOT / "offline-terminal-postamble/XGODriver.cpp", False),
    ("SPSC-RAM-candidate", ROOT / "offline-spsc-ram-hotpath/XGODriver.cpp", True),
    ("Test44-playable-SPSC", ROOT / "offline-test44-spsc-ram-playable/XGODriver.cpp", True),
    ("Test44-coherent-SPSC", ROOT / "offline-test44-spsc-coherent-ram/XGODriver.cpp", True),
)

PRELUDE = r"""
#include <atomic>
#include <cstdint>
#include <cstdio>
#include <stdexcept>
#include <vector>
using std::memory_order_relaxed;

// Declaration must precede run_frame(), which calls the extracted body.
bool emit_frame();

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
std::atomic<uint32_t> attack_edge_commit_seq{0};
uint32_t core0_attack_commit_counter=0;
uint16_t attack_pulse_mask = 0;
uint32_t attack_pulse_start_us = 0;
bool previous_active_success = false;
uint32_t active_failure_streak = 0;
constexpr uint16_t ATTACK_BITS = 0x003fu;
constexpr uint32_t ATTACK_PULSE_US = 18000;
constexpr uint32_t EDGE_TIMEOUT_US = 18;
constexpr uint32_t LOAD_TIMEOUT_US = 20000;

struct Step { char type; bool level; bool outcome; };
std::vector<Step> script;
size_t cursor = 0;
uint32_t tick = 10;
bool sinking = false;
unsigned slot_seen = 0;
uint16_t sampled_mask = 0;
bool saw_load_low = false;
bool sampled_slot0 = false;
bool model_host_sampled_release_too_early = false;

uint32_t time_us_32() { return tick++; }
uint32_t save_and_disable_interrupts() { return 0; }
void restore_interrupts(uint32_t) {}
void data_release() { sinking = false; }
void data_sink() { sinking = true; }
bool next(char kind, bool level) {
    if (cursor >= script.size()) throw std::runtime_error("Responder read past scripted host events");
    Step s = script[cursor++];
    if (s.type != kind || s.level != level)
        throw std::runtime_error("Responder expected a different CLOCK/DATA event");
    ++tick;
    return s.outcome;
}
bool wait_data(bool level, uint32_t) {
    const bool ok = next('D', level);
    if (ok && !level) saw_load_low = true;
    if (ok && level && saw_load_low && !sampled_slot0) {
        // XGO samples slot0 immediately at host LOAD release, before CLOCK.
        // Fault-injection simulates a slow DATA rise relative to that sample,
        // even though the firmware later observes DATA high.
        if (sinking || model_host_sampled_release_too_early) sampled_mask |= 1u;
        sampled_slot0 = true;
    }
    return ok;
}
bool wait_clock(bool level, uint32_t) {
    const bool ok = next('C', level);
    // For the special pre-driven R/slot0 path, the firmware never calls
    // wait_data(true). Fold that earlier host release event into this first
    // clock transition in the idealized mock (not a measured timestamp).
    if (ok && !level) {
        if (slot_seen == 0 && !sampled_slot0) {
            if (sinking) sampled_mask |= 1u;
            sampled_slot0 = true;
        }
        ++slot_seen;
    } else if (ok && level && slot_seen >= 1 && slot_seen < 12) {
        if (sinking) sampled_mask |= 1u << slot_seen;
    }
    return ok;
}
void push(char type, bool level, bool outcome = true) {
    script.push_back(Step{type, level, outcome});
}
void frame_script(uint16_t expected, bool rearm, int failure_slot = -1,
                  bool failure_is_rise = false, bool final_high = true) {
    if (rearm) push('D', true);
    push('D', false);     // Host's LOAD-low acquisition.
    if (!(expected & 1u)) push('D', true); // R/slot0 has special pre-drive path.
    for (int slot = 1; slot < 12; ++slot) {
        const bool fail_fall = slot == failure_slot && !failure_is_rise;
        push('C', false, !fail_fall);
        if (fail_fall) return;
        const bool fail_rise = slot == failure_slot && failure_is_rise;
        push('C', true, !fail_rise);
        if (fail_rise) return;
    }
    push('C', false); // Terminal falling edge (after transmitting slot11).
    push('C', true, final_high);
}
void check(bool condition, const char* message) {
    if (!condition) throw std::runtime_error(message);
}
void run_frame(uint16_t mask, bool rearm, bool expected_success,
               int failure_slot = -1, bool fail_rise = false, bool final_high = true,
               bool inject_slot0_false_low = false) {
    script.clear(); cursor = 0; slot_seen = 0; sampled_mask = 0;
    saw_load_low = false; sampled_slot0 = false;
    model_host_sampled_release_too_early = inject_slot0_false_low;
    sinking = false;
    published_mask.store(mask);
    pending_press_edges.store(mask & ATTACK_BITS);
    attack_edge_commit_seq.store(0);
    core0_attack_commit_counter=0;
    for (unsigned bit = 0; bit < 6; ++bit) {
        attack_edge_generation[bit].store((mask >> bit) & 1u);
        consumed_attack_edge_generation[bit] = 0;
    }
    attack_pulse_mask = 0;
    frame_script(mask, rearm, failure_slot, fail_rise, final_high);
    const bool complete = emit_frame();
    check(complete == expected_success, "Unexpected frame success/failure");
    check(cursor == script.size(), "Unconsumed scripted host event");
    check(!sinking, "DATA must be released after every attempt");
    if (failure_slot == -1) {
        const uint16_t expected = mask | (inject_slot0_false_low ? 1u : 0u);
        check(sampled_mask == expected, "Unexpected decoded bits in ideal or injected release");
    } else {
        // Successful slots seen by the mock cannot invent a foreign bit.
        check(!(sampled_mask & ~mask), "Partial serial output invented another pressed bit");
    }
}
"""

# The real emit_frame() is inserted between PRELUDE and MAIN after a prototype.
# Every emitted frame uses the real core logic, diagnostics, and recovery path.
MAIN = r"""
int main() {
    constexpr bool gp_treats_terminal_high_failure_as_error = POSTAMBLE_FAILS;
    const uint16_t RIGHT = 1u << 11;
    const uint16_t FIRE = 1u << 5;
    const uint16_t JUMP = 1u << 0;  // HW fixed-R Contra jump proof.
    const uint16_t START = 1u << 7;

    // Exhaustive ideal-slot test over every twelve-bit mask.
    for (uint16_t mask = 0; mask < 4096; ++mask) {
        run_frame(mask, false, true);
    }

    // Nominal RIGHT+FIRE never emits JUMP or START in source-level serialization.
    check(((RIGHT | FIRE) & (JUMP | START)) == 0, "Invalid bit identities");
    run_frame(RIGHT | FIRE, false, true);
    // Hypothetical DATA threshold recovery lag: host samples slot0 low during
    // LOAD release, despite firmware having no R press and later seeing high.
    // This is a modeled electrical boundary case, NOT a measured failure.
    run_frame(RIGHT | FIRE, false, true, -1, false, true, true);

    // Final high fails AFTER all 12 slots were sent. Real source policy differs.
    run_frame(RIGHT | FIRE, false,
              !gp_treats_terminal_high_failure_as_error,
              -1, false, false);
    // Legacy source calls require_idle_high on next frame; proposed version does not.
    run_frame(RIGHT | FIRE, gp_treats_terminal_high_failure_as_error, true);

    // Mid-frame failures are real errors for both source versions.
    // In each case the next acquisition first sees DATA high to rearm.
    for (int slot = 1; slot < 12; ++slot) {
        for (int fail_rise = 0; fail_rise < 2; ++fail_rise) {
            run_frame(RIGHT | FIRE, false, false, slot, fail_rise != 0);
            run_frame(RIGHT | FIRE, true, true);
        }
    }
    std::printf("PASS exact extracted C++ responder: 4096 ideal masks,"
                " 22 mid-frame abort/recovery pairs, slot0 early-sample injection, final postamble policy\n");
}
"""

def extract(source):
    # The SRAM attribute is stripped only in the host-native mock compilation,
    # never in the actual pinned RP2040 candidate or its ELF audit.
    source = source.replace("bool __no_inline_not_in_flash_func(emit_frame)() {",
                            "bool emit_frame() {")
    start = source.index("bool emit_frame() {")
    end = source.index("\n}\n\n} // namespace", start) + 2
    function = source[start:end]
    assert function.count("bool emit_frame()") == 1
    assert ("pending_press_edges.exchange(0, std::memory_order_acq_rel)" in function
            or "attack_edge_generation[bit].load(std::memory_order_acquire)" in function
            or "attack_edge_generation[bit].load(std::memory_order_seq_cst)" in function)
    assert "if (!complete) require_idle_high = true;" in function
    return function

def run():
    if not shutil.which("g++"):
        raise RuntimeError("A host C++ compiler (g++) is required")
    with tempfile.TemporaryDirectory(prefix="xgo-responder-mock-") as tmp:
        for name, path, tail_failure_expected in SOURCES:
            source = path.read_text()
            function = extract(source)
            code = (PRELUDE + "\nbool emit_frame();\n" + function + "\n" +
                    MAIN.replace("POSTAMBLE_FAILS", "true" if tail_failure_expected else "false"))
            src = Path(tmp) / (name + ".cpp")
            exe = Path(tmp) / (name + ".bin")
            src.write_text(code)
            compile_result = subprocess.run(
                ["g++", "-std=c++17", "-O2", "-Wall", "-Wextra",
                 "-Werror", str(src), "-o", str(exe)],
                capture_output=True, text=True
            )
            if compile_result.returncode:
                raise RuntimeError(f"{name} mock C++ compilation failed:\\n"
                                   + compile_result.stderr)
            p = subprocess.run([str(exe)], check=True, capture_output=True, text=True)
            print(name + ": " + p.stdout.strip())
    print("LIMIT: scripted input levels, not a measured XGO CLOCK/DATA waveform")

if __name__ == "__main__":
    run()
