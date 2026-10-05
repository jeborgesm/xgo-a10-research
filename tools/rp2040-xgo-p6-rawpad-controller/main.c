#include <stdint.h>
#include <stdbool.h>
#include "pico/stdlib.h"
#include "hardware/structs/usb.h"
#include "hardware/regs/usb.h"
#include "hardware/address_mapped.h"

#define LED 25u
#define OBSERVE_MS 500u
#define FRAME_GAP_US 100u
#define EDGE_TIMEOUT_US 12u
#define LOAD_TIMEOUT_US 20000u

static usb_hw_t *const uset=(usb_hw_t*)hw_set_alias_untyped(usb_hw);
static usb_hw_t *const uclr=(usb_hw_t*)hw_clear_alias_untyped(usb_hw);

typedef enum { SRC_PHY=0, SRC_SIE=1 } source_t;
typedef struct { uint32_t frames,good12,falls; } stats_t;
typedef struct { source_t src; bool clock_dp; bool valid; uint8_t code; } mapping_t;

static inline uint8_t phy_pair(void) {
    uint32_t v=usb_hw->phy_direct;
    return ((v&USB_USBPHY_DIRECT_RX_DP_BITS)?1u:0u)|((v&USB_USBPHY_DIRECT_RX_DM_BITS)?2u:0u);
}
static inline uint8_t sie_pair(void) {
    return (usb_hw->sie_status&USB_SIE_STATUS_LINE_STATE_BITS)>>USB_SIE_STATUS_LINE_STATE_LSB;
}
static inline bool line(source_t s,bool dp) {
    uint8_t p=(s==SRC_PHY)?phy_pair():sie_pair();
    return !!(p&(dp?1u:2u));
}
static void blink(unsigned n) {
    for(unsigned i=0;i<n;i++){gpio_put(LED,1);sleep_ms(100);gpio_put(LED,0);sleep_ms(130);}
    sleep_ms(650);
}
static void raw_pad_init(void) {
    usb_hw->main_ctrl=0;
    usb_hw->sie_ctrl=0;
    usb_hw->muxing=USB_USB_MUXING_TO_PHY_BITS|USB_USB_MUXING_SOFTCON_BITS;
    usb_hw->phy_direct=0; /* TX values LOW, OEs off, powers on, pulls off */
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
    /* Deliberately do NOT assert DM_PULLUP_OVERRIDE_EN: P3-v3 hardware froze XGO
       when that override was introduced. main_ctrl/sie_ctrl are zero and
       phy_direct DM_PULLUP_EN remains zero. */
}
static stats_t observe(source_t src,bool dp) {
    stats_t s={0}; bool prev=line(src,dp); uint32_t start=to_ms_since_boot(get_absolute_time());
    uint32_t lastfall=0,inframe=0;
    while((uint32_t)(to_ms_since_boot(get_absolute_time())-start)<OBSERVE_MS) {
        bool v=line(src,dp);
        if(prev&&!v) {
            uint32_t now=time_us_32(),dt=now-lastfall; s.falls++;
            if(!lastfall||dt>FRAME_GAP_US) { if(inframe==12)s.good12++; s.frames++; inframe=1; }
            else inframe++;
            lastfall=now;
        }
        prev=v;
    }
    if(inframe==12)s.good12++;
    return s;
}
static mapping_t classify(void) {
    stats_t pdp=observe(SRC_PHY,true), pdm=observe(SRC_PHY,false);
    stats_t sdp=observe(SRC_SIE,true), sdm=observe(SRC_SIE,false);
    mapping_t m={0};
    if(pdp.good12>=10 && pdp.good12>pdm.good12){m=(mapping_t){SRC_PHY,true,true,2};}
    else if(pdm.good12>=10 && pdm.good12>pdp.good12){m=(mapping_t){SRC_PHY,false,true,3};}
    else if(sdp.good12>=10 && sdp.good12>sdm.good12){m=(mapping_t){SRC_SIE,true,true,5};}
    else if(sdm.good12>=10 && sdm.good12>sdp.good12){m=(mapping_t){SRC_SIE,false,true,6};}
    else m=(mapping_t){SRC_PHY,true,false,4};
    return m;
}
static inline void data_release(bool data_dp) {
    uclr->phy_direct=data_dp?USB_USBPHY_DIRECT_TX_DP_OE_BITS:USB_USBPHY_DIRECT_TX_DM_OE_BITS;
}
static inline void data_sink(bool data_dp) {
    uset->phy_direct=data_dp?USB_USBPHY_DIRECT_TX_DP_OE_BITS:USB_USBPHY_DIRECT_TX_DM_OE_BITS;
}
static bool wait_line(source_t src,bool dp,bool value,uint32_t timeout) {
    uint32_t t=time_us_32();
    while(line(src,dp)!=value) if((uint32_t)(time_us_32()-t)>timeout)return false;
    return true;
}
static bool emit_frame(mapping_t m,uint16_t mask) {
    bool clock_dp=m.clock_dp, data_dp=!clock_dp;
    data_release(data_dp);
    /* Reproduce hardware-proven P2 synchronization: DATA load LOW -> release HIGH. */
    if(!wait_line(m.src,data_dp,false,LOAD_TIMEOUT_US))return false;
    if(!wait_line(m.src,data_dp,true,EDGE_TIMEOUT_US)){data_release(data_dp);return false;}
    /* Position 0 is sampled immediately after DATA release, before first CLOCK fall. */
    if(mask&1u)data_sink(data_dp); else data_release(data_dp);
    for(unsigned slot=1;slot<12;slot++) {
        if(!wait_line(m.src,clock_dp,false,EDGE_TIMEOUT_US)){data_release(data_dp);return false;}
        if(mask&(1u<<slot))data_sink(data_dp); else data_release(data_dp);
        if(!wait_line(m.src,clock_dp,true,EDGE_TIMEOUT_US)){data_release(data_dp);return false;}
    }
    /* Consume final/trailing low pulse exactly as proven PIO responder does. */
    if(!wait_line(m.src,clock_dp,false,EDGE_TIMEOUT_US)){data_release(data_dp);return false;}
    data_release(data_dp);
    (void)wait_line(m.src,clock_dp,true,EDGE_TIMEOUT_US);
    return true;
}
typedef struct {uint16_t mask;uint16_t polls;} phase_t;
static const phase_t script[]={
    {1u<<11,50},{(1u<<11)|(1u<<0)|(1u<<5),12},{1u<<11,18},{0,8},
    {1u<<10,50},{1u<<9,24},{(1u<<0)|(1u<<5),12},{0,24}
};
int main(void) {
    gpio_init(LED);gpio_set_dir(LED,GPIO_OUT);gpio_put(LED,0);
    raw_pad_init();sleep_ms(400);
    blink(1);
    mapping_t m=classify();
    blink(m.code);
    if(!m.valid)while(1)blink(4);
    size_t phase=0;uint16_t remaining=script[0].polls;bool led=0;
    while(1) {
        if(emit_frame(m,script[phase].mask)) {
            gpio_put(LED,led=!led);
            if(--remaining==0){phase=(phase+1)%(sizeof(script)/sizeof(script[0]));remaining=script[phase].polls;}
        } else {
            data_release(!m.clock_dp);
            gpio_put(LED,0);
        }
    }
}
