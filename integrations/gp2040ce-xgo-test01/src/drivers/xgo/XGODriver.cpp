// Experimental GP2040-CE XGO output: derived from hardware-proven Caveman.
// Preserve USB PHY signaling; no USB device stack in XGO mode.
#include "drivers/xgo/XGODriver.h"
#include "drivers/xgo/XGODiagnostics.h"
#include "hardware/structs/usb.h"
#include "hardware/regs/usb.h"
#include "hardware/address_mapped.h"
#include "pico/time.h"
#include "hardware/sync.h"
#include <cstdint>

std::atomic<uint32_t> xgo_diag_raw{0};
std::atomic<uint32_t> xgo_diag_processed{0};
std::atomic<uint32_t> xgo_diag_output{0};
namespace {
constexpr uint32_t EDGE_TIMEOUT_US = 12;
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
bool emit_frame(uint16_t mask) {
 data_release();
 if (!wait_data(false, LOAD_TIMEOUT_US)) { data_release(); return false; }

 // Test04: the host's LOAD release-to-slot-0 interval is only 12us.
 // Test03 left this critical edge vulnerable to interrupt preemption.
 // Never mask interrupts during the potentially 20ms LOAD acquisition.
 const uint32_t irq_state = save_and_disable_interrupts();
 bool complete = wait_data(true, EDGE_TIMEOUT_US);
 if (complete) {
  if (mask & 1u) data_sink(); else data_release();
 }
 for (unsigned slot = 1; complete && slot < 12; ++slot) {
  if (!wait_clock(false, EDGE_TIMEOUT_US)) { complete = false; break; }
  if (mask & (1u << slot)) data_sink(); else data_release();
  if (!wait_clock(true, EDGE_TIMEOUT_US)) { complete = false; break; }
 }
 if (complete) {
  if (!wait_clock(false, EDGE_TIMEOUT_US)) complete = false;
 }
 data_release();
 if (complete) (void)wait_clock(true, EDGE_TIMEOUT_US);
 restore_interrupts(irq_state);
 return complete;
}

} // namespace

void XGODriver::initialize() { raw_init(); }
bool XGODriver::process(Gamepad *gamepad) {
 const uint16_t snapshot = map_mask(gamepad);
 xgo_diag_output.store(snapshot, std::memory_order_relaxed);
 return emit_frame(snapshot);
}
