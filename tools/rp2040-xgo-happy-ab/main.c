#include <stdint.h>
#include <stdbool.h>
#include "pico/stdlib.h"
#include "hardware/structs/usb.h"
#include "hardware/regs/usb.h"
#include "hardware/address_mapped.h"
#define LED 25u
#define EDGE_US 12u
#define LOAD_US 20000u
#ifndef CLOCK_IS_DP
#define CLOCK_IS_DP 1
#endif
static usb_hw_t *const uset=(usb_hw_t*)hw_set_alias_untyped(usb_hw);
static usb_hw_t *const uclr=(usb_hw_t*)hw_clear_alias_untyped(usb_hw);
static inline bool dp(void){return !!(usb_hw->phy_direct&USB_USBPHY_DIRECT_RX_DP_BITS);}
static inline bool dm(void){return !!(usb_hw->phy_direct&USB_USBPHY_DIRECT_RX_DM_BITS);}
static inline bool clk(void){return CLOCK_IS_DP?dp():dm();}
static inline bool dat(void){return CLOCK_IS_DP?dm():dp();}
static inline uint32_t data_oe(void){return CLOCK_IS_DP?USB_USBPHY_DIRECT_TX_DM_OE_BITS:USB_USBPHY_DIRECT_TX_DP_OE_BITS;}
static inline void release(void){uclr->phy_direct=data_oe();}
static inline void sink(void){uset->phy_direct=data_oe();}
static bool waitv(bool (*fn)(void),bool v,uint32_t us){uint32_t t=time_us_32();while(fn()!=v)if((uint32_t)(time_us_32()-t)>us)return false;return true;}
static void init_raw(void){
 usb_hw->main_ctrl=0; usb_hw->sie_ctrl=0;
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
 release();
}
static bool frame(uint16_t mask){
 release();
 if(!waitv(dat,false,LOAD_US))return false;
 if(!waitv(dat,true,EDGE_US))return false;
 if(mask&1u)sink();else release();
 for(unsigned slot=1;slot<12;slot++){
  if(!waitv(clk,false,EDGE_US)){release();return false;}
  if(mask&(1u<<slot))sink();else release();
  if(!waitv(clk,true,EDGE_US)){release();return false;}
 }
 if(!waitv(clk,false,EDGE_US)){release();return false;}
 release(); (void)waitv(clk,true,EDGE_US); return true;
}
typedef struct{uint16_t mask,polls;} phase_t;
static const phase_t script[]={
 {1u<<11,50},{(1u<<11)|(1u<<0)|(1u<<5),12},{1u<<11,18},{0,8},
 {1u<<10,50},{1u<<9,24},{(1u<<0)|(1u<<5),12},{0,24}
};
int main(void){
 gpio_init(LED);gpio_set_dir(LED,GPIO_OUT);gpio_put(LED,1);
 init_raw();sleep_ms(250);
 size_t p=0;uint16_t left=script[0].polls;
 while(1){if(frame(script[p].mask)){gpio_xor_mask(1u<<LED);if(--left==0){p=(p+1)%(sizeof(script)/sizeof(script[0]));left=script[p].polls;}}else{release();}}
}
