#include <stdint.h>
#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/structs/usb.h"
#include "hardware/regs/usb.h"

#define SAMPLE_HZ 1000000u
#define CAPTURE_SAMPLES 65536u
#define LED_PIN 25u

static uint8_t capture[CAPTURE_SAMPLES];

static unsigned score_clock_bursts(unsigned bit) {
    const uint8_t mask = (uint8_t)(1u << bit);
    unsigned score = 0;
    uint32_t last_burst = 0;
    bool have_last = false;

    for (uint32_t i = 1; i + 80 < CAPTURE_SAMPLES; ++i) {
        if (!((capture[i - 1] & mask) && !(capture[i] & mask))) continue;

        unsigned falls = 1;
        uint32_t last_fall = i;
        uint32_t j = i + 1;
        for (; j < i + 80 && j < CAPTURE_SAMPLES; ++j) {
            if ((capture[j - 1] & mask) && !(capture[j] & mask)) {
                uint32_t dt = j - last_fall;
                if (dt >= 2 && dt <= 7) {
                    ++falls;
                    last_fall = j;
                } else if (dt > 7) {
                    break;
                }
            }
        }

        if (falls >= 10 && falls <= 14) {
            score += 10;
            if (have_last) {
                uint32_t cadence = i - last_burst;
                if (cadence >= 14000 && cadence <= 18000) score += 20;
            }
            last_burst = i;
            have_last = true;
            i = j;
        }
    }
    return score;
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

    puts("\\nXGO-P3 USBPHY PASSIVE v4");
    puts("native USB DP/DM receive-only; SIE line-state telemetry, non-freezing P3-v2 PHY baseline");
    printf("rate=%uHz samples=%u duration_us=%u\\n",
           SAMPLE_HZ, CAPTURE_SAMPLES,
           (unsigned)((uint64_t)CAPTURE_SAMPLES * 1000000ull / SAMPLE_HZ));

    absolute_time_t next = get_absolute_time();
    for (uint32_t i = 0; i < CAPTURE_SAMPLES; ++i) {
        capture[i] = sample_dp_dm();
        next = delayed_by_us(next, 1);
        busy_wait_until(next);
    }

    unsigned dp_score = score_clock_bursts(0);
    unsigned dm_score = score_clock_bursts(1);
    uint32_t sie = usb_hw->sie_status;\n    unsigned line_state = (sie & USB_SIE_STATUS_LINE_STATE_BITS) >> USB_SIE_STATUS_LINE_STATE_LSB;\n    printf("clock scores: DP=%u DM=%u line_state=%u sie=0x%08lx\\n",\n           dp_score, dm_score, line_state, (unsigned long)sie);

    puts("BEGIN XGO_P3");
    for (uint32_t i = 0; i < CAPTURE_SAMPLES; i += 32) {
        for (uint32_t j = 0; j < 32; ++j)
            putchar("0123"[capture[i + j] & 3u]);
        putchar('\\n');
    }
    puts("END XGO_P3");

    /* 1=DP clock signature, 2=DM clock signature, 3=ambiguous. */
    if (dp_score >= 30u && dp_score > dm_score + 10u) blink_code(1);
    if (dm_score >= 30u && dm_score > dp_score + 10u) blink_code(2);
    blink_code(3);
}
