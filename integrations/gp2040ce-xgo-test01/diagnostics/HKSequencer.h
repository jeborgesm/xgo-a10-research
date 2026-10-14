#pragma once
// Offline HK diagnostic stimulus scheduler. Does not touch the protected Test16 driver.
// Pure state machine: caller supplies monotonic milliseconds and a rising-edge trigger.
// Outputs are synthetic 12-slot masks. Bit 0 is the XGO R/HK serial slot.
// Production integration MUST keep this outside the time-critical Core1 PHY loop.
#include <cstdint>
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
