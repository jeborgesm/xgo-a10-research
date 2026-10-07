#include <stdint.h>
#include <stdbool.h>
#include "pico/stdlib.h"
#include "hardware/structs/usb.h"
#include "hardware/regs/usb.h"
#include "hardware/address_mapped.h"

#define LED 25u
#define EDGE_TIMEOUT_US 12u
#define LOAD_TIMEOUT_US 20000u

/* Neanderthal-controller GPIO map.
   Wire each momentary button between its GPIO and GND.
   Internal pull-ups make released=HIGH and pressed=LOW. */
#define BTN_R       2u
#define BTN_Y       3u
#define BTN_X       4u
#define BTN_L       5u
#define BTN_A       6u
#define BTN_B       7u
#define BTN_SELECT  8u
#define BTN_START   9u
#define BTN_UP      10u
#define BTN_DOWN    11u
#define BTN_LEFT    12u
#define BTN_RIGHT   13u

typedef struct {
    uint8_t gpio;
    uint16_t slot_bit;
} button_t;

/* Exact XGO wire order:
   0 R,1 Y,2 X,3 L,4 A,5 B,6 SELECT,7 START,8 UP,9 DOWN,10 LEFT,11 RIGHT. */
static const button_t buttons[] = {
    {BTN_R,      1u << 0},
    {BTN_Y,      1u << 1},
    {BTN_X,      1u << 2},
    {BTN_L,      1u << 3},
    {BTN_A,      1u << 4},
    {BTN_B,      1u << 5},
    {BTN_SELECT, 1u << 6},
    {BTN_START,  1u << 7},
    {BTN_UP,     1u << 8},
    {BTN_DOWN,   1u << 9},
    {BTN_LEFT,   1u << 10},
    {BTN_RIGHT,  1u << 11},
};

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
static void buttons_init(void) {
    for (unsigned i=0;i<sizeof(buttons)/sizeof(buttons[0]);i++) {
        gpio_init(buttons[i].gpio);
        gpio_set_dir(buttons[i].gpio, GPIO_IN);
        gpio_pull_up(buttons[i].gpio);
    }
}
static inline uint16_t read_buttons(void) {
    uint16_t mask=0;
    for (unsigned i=0;i<sizeof(buttons)/sizeof(buttons[0]);i++)
        if (!gpio_get(buttons[i].gpio))
            mask |= buttons[i].slot_bit;
    return mask;
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
static bool emit_frame(uint16_t mask) {
    data_release();

    /* Proven native transport is intentionally unchanged:
       DP = DATA/load-like, DM = CLOCK-like, LOW sink/high-Z only. */
    if(!wait_data(false,LOAD_TIMEOUT_US)) return false;
    if(!wait_data(true,EDGE_TIMEOUT_US)) { data_release(); return false; }

    if(mask&1u) data_sink(); else data_release();

    for(unsigned slot=1;slot<12;slot++) {
        if(!wait_clock(false,EDGE_TIMEOUT_US)) { data_release(); return false; }
        if(mask&(1u<<slot)) data_sink(); else data_release();
        if(!wait_clock(true,EDGE_TIMEOUT_US)) { data_release(); return false; }
    }

    if(!wait_clock(false,EDGE_TIMEOUT_US)) { data_release(); return false; }
    data_release();
    (void)wait_clock(true,EDGE_TIMEOUT_US);
    return true;
}

int main(void) {
    gpio_init(LED); gpio_set_dir(LED,GPIO_OUT); gpio_put(LED,0);
    buttons_init();
    raw_init();
    sleep_ms(400);

    /* Three quick blinks identify the live-input build. */
    for(unsigned i=0;i<3;i++){gpio_put(LED,1);sleep_ms(100);gpio_put(LED,0);sleep_ms(120);}

    bool led=false;
    while(true) {
        /* Snapshot once per XGO transaction. Human input cannot change the
           serialized state halfway through a frame. */
        const uint16_t mask=read_buttons();
        if(emit_frame(mask)) {
            gpio_put(LED,led=!led);
        } else {
            data_release();
            gpio_put(LED,0);
        }
    }
}
