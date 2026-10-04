#include <stdint.h>
#include "pico/stdlib.h"
#include "hardware/structs/usb.h"
#include "hardware/regs/usb.h"

#define SAMPLE_HZ 1000000u
#define CAPTURE_SAMPLES 65536u
#define LED_PIN 25u

static uint8_t capture[CAPTURE_SAMPLES];

static unsigned count_falling_edges(unsigned bit) {
    unsigned n = 0;
    uint8_t mask = (uint8_t)(1u << bit);
    for (uint32_t i = 1; i < CAPTURE_SAMPLES; ++i)
        if ((capture[i - 1] & mask) && !(capture[i] & mask)) ++n;
    return n;
}

static void blink_code(unsigned n) {
    gpio_init(LED_PIN); gpio_set_dir(LED_PIN, GPIO_OUT);
    while (true) {
        for (unsigned i = 0; i < n; ++i) {
            gpio_put(LED_PIN, 1); sleep_ms(180);
            gpio_put(LED_PIN, 0); sleep_ms(220);
        }
        sleep_ms(1200);
    }
}

static void usbphy_force_passive(void) {
    /* Route the native pins to the USB PHY, but keep the USB controller disabled. */
    usb_hw->main_ctrl = 0;
    usb_hw->muxing = USB_USB_MUXING_TO_PHY_BITS | USB_USB_MUXING_SOFTCON_BITS;

    /*
     * Override every local bias/output function used by this experiment.
     * All values are zero: no pull-up, no pull-down, no DP/DM output enable.
     * RX_DP/RX_DM remain readable physical pin-state bits.
     */
    usb_hw->phy_direct = 0;
    usb_hw->phy_direct_override =
        USB_USBPHY_DIRECT_OVERRIDE_DP_PULLUP_EN_OVERRIDE_EN_BITS |
        USB_USBPHY_DIRECT_OVERRIDE_DP_PULLDN_EN_OVERRIDE_EN_BITS |
        USB_USBPHY_DIRECT_OVERRIDE_DM_PULLDN_EN_OVERRIDE_EN_BITS |
        USB_USBPHY_DIRECT_OVERRIDE_TX_DP_OE_OVERRIDE_EN_BITS |
        USB_USBPHY_DIRECT_OVERRIDE_TX_DM_OE_OVERRIDE_EN_BITS |
        USB_USBPHY_DIRECT_OVERRIDE_TX_DIFFMODE_OVERRIDE_EN_BITS;
}

static inline uint8_t sample_dp_dm(void) {
    uint32_t v = usb_hw->phy_direct;
    return (uint8_t)(((v & USB_USBPHY_DIRECT_RX_DP_BITS) ? 1u : 0u) |
                     ((v & USB_USBPHY_DIRECT_RX_DM_BITS) ? 2u : 0u));
}

int main(void) {
    usbphy_force_passive();

    /* UART only. Never initialize USB stdio/TinyUSB in this build. */
    stdio_init_all();
    sleep_ms(250);

    puts("\nXGO-P3 USBPHY PASSIVE v1");
    puts("native USB DP/DM receive-only; local pulls and TX output enables forced off");
    printf("rate=%uHz samples=%u duration_us=%u\n",
           SAMPLE_HZ, CAPTURE_SAMPLES,
           (unsigned)((uint64_t)CAPTURE_SAMPLES * 1000000ull / SAMPLE_HZ));

    absolute_time_t next = get_absolute_time();
    for (uint32_t i = 0; i < CAPTURE_SAMPLES; ++i) {
        capture[i] = sample_dp_dm();
        next = delayed_by_us(next, 1);
        busy_wait_until(next);
    }

    /* Classification happens only after the passive capture is complete. */
    unsigned dp_edges = count_falling_edges(0);
    unsigned dm_edges = count_falling_edges(1);
    printf("edges: DP=%u DM=%u\\n", dp_edges, dm_edges);

    puts("BEGIN XGO_P3");
    for (uint32_t i = 0; i < CAPTURE_SAMPLES; i += 32) {
        for (uint32_t j = 0; j < 32; ++j)
            putchar("0123"[capture[i + j] & 3u]);
        putchar('\n');
    }
    puts("END XGO_P3");

    /* Self-contained indication when no UART adapter is available:
       1 blink = DP has substantially more falling edges (clock candidate)
       2 blinks = DM has substantially more falling edges (clock candidate)
       3 blinks = ambiguous/no dominant line. */
    if (dp_edges > dm_edges + 20u) blink_code(1);
    if (dm_edges > dp_edges + 20u) blink_code(2);
    blink_code(3);
}
