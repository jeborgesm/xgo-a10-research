#include <stdint.h>
#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/structs/usb.h"
#include "hardware/regs/usb.h"
#include "hardware/address_mapped.h"

#define LED_PIN 25u
#define CLOCK_TIMEOUT_US 20u

static usb_hw_t *const usb_set = (usb_hw_t *)hw_set_alias_untyped(usb_hw);
static usb_hw_t *const usb_clr = (usb_hw_t *)hw_clear_alias_untyped(usb_hw);

static inline bool dp(void) {
    return (usb_hw->phy_direct & USB_USBPHY_DIRECT_RX_DP_BITS) != 0;
}
static inline bool dm(void) {
    return (usb_hw->phy_direct & USB_USBPHY_DIRECT_RX_DM_BITS) != 0;
}
static inline void data_sink(void) {
    /* TX_DP remains zero. Enabling only its OE sinks DPP low. */
    usb_set->phy_direct = USB_USBPHY_DIRECT_TX_DP_OE_BITS;
}
static inline void data_release(void) {
    usb_clr->phy_direct = USB_USBPHY_DIRECT_TX_DP_OE_BITS;
}

static void usbphy_xgo_mode(void) {
    usb_hw->main_ctrl = 0;
    usb_hw->sie_ctrl = 0;
    usb_hw->muxing = USB_USB_MUXING_TO_PHY_BITS | USB_USB_MUXING_SOFTCON_BITS;

    /* Single-ended, LOW data latch, both outputs initially Hi-Z, no local pulls.
       Deliberately do not claim DM-pullup override ownership: P3-v3 proved that
       change freezes the XGO even with a zero requested pull-up value. */
    usb_hw->phy_direct = 0;
    usb_hw->phy_direct_override =
        USB_USBPHY_DIRECT_OVERRIDE_DP_PULLUP_EN_OVERRIDE_EN_BITS |
        USB_USBPHY_DIRECT_OVERRIDE_DP_PULLDN_EN_OVERRIDE_EN_BITS |
        USB_USBPHY_DIRECT_OVERRIDE_DM_PULLDN_EN_OVERRIDE_EN_BITS |
        USB_USBPHY_DIRECT_OVERRIDE_TX_DP_OE_OVERRIDE_EN_BITS |
        USB_USBPHY_DIRECT_OVERRIDE_TX_DM_OE_OVERRIDE_EN_BITS |
        USB_USBPHY_DIRECT_OVERRIDE_TX_DIFFMODE_OVERRIDE_EN_BITS;
    data_release();
}

int main(void) {
    usbphy_xgo_mode();
    stdio_init_all();
    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);
    gpio_put(LED_PIN, 1);
    sleep_ms(250);

    puts("\nXGO-P4 NATIVE USBPHY FIXED-R v1");
    puts("assumption: DPP=DATA, DPM=CLOCK; DPP sinks LOW for slot 0 only");

    while (true) {
        /* Host load/reset: DATA is driven LOW, then released HIGH. */
        while (dp()) tight_loop_contents();
        while (!dp()) tight_loop_contents();

        /* R is slot 0 and is sampled before the first CLOCK fall. */
        data_sink();

        /* Fail-safe: never leave DATA asserted if the expected clock is absent. */
        uint32_t deadline = time_us_32() + CLOCK_TIMEOUT_US;
        while (dm() && (int32_t)(deadline - time_us_32()) > 0)
            tight_loop_contents();

        data_release();

        /* If no falling clock arrived, wait for bus recovery before re-arming.
           Output is already Hi-Z, so this path cannot hold the XGO line down. */
        if (dm()) {
            sleep_us(100);
            continue;
        }

        /* Consume the first clock low/high so the next DATA low is the next
           host load/reset rather than anything in the current transaction. */
        while (!dm()) tight_loop_contents();
    }
}
