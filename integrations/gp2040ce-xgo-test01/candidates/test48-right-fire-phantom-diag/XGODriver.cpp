// Experimental GP2040-CE XGO output: derived from hardware-proven Caveman.
// Preserve USB PHY signaling; no USB device stack in XGO mode.
#include "drivers/xgo/XGODriver.h"
#include "drivers/xgo/XGODiagnostics.h"
#include "hardware/structs/usb.h"
#include "hardware/regs/usb.h"
#include "hardware/address_mapped.h"
#include "pico/time.h"
#include "hardware/sync.h"

#include "pico/stdlib.h"
#include <cstdint>

std::atomic<uint32_t> xgo_diag_raw{0};
std::atomic<uint32_t> xgo_diag_processed{0};
std::atomic<uint32_t> xgo_diag_output{0};
std::atomic<uint32_t> xgo_diag_frames_ok{0};
std::atomic<uint32_t> xgo_diag_frames_failed{0};
std::atomic<uint32_t> xgo_diag_load_timeouts{0};
std::atomic<uint32_t> xgo_diag_release_timeouts{0};
std::atomic<uint32_t> xgo_diag_clock_timeouts{0};
std::atomic<uint32_t> xgo_diag_clock_low_failures{0};
std::atomic<uint32_t> xgo_diag_clock_high_failures{0};
std::atomic<uint32_t> xgo_diag_right_attack_attempts{0};
std::atomic<uint32_t> xgo_diag_right_attack_failures{0};
std::atomic<uint32_t> xgo_diag_last_failure_slot{0};
std::atomic<uint32_t> xgo_diag_load_low_last_us{0};
std::atomic<uint32_t> xgo_diag_load_low_max_us{0};
std::atomic<uint32_t> xgo_diag_clock_failure_slots[13]{};
std::atomic<uint32_t> xgo_diag_mask_changes{0};
std::atomic<uint32_t> xgo_diag_zero_frames{0};
std::atomic<uint32_t> xgo_diag_last_nonzero_mask{0};
std::atomic<uint32_t> xgo_diag_nonzero_to_zero{0};
std::atomic<uint32_t> xgo_diag_active_attempts{0};
std::atomic<uint32_t> xgo_diag_active_failures{0};
std::atomic<uint32_t> xgo_diag_fail_after_success{0};
std::atomic<uint32_t> xgo_diag_consecutive_active_failures{0};
std::atomic<uint32_t> xgo_diag_max_active_failure_streak{0};
namespace { std::atomic<uint16_t> published_mask{0}; }
// Core0 observes physical transitions; Core1 acknowledges consumption once per host scan.
namespace { std::atomic<uint16_t> pending_press_edges{0}; }
// Core1 owns the output pulse window, measured in host scan time.
namespace { uint16_t attack_pulse_mask = 0; uint32_t attack_pulse_start_us = 0; }
constexpr uint32_t ATTACK_PULSE_US = 18000;
namespace { uint16_t previous_physical_attacks = 0; }
constexpr uint16_t ATTACK_BITS = 0x003fu;
namespace { bool previous_active_success = false; uint32_t active_failure_streak = 0; }
namespace { uint16_t previous_snapshot = 0; }

namespace {
// Test42: allow a slightly longer CLOCK transition wait; preserve slot order and 18ms pulse.
constexpr uint32_t EDGE_TIMEOUT_US = 18;
constexpr uint32_t LOAD_TIMEOUT_US = 20000;
usb_hw_t *const set_alias = (usb_hw_t *)hw_set_alias_untyped(usb_hw);
usb_hw_t *const clear_alias = (usb_hw_t *)hw_clear_alias_untyped(usb_hw);
inline bool clock_level() { return (usb_hw->phy_direct & USB_USBPHY_DIRECT_RX_DM_BITS) != 0; }
inline bool data_level() { return (usb_hw->phy_direct & USB_USBPHY_DIRECT_RX_DP_BITS) != 0; }
inline void data_release() { clear_alias->phy_direct = USB_USBPHY_DIRECT_TX_DP_OE_BITS; }
inline void data_sink() { set_alias->phy_direct = USB_USBPHY_DIRECT_TX_DP_OE_BITS; }
bool wait_clock(bool level, uint32_t timeout) {
 uint32_t t = time_us_32();
 while (clock_level() != level)
  if ((uint32_t)(time_us_32() - t) > timeout) return false;
 return true;
}
bool wait_data(bool level, uint32_t timeout) {
 uint32_t t = time_us_32();
 while (data_level() != level)
  if ((uint32_t)(time_us_32() - t) > timeout) return false;
 return true;
}
void raw_init() {
 usb_hw->main_ctrl = 0;
 usb_hw->sie_ctrl = 0;
 usb_hw->muxing = USB_USB_MUXING_TO_PHY_BITS | USB_USB_MUXING_SOFTCON_BITS;
 usb_hw->phy_direct = 0;
 usb_hw->phy_direct_override =
  USB_USBPHY_DIRECT_OVERRIDE_TX_DIFFMODE_OVERRIDE_EN_BITS |
  USB_USBPHY_DIRECT_OVERRIDE_TX_PD_OVERRIDE_EN_BITS |
  USB_USBPHY_DIRECT_OVERRIDE_RX_PD_OVERRIDE_EN_BITS |
  USB_USBPHY_DIRECT_OVERRIDE_TX_DM_OVERRIDE_EN_BITS |
  USB_USBPHY_DIRECT_OVERRIDE_TX_DP_OVERRIDE_EN_BITS |
  USB_USBPHY_DIRECT_OVERRIDE_TX_DM_OE_OVERRIDE_EN_BITS |
  USB_USBPHY_DIRECT_OVERRIDE_TX_DP_OE_OVERRIDE_EN_BITS |
  USB_USBPHY_DIRECT_OVERRIDE_DP_PULLUP_EN_OVERRIDE_EN_BITS |
  USB_USBPHY_DIRECT_OVERRIDE_DP_PULLDN_EN_OVERRIDE_EN_BITS |
  USB_USBPHY_DIRECT_OVERRIDE_DM_PULLDN_EN_OVERRIDE_EN_BITS;
 data_release();
}
uint16_t map_mask(Gamepad *g) {
 return (g->pressedR1() ? 1u << 0 : 0u)
  | (g->pressedB4() ? 1u << 1 : 0u)
  | (g->pressedB3() ? 1u << 2 : 0u)
  | (g->pressedL1() ? 1u << 3 : 0u)
  | (g->pressedB1() ? 1u << 4 : 0u)
  | (g->pressedB2() ? 1u << 5 : 0u)
  | (g->pressedS1() ? 1u << 6 : 0u)
  | (g->pressedS2() ? 1u << 7 : 0u)
  | (g->pressedUp() ? 1u << 8 : 0u)
  | (g->pressedDown() ? 1u << 9 : 0u)
  | (g->pressedLeft() ? 1u << 10 : 0u)
  | (g->pressedRight() ? 1u << 11 : 0u);
}
// Test03: keep the long host-load wait interruptible; protect only the
// microsecond-scale 12-slot clock train against Core0 IRQ preemption.
// Core1 (OLED/add-ons) remains untouched.
bool emit_frame() {
 data_release();
 // Test12 recovery: after a failed active transaction, do not interpret
 // the same host LOAD-low interval as another new frame. Require DATA
 // high before rearming. This only affects the failure path.
 static bool require_idle_high = false;
 if (require_idle_high) {
  if (!wait_data(true, LOAD_TIMEOUT_US)) {
   xgo_diag_load_timeouts.fetch_add(1, std::memory_order_relaxed);
   return false;
  }
  require_idle_high = false;
 }

 if (!wait_data(false, LOAD_TIMEOUT_US)) { xgo_diag_load_timeouts.fetch_add(1, std::memory_order_relaxed); data_release(); return false; }

 // Test04: the host's LOAD release-to-slot-0 interval is only 12us.
 // Test03 left this critical edge vulnerable to interrupt preemption.
 // Never mask interrupts during the potentially 20ms LOAD acquisition.
 const uint32_t irq_state = save_and_disable_interrupts();
 const uint16_t physical = published_mask.load(std::memory_order_acquire);
 // Retain an attack across host polls for >= one 12ms game-poll period.
 // This is a bounded output pulse, NOT a repeated pulse while held.
 const uint32_t now = time_us_32();
 if (attack_pulse_mask && (uint32_t)(now - attack_pulse_start_us) >= ATTACK_PULSE_US)
  attack_pulse_mask = 0;
 const uint16_t pending = pending_press_edges.exchange(0, std::memory_order_acq_rel);
 // Queue any new edge after the current window; do not erase other edges.
 // Physical release is tracked on Core0, not inferred from the output pulse.
 if (pending && !attack_pulse_mask) {
  attack_pulse_mask = pending;
  attack_pulse_start_us = now;
 } else if (pending) {
  pending_press_edges.fetch_or(pending, std::memory_order_release);
 }
 const uint16_t mask = (physical & ~ATTACK_BITS) | attack_pulse_mask;
 const uint32_t low_start = time_us_32();
 // Test27 experimental: slot 0 has no preceding CLOCK edge. When R/HK
 // is pressed, waiting for DATA to rise before asserting it is inherently
 // late relative to the host's first sample. The host itself drives DATA
 // low during LOAD, so an early open-drain sink is electrically compatible.
 // This path intentionally does NOT wait for a DATA-high transition that
 // our own asserted output would mask. The first CLOCK-low edge terminates
 // slot 0 and synchronizes the remaining eleven slots.
 const bool hk_slot0 = (mask & 1u) != 0;
 bool complete;
 if (hk_slot0) {
  // Empirical protocol hypothesis: host LOAD low lasts ~4 us.
  // Keep an explicit pre-drive interval; no electrical contention because
  // the controller only sinks the line (never drives it high).
  while ((uint32_t)(time_us_32() - low_start) < 3u) {}
  data_sink();
  complete = true;
 } else {
  complete = wait_data(true, EDGE_TIMEOUT_US);
  if (complete) data_release();
 }
 const uint32_t low_duration = (uint32_t)(time_us_32() - low_start);
 const bool release_timeout = !complete;
 unsigned failed_slot = 0;
 bool clock_timeout = false;
 bool clock_low_failure = false;
 bool clock_high_failure = false;
 for (unsigned slot = 1; complete && slot < 12; ++slot) {
  if (!wait_clock(false, EDGE_TIMEOUT_US)) { clock_timeout = true; clock_low_failure = true; failed_slot = slot; complete = false; break; }
  if (mask & (1u << slot)) data_sink(); else data_release();
  if (!wait_clock(true, EDGE_TIMEOUT_US)) { clock_timeout = true; clock_high_failure = true; failed_slot = slot; complete = false; break; }
 }
 if (complete) {
  if (!wait_clock(false, EDGE_TIMEOUT_US)) { clock_timeout = true; clock_low_failure = true; failed_slot = 12; complete = false; }
 }
 data_release();
 if (complete && !wait_clock(true, EDGE_TIMEOUT_US)) { complete = false; clock_high_failure = true; clock_timeout = true; failed_slot = 12; }
 restore_interrupts(irq_state);
 const bool right_and_attack = (mask & (1u << 11)) && (mask & ATTACK_BITS);
 if (right_and_attack) {
  xgo_diag_right_attack_attempts.fetch_add(1, std::memory_order_relaxed);
  if (!complete) xgo_diag_right_attack_failures.fetch_add(1, std::memory_order_relaxed);
 }
 // A failed serial transaction cannot acknowledge the physical press.
 // Retry the event on the next host transaction instead of losing it.
 // An unsuccessful transaction does not end the time-bounded pulse.
 // It remains active for subsequent host polls within its window.
 xgo_diag_active_attempts.fetch_add(1, std::memory_order_relaxed);
 if (release_timeout) xgo_diag_release_timeouts.fetch_add(1, std::memory_order_relaxed);
 if (clock_low_failure) xgo_diag_clock_low_failures.fetch_add(1, std::memory_order_relaxed);
 if (clock_high_failure) xgo_diag_clock_high_failures.fetch_add(1, std::memory_order_relaxed);
 if (clock_timeout) {
  xgo_diag_clock_timeouts.fetch_add(1, std::memory_order_relaxed);
  xgo_diag_last_failure_slot.store(failed_slot, std::memory_order_relaxed);
  xgo_diag_clock_failure_slots[failed_slot].fetch_add(1, std::memory_order_relaxed);
 }
 xgo_diag_load_low_last_us.store(low_duration, std::memory_order_relaxed);
 uint32_t maximum = xgo_diag_load_low_max_us.load(std::memory_order_relaxed);
 if (low_duration > maximum) xgo_diag_load_low_max_us.store(low_duration, std::memory_order_relaxed);
 if (!complete) require_idle_high = true;
 if (complete) {
  previous_active_success = true;
  active_failure_streak = 0;
  xgo_diag_consecutive_active_failures.store(0, std::memory_order_relaxed);
 } else {
  xgo_diag_active_failures.fetch_add(1, std::memory_order_relaxed);
  if (previous_active_success) xgo_diag_fail_after_success.fetch_add(1, std::memory_order_relaxed);
  previous_active_success = false;
  ++active_failure_streak;
  xgo_diag_consecutive_active_failures.store(active_failure_streak, std::memory_order_relaxed);
  const uint32_t peak = xgo_diag_max_active_failure_streak.load(std::memory_order_relaxed);
  if (active_failure_streak > peak) xgo_diag_max_active_failure_streak.store(active_failure_streak, std::memory_order_relaxed);
 }
 return complete;
}

} // namespace

void XGODriver::initialize() { /* USB PHY belongs exclusively to Core1 responder. */ }
void XGODriver::runResponder() {
 raw_init();
 while (true) {
  const bool complete = emit_frame();
  if (complete) xgo_diag_frames_ok.fetch_add(1, std::memory_order_relaxed);
  else xgo_diag_frames_failed.fetch_add(1, std::memory_order_relaxed);
 }
}
// Test26: Core0-only diagnostic controls. No change to Core1 serial responder.
bool XGODriver::process(Gamepad *gamepad) {
 const uint16_t snapshot = map_mask(gamepad);
 const uint16_t attacks = snapshot & ATTACK_BITS;
 const uint16_t rising = attacks & ~previous_physical_attacks;
 previous_physical_attacks = attacks;
 if (rising) pending_press_edges.fetch_or(rising, std::memory_order_release);
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
