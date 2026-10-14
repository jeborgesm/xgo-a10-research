#include <atomic>
#include <cstdint>
#include <cassert>
#include <iostream>
uint32_t now_ms=0;
uint32_t get_absolute_time(){return now_ms;}
uint32_t to_ms_since_boot(uint32_t t){return t;}
struct Gamepad{uint16_t buttons;};
uint16_t map_mask(Gamepad*g){return g->buttons;}
std::atomic<uint32_t> xgo_hk_phase_state{0},xgo_hk_repeat_state{0},xgo_diag_mask_changes{0},xgo_diag_nonzero_to_zero{0},xgo_diag_zero_frames{0},xgo_diag_last_nonzero_mask{0},xgo_diag_output{0};
std::atomic<uint16_t> published_mask{0};
uint16_t previous_snapshot=0;
namespace xgo_hk_diag {
struct Phase { uint16_t on_ms, off_ms; uint8_t repeats; };
constexpr Phase kPhases[] = {
  {1000,1000,1}, // baseline hold
  {100,500,5},
  {50,500,5},
  {25,500,5},
  {10,500,5},
  {2000,1000,1}, // extended hold
};
constexpr uint8_t kPhaseCount = sizeof(kPhases)/sizeof(kPhases[0]);
constexpr uint16_t kHKMask = 1u;
class Sequencer {
public:
  void reset() { running_=false; phase_=0; repetition_=0; high_=false; last_pressed_=false; }
  uint16_t update(uint32_t now_ms, bool hk_pressed) {
    const bool rising = hk_pressed && !last_pressed_;
    last_pressed_=hk_pressed;
    if (!running_) {
      if (rising) { running_=true; phase_=0; repetition_=0; high_=false; deadline_=now_ms+2000u; }
      return 0;
    }
    // Wrap-safe deadline test; call at least once per 2^31 milliseconds.
    while (running_ && static_cast<int32_t>(now_ms-deadline_)>=0) {
      const Phase &p=kPhases[phase_];
      if (!high_) { high_=true; deadline_+=p.on_ms; }
      else {
        high_=false;
        deadline_+=p.off_ms;
        if (++repetition_>=p.repeats) {
          repetition_=0;
          if (++phase_>=kPhaseCount) { running_=false; high_=false; }
        }
      }
    }
    return running_ && high_ ? kHKMask : 0u;
  }
  bool running() const { return running_; }
  uint8_t phase() const { return phase_; }
  uint8_t repetition() const { return repetition_; }
private:
  bool running_=false, high_=false, last_pressed_=false;
  uint8_t phase_=0, repetition_=0;
  uint32_t deadline_=0;
};
} // namespace xgo_hk_diag
bool process(Gamepad *gamepad) {
 static xgo_hk_diag::Sequencer hk_sequence;
 static bool armed = false;
 static bool prev_chord = false;
 static bool prev_abort = false;
 static bool trigger_released = true;
 static bool swallow_chord_until_release = false;
 static bool swallow_trigger_until_release = false;
 const uint16_t physical = map_mask(gamepad);
 const bool select = (physical & (1u << 6)) != 0;
 const bool start = (physical & (1u << 7)) != 0;
 const bool hk = (physical & 1u) != 0;
 const bool chord = select && start && hk;
 const bool abort = select && start && !hk;
 const bool chord_edge = chord && !prev_chord;
 const bool abort_edge = abort && !prev_abort;
 prev_chord = chord;
 prev_abort = abort;
 if (abort_edge && (armed || hk_sequence.running())) {
  swallow_chord_until_release = true;
  swallow_trigger_until_release = true;
  hk_sequence.reset();
  armed = false;
  trigger_released = true;
 }
 if (chord_edge && !hk_sequence.running() && !swallow_chord_until_release) {
  hk_sequence.reset();
  swallow_trigger_until_release = true;
  armed = true;
  trigger_released = false;
 }
 // The arming chord never leaks into the XGO host as SELECT/START/HK.
 // Release the entire chord, then press HK alone to trigger the sequence.
 if (!select && !start && !hk) {
  swallow_chord_until_release = false;
  if (!armed && !hk_sequence.running()) swallow_trigger_until_release = false;
 }
 if (armed && !hk && !select && !start) trigger_released = true;
 uint16_t snapshot = physical;
 if (armed || hk_sequence.running()) {
  const bool trigger = armed && trigger_released && hk && !select && !start;
  const uint16_t synthetic = hk_sequence.update(to_ms_since_boot(get_absolute_time()), trigger);
  if (hk_sequence.running()) {
   armed = false;
   swallow_trigger_until_release = true;
  }
  // During a sequence only the synthetic HK bit reaches the host.
  snapshot = synthetic;
  // Armed but not yet triggered: remain neutral.
  if (!hk_sequence.running() && !armed) trigger_released = false;
 }
 // Consume the trigger HK after completion until it is physically released.
 if (swallow_trigger_until_release && hk && !hk_sequence.running()) snapshot &= ~1u;
 if (chord || abort || swallow_chord_until_release) snapshot = 0;
 xgo_hk_phase_state.store(hk_sequence.running() ? (2u + hk_sequence.phase()) : (armed ? 1u : 0u), std::memory_order_relaxed);
 xgo_hk_repeat_state.store(hk_sequence.running() ? (1u + hk_sequence.repetition()) : 0u, std::memory_order_relaxed);
 if (snapshot != previous_snapshot) {
  xgo_diag_mask_changes.fetch_add(1, std::memory_order_relaxed);
  if (snapshot == 0 && previous_snapshot != 0) xgo_diag_nonzero_to_zero.fetch_add(1, std::memory_order_relaxed);
  previous_snapshot = snapshot;
 }
 if (snapshot == 0) xgo_diag_zero_frames.fetch_add(1, std::memory_order_relaxed);
 else xgo_diag_last_nonzero_mask.store(snapshot, std::memory_order_relaxed);
 xgo_diag_output.store(snapshot, std::memory_order_relaxed);
 published_mask.store(snapshot, std::memory_order_release);
 return true;
}

constexpr uint16_t HK=1,SEL=64,START=128,LEFT=1024;
uint16_t tick(uint32_t t,uint16_t b){now_ms=t;Gamepad g{b};process(&g);return published_mask.load();}
int main(){
assert(tick(0,LEFT)==LEFT);
assert(tick(1,0)==0);
assert(tick(2,SEL|START|HK)==0);
assert(xgo_hk_phase_state.load()==1);
assert(tick(3,SEL|START|HK)==0);
assert(tick(4,0)==0);
assert(tick(5,HK)==0);
assert(xgo_hk_phase_state.load()==2);
assert(tick(2005,0)==HK);
assert(tick(3005,0)==0);
assert(tick(3100,SEL|START)==0);
assert(xgo_hk_phase_state.load()==0);
assert(tick(3101,SEL|START)==0);
assert(tick(3102,0)==0);
assert(tick(3103,LEFT)==LEFT);
assert(tick(3200,SEL|START|HK)==0);
assert(tick(3201,0)==0);
assert(tick(3202,HK)==0);
assert(tick(5202,0)==HK);
assert(tick(50000,HK)==0);
assert(xgo_hk_phase_state.load()==0);
assert(tick(50001,HK)==0);
assert(tick(50002,0)==0);
assert(tick(50003,HK)==HK);
std::cout<<"Test26 behavioral checks passed\\n";}
