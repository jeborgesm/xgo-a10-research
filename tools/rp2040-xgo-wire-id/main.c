#include <stdint.h>
#include <stdbool.h>
#include "pico/stdlib.h"
#include "hardware/structs/usb.h"
#include "hardware/regs/usb.h"
#include "hardware/address_mapped.h"

#define LED 25u
#define OBS_US 250000u
#define FRAME_GAP_US 100u
#define MIN_EDGE_US 1u
#define MAX_EDGE_US 8u

static usb_hw_t *const uclr=(usb_hw_t*)hw_clear_alias_untyped(usb_hw);

typedef struct {
 uint32_t rises, falls, short_intervals, long_gaps;
 uint32_t min_dt, max_dt;
 bool initial, final;
} obs_t;

static inline bool dp(void){return !!(usb_hw->phy_direct & USB_USBPHY_DIRECT_RX_DP_BITS);}
static inline bool dm(void){return !!(usb_hw->phy_direct & USB_USBPHY_DIRECT_RX_DM_BITS);}

static void raw_init(void){
 usb_hw->main_ctrl=0;
 usb_hw->sie_ctrl=0;
 usb_hw->muxing=USB_USB_MUXING_TO_PHY_BITS|USB_USB_MUXING_SOFTCON_BITS;
 usb_hw->phy_direct=0;
 usb_hw->phy_direct_override=
   USB_USBPHY_DIRECT_OVERRIDE_TX_DIFFMODE_OVERRIDE_EN_BITS|
   USB_USBPHY_DIRECT_OVERRIDE_TX_PD_OVERRIDE_EN_BITS|
   USB_USBPHY_DIRECT_OVERRIDE_RX_PD_OVERRIDE_EN_BITS|
   USB_USBPHY_DIRECT_OVERRIDE_TX_DM_OVERRIDE_EN_BITS|
   USB_USBPHY_DIRECT_OVERRIDE_TX_DP_OVERRIDE_EN_BITS|
   USB_USBPHY_DIRECT_OVERRIDE_TX_DM_OE_OVERRIDE_EN_BITS|
   USB_USBPHY_DIRECT_OVERRIDE_TX_DP_OE_OVERRIDE_EN_BITS|
   USB_USBPHY_DIRECT_OVERRIDE_DP_PULLUP_EN_OVERRIDE_EN_BITS|
   USB_USBPHY_DIRECT_OVERRIDE_DP_PULLDN_EN_OVERRIDE_EN_BITS|
   USB_USBPHY_DIRECT_OVERRIDE_DM_PULLDN_EN_OVERRIDE_EN_BITS;
 /* TX values LOW, both OEs OFF, pulls OFF, RX/TX powered. */
 uclr->phy_direct=USB_USBPHY_DIRECT_TX_DP_OE_BITS|USB_USBPHY_DIRECT_TX_DM_OE_BITS;
}

static obs_t observe(bool (*pin)(void)){
 obs_t o={0}; o.min_dt=0xffffffffu; o.initial=pin();
 bool last=o.initial; uint32_t start=time_us_32(), prev=start;
 while((uint32_t)(time_us_32()-start)<OBS_US){
   bool v=pin();
   if(v!=last){
     uint32_t now=time_us_32(),dt=now-prev; prev=now;
     if(v)o.rises++; else o.falls++;
     if(dt<o.min_dt)o.min_dt=dt; if(dt>o.max_dt)o.max_dt=dt;
     if(dt>=MIN_EDGE_US && dt<=MAX_EDGE_US)o.short_intervals++;
     if(dt>=FRAME_GAP_US)o.long_gaps++;
     last=v;
   }
 }
 o.final=last; if(o.min_dt==0xffffffffu)o.min_dt=0; return o;
}

/* Deliberately broad fingerprints. We report raw activity separately from
   interpretation so a failed fingerprint cannot hide electrical activity. */
static uint8_t classify(const obs_t *o){
 if(o->rises==0 && o->falls==0) return o->initial ? 1 : 0; /* static H/L */
 if(o->falls>=100 && o->short_intervals>=100) return 3;    /* clock-like */
 if(o->falls>=5 && o->falls<=40 && o->long_gaps>=3) return 2; /* load/data-like */
 return 4; /* active, unclassified */
}
static void blink(unsigned n){
 for(unsigned i=0;i<n;i++){gpio_put(LED,1);sleep_ms(140);gpio_put(LED,0);sleep_ms(180);}
}
static void report(uint8_t d,uint8_t m){
 /* DP code, pause, DM code, long pause; code meanings in README. */
 blink(d+1); sleep_ms(900); blink(m+1); sleep_ms(2500);
}
int main(void){
 gpio_init(LED);gpio_set_dir(LED,GPIO_OUT);
 blink(1);sleep_ms(500);
 raw_init();sleep_ms(250);
 obs_t od=observe(dp); sleep_ms(50); obs_t om=observe(dm);
 uint8_t cd=classify(&od),cm=classify(&om);
 while(1) report(cd,cm);
}
