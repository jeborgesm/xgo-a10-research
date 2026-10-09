#include <stdint.h>
#include <stdbool.h>
#include "pico/stdlib.h"
#include "hardware/structs/usb.h"
#include "hardware/regs/usb.h"
#include "hardware/address_mapped.h"

#define LED 25u
#define SAMPLE_COUNT 256u

/* Capture-only derivative: inspect g_samples and g_captured with a debugger.
   Never print or write flash during a frame. */
typedef struct {
    uint32_t load_low_us;
    uint32_t release_to_first_dm_fall_us;
    uint32_t frame_us;
    uint32_t start_to_start_us;
    uint8_t success;
} xgo_sample_t;
volatile xgo_sample_t g_samples[SAMPLE_COUNT];
volatile uint32_t g_captured = 0;
volatile uint32_t g_failed = 0;
volatile bool g_capture_done = false;
static uint32_t previous_start = 0;
static bool have_previous_start = false;
#define EDGE_TIMEOUT_US 12u
#define LOAD_TIMEOUT_US 20000u

static usb_hw_t *const uset=(usb_hw_t*)hw_set_alias_untyped(usb_hw);
static usb_hw_t *const uclr=(usb_hw_t*)hw_clear_alias_untyped(usb_hw);

static inline bool clock_level(void) {
    return !!(usb_hw->phy_direct & USB_USBPHY_DIRECT_RX_DM_BITS);
}
static inline bool data_level(void) {
    return !!(usb_hw->phy_direct & USB_USBPHY_DIRECT_RX_DP_BITS);
}
static inline void data_release(void) {
    uclr->phy_direct=USB_USBPHY_DIRECT_TX_DP_OE_BITS;
}
static inline void data_sink(void) {
    uset->phy_direct=USB_USBPHY_DIRECT_TX_DP_OE_BITS;
}
static void raw_init(void) {
    usb_hw->main_ctrl=0;
    usb_hw->sie_ctrl=0;
    usb_hw->muxing=USB_USB_MUXING_TO_PHY_BITS|USB_USB_MUXING_SOFTCON_BITS;
    usb_hw->phy_direct=0;
    usb_hw->phy_direct_override=
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
static bool wait_clock(bool value,uint32_t timeout) {
    uint32_t t=time_us_32();
    while(clock_level()!=value)
        if((uint32_t)(time_us_32()-t)>timeout)return false;
    return true;
}
static bool wait_data(bool value,uint32_t timeout) {
    uint32_t t=time_us_32();
    while(data_level()!=value)
        if((uint32_t)(time_us_32()-t)>timeout)return false;
    return true;
}

/* Exact 12-slot order proven by the loose-wire P2 Contra responder:
   0 R,1 Y,2 X,3 L,4 A,5 B,6 SELECT,7 START,8 UP,9 DOWN,10 LEFT,11 RIGHT. */
typedef struct {uint16_t mask;uint16_t polls;} phase_t;
static const phase_t script[]={
    {1u<<11,50},
    {(1u<<11)|(1u<<0)|(1u<<5),12},
    {1u<<11,18},
    {0,8},
    {1u<<10,50},
    {1u<<9,24},
    {(1u<<0)|(1u<<5),12},
    {0,24}
};

static bool emit_frame(uint16_t mask) {
    uint32_t started, released, first_fall = 0, ended;
    uint32_t low_started;
    bool ok = false;
    data_release();
    if(!wait_data(false,LOAD_TIMEOUT_US)) return false;
    low_started = time_us_32();
    if(!wait_data(true,EDGE_TIMEOUT_US)) { data_release(); return false; }
    released = time_us_32();
    started = low_started;

    if(mask&1u) data_sink(); else data_release();
    for(unsigned slot=1;slot<12;slot++) {
        if(!wait_clock(false,EDGE_TIMEOUT_US)) goto record;
        if(slot == 1) first_fall = time_us_32();
        if(mask&(1u<<slot)) data_sink(); else data_release();
        if(!wait_clock(true,EDGE_TIMEOUT_US)) goto record;
    }
    if(!wait_clock(false,EDGE_TIMEOUT_US)) goto record;
    data_release();
    (void)wait_clock(true,EDGE_TIMEOUT_US);
    ok = true;
record:
    data_release();
    ended = time_us_32();
    /* Store only after the critical edge sequence, never during it. */
    if(g_captured < SAMPLE_COUNT) {
        volatile xgo_sample_t *p = &g_samples[g_captured];
        p->load_low_us = released - low_started;
        p->release_to_first_dm_fall_us = first_fall ? first_fall - released : 0;
        p->frame_us = ended - started;
        p->start_to_start_us = have_previous_start ? started - previous_start : 0;
        p->success = ok ? 1 : 0;
        previous_start = started;
        have_previous_start = true;
        ++g_captured;
    }
    if(!ok) ++g_failed;
    return ok;
}

int main(void) {
    gpio_init(LED); gpio_set_dir(LED,GPIO_OUT); gpio_put(LED,0);
    raw_init();
    sleep_ms(400);

    /* Two quick blinks identify this native-responder build. */
    for(unsigned i=0;i<2;i++){gpio_put(LED,1);sleep_ms(100);gpio_put(LED,0);sleep_ms(120);}

    size_t phase=0;
    uint16_t remaining=script[0].polls;
    bool led=false;
    while(g_captured < SAMPLE_COUNT) {
        if(emit_frame(script[phase].mask)) {
            gpio_put(LED,led=!led);
            if(--remaining==0) {
                phase=(phase+1)%(sizeof(script)/sizeof(script[0]));
                remaining=script[phase].polls;
            }
        } else {
            data_release();
            gpio_put(LED,0);
        }
    }
    g_capture_done = true;
    data_release();
    gpio_put(LED,0);
    while(true) { tight_loop_contents(); }
}
