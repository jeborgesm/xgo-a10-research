#include <stdint.h>
#include <stdbool.h>
#include "pico/stdlib.h"
#include "hardware/structs/usb.h"
#include "hardware/regs/usb.h"
#include "hardware/address_mapped.h"

#define LED 25u
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
    data_release();

    /* XGO host's load/reset pulse is on DATA. Wait for host LOW then release.
       Position 0 is sampled immediately after the host releases DATA. */
    if(!wait_data(false,LOAD_TIMEOUT_US)) return false;
    if(!wait_data(true,EDGE_TIMEOUT_US)) { data_release(); return false; }

    if(mask&1u) data_sink(); else data_release();

    for(unsigned slot=1;slot<12;slot++) {
        if(!wait_clock(false,EDGE_TIMEOUT_US)) { data_release(); return false; }
        if(mask&(1u<<slot)) data_sink(); else data_release();
        if(!wait_clock(true,EDGE_TIMEOUT_US)) { data_release(); return false; }
    }

    /* Consume the proven trailing clock pulse, then leave DATA high-Z. */
    if(!wait_clock(false,EDGE_TIMEOUT_US)) { data_release(); return false; }
    data_release();
    (void)wait_clock(true,EDGE_TIMEOUT_US);
    return true;
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
    while(true) {
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
}
