#include <stdint.h>
#include <stdbool.h>
#include "pico/stdlib.h"
#include "hardware/structs/usb.h"
#include "hardware/regs/usb.h"
#include "hardware/address_mapped.h"
#define LED 25u
#define OBSERVE_MS 220u
#define GAP_US 100u
#define EDGE_US 12u
static usb_hw_t *const uset=(usb_hw_t*)hw_set_alias_untyped(usb_hw);
static usb_hw_t *const uclr=(usb_hw_t*)hw_clear_alias_untyped(usb_hw);
typedef struct{uint32_t falls,frames,good12;} stats_t;
static inline bool dp(void){return !!(usb_hw->phy_direct&USB_USBPHY_DIRECT_RX_DP_BITS);}
static inline bool dm(void){return !!(usb_hw->phy_direct&USB_USBPHY_DIRECT_RX_DM_BITS);}
static void blink(unsigned n){for(unsigned i=0;i<n;i++){gpio_put(LED,1);sleep_ms(110);gpio_put(LED,0);sleep_ms(130);}sleep_ms(700);}
static void passive(void){usb_hw->main_ctrl=0;usb_hw->sie_ctrl=0;usb_hw->muxing=USB_USB_MUXING_TO_PHY_BITS|USB_USB_MUXING_SOFTCON_BITS;usb_hw->phy_direct=0;usb_hw->phy_direct_override=USB_USBPHY_DIRECT_OVERRIDE_DP_PULLUP_EN_OVERRIDE_EN_BITS|USB_USBPHY_DIRECT_OVERRIDE_DP_PULLDN_EN_OVERRIDE_EN_BITS|USB_USBPHY_DIRECT_OVERRIDE_DM_PULLDN_EN_OVERRIDE_EN_BITS|USB_USBPHY_DIRECT_OVERRIDE_TX_DP_OE_OVERRIDE_EN_BITS|USB_USBPHY_DIRECT_OVERRIDE_TX_DM_OE_OVERRIDE_EN_BITS|USB_USBPHY_DIRECT_OVERRIDE_TX_DIFFMODE_OVERRIDE_EN_BITS|USB_USBPHY_DIRECT_OVERRIDE_TX_PD_OVERRIDE_EN_BITS|USB_USBPHY_DIRECT_OVERRIDE_RX_PD_OVERRIDE_EN_BITS;}
static stats_t observe(bool(*line)(void)){stats_t s={0};bool p=line();uint32_t start=to_ms_since_boot(get_absolute_time()),lastfall=0,inframe=0;while((uint32_t)(to_ms_since_boot(get_absolute_time())-start)<OBSERVE_MS){bool v=line();if(p&&!v){uint32_t now=time_us_32(),dt=now-lastfall;s.falls++;if(!lastfall||dt>GAP_US){if(inframe==12)s.good12++;s.frames++;inframe=1;}else inframe++;lastfall=now;}p=v;}if(inframe==12)s.good12++;return s;}
static inline void sink(void){uset->phy_direct=USB_USBPHY_DIRECT_TX_DM_OE_BITS;}
static inline void release(void){uclr->phy_direct=USB_USBPHY_DIRECT_TX_DM_OE_BITS;}
static bool waitdp(bool v,uint32_t us){uint32_t t=time_us_32();while(dp()!=v)if((uint32_t)(time_us_32()-t)>us)return false;return true;}
static bool emit(uint16_t mask){release();while(!dp());uint32_t h=time_us_32();while(dp()){if((uint32_t)(time_us_32()-h)>GAP_US)break;}if(!dp()||!waitdp(0,20000))return false;for(unsigned slot=1;slot<12;slot++){if(mask&(1u<<slot))sink();else release();if(!waitdp(1,EDGE_US)){release();return false;}if(slot<11&&!waitdp(0,EDGE_US)){release();return false;}}release();return true;}
int main(void){gpio_init(LED);gpio_set_dir(LED,GPIO_OUT);passive();sleep_ms(300);stats_t a=observe(dp),b=observe(dm);blink(1);bool dpclk=a.good12>=5&&a.good12>b.good12;if(dpclk)blink(2);else if(b.good12>=5)blink(3);else while(1)blink(4);if(!dpclk)while(1)blink(3);const uint16_t seq[]={1u<<11,1u<<10,1u<<9,1u<<0,0};unsigned ph=0,n=0;bool l=0;while(1){if(emit(seq[ph])){gpio_put(LED,l=!l);if(++n>=62){n=0;ph=(ph+1)%5;}}}}
