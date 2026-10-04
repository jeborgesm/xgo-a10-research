#include <stdint.h>
#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/structs/usb.h"
#include "hardware/regs/usb.h"
#include "hardware/address_mapped.h"

#define LED_PIN 25u
#define EDGE_TIMEOUT_US 20u
#define IDLE_QUALIFY_US 100u

static usb_hw_t *const usb_set = (usb_hw_t *)hw_set_alias_untyped(usb_hw);
static usb_hw_t *const usb_clr = (usb_hw_t *)hw_clear_alias_untyped(usb_hw);

static inline bool dm(void) {
    return (usb_hw->phy_direct & USB_USBPHY_DIRECT_RX_DM_BITS) != 0;
}
static inline void data_sink(void) {
    /* TX_DM stays zero; OE=1 sinks DPM LOW. */
    usb_set->phy_direct = USB_USBPHY_DIRECT_TX_DM_OE_BITS;
}
static inline void data_release(void) {
    usb_clr->phy_direct = USB_USBPHY_DIRECT_TX_DM_OE_BITS;
}
static bool wait_level(bool level, uint32_t timeout_us) {
    uint32_t deadline = time_us_32() + timeout_us;
    while (dm() != level) {
        if ((int32_t)(deadline - time_us_32()) <= 0) return false;
    }
    return true;
}

static void usbphy_xgo_mode(void) {
    usb_hw->main_ctrl = 0;
    usb_hw->sie_ctrl = 0;
    usb_hw->muxing = USB_USB_MUXING_TO_PHY_BITS | USB_USB_MUXING_SOFTCON_BITS;
    usb_hw->phy_direct = 0;
    usb_hw->phy_direct_override =
        USB_USBPHY_DIRECT_OVERRIDE_DP_PULLUP_EN_OVERRIDE_EN_BITS |
        USB_USBPHY_DIRECT_OVERRIDE_DP_PULLDN_EN_OVERRIDE_EN_BITS |
        USB_USBPHY_DIRECT_OVERRIDE_DM_PULLDN_EN_OVERRIDE_EN_BITS |
        USB_USBPHY_DIRECT_OVERRIDE_TX_DP_OE_OVERRIDE_EN_BITS |
        USB_USBPHY_DIRECT_OVERRIDE_TX_DM_OE_OVERRIDE_EN_BITS |
        USB_USBPHY_DIRECT_OVERRIDE_TX_DIFFMODE_OVERRIDE_EN_BITS |
        USB_USBPHY_DIRECT_OVERRIDE_TX_PD_OVERRIDE_EN_BITS |
        USB_USBPHY_DIRECT_OVERRIDE_RX_PD_OVERRIDE_EN_BITS;
    data_release();
}

int main(void) {
    usbphy_xgo_mode();
    stdio_init_all();
    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);
    gpio_put(LED_PIN, 1);
    sleep_ms(250);

    puts("\nXGO-P4 NATIVE USBPHY FIXED-RIGHT v4 PHY-POWER");
    puts("DPP=CLOCK; DPM=DATA; explicit TX/RX powered overrides; slot 11 RIGHT");

    while (true) {
        data_release();

        /* Qualify the long inter-transaction CLOCK-high idle. This avoids using
           DATA/load as our synchronizer, so passive slot-0 behavior cannot
           masquerade as active responder success. */
        while (!dm()) tight_loop_contents();
        uint32_t high_since = time_us_32();
        while (dm()) {
            if ((uint32_t)(time_us_32() - high_since) >= IDLE_QUALIFY_US) break;
        }
        if (!dm()) continue;

        /* First falling edge begins position-1 setup. Count through falling
           edges 1..11. RIGHT is wire slot 11, so assert during low #11. */
        if (!wait_level(false, 20000u)) continue;
        for (unsigned fall = 1; fall < 11; ++fall) {
            if (!wait_level(true, EDGE_TIMEOUT_US)) goto recover;
            if (!wait_level(false, EDGE_TIMEOUT_US)) goto recover;
        }

        data_sink();                 /* low #11: install RIGHT */
        if (!wait_level(true, EDGE_TIMEOUT_US)) goto recover; /* sample slot 11 */
        if (!wait_level(false, EDGE_TIMEOUT_US)) goto recover;/* trailing low #12 */
        data_release();
        if (!wait_level(true, EDGE_TIMEOUT_US)) goto recover;
        continue;

recover:
        /* Hard fail-safe: output always returns Hi-Z before resynchronizing. */
        data_release();
        sleep_us(100);
    }
}
