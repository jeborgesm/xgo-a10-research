#include <stdint.h>
extern int xgo_stock_fs_open(const char*,int,int);
extern int xgo_stock_fs_fstat(int,void*);
extern int xgo_stock_fs_read(int,void*,unsigned);
extern int xgo_stock_fs_close(int);

typedef union { struct { unsigned char pad[0x38]; uint32_t size; } s; unsigned char raw[160]; } xgo_stat_t;
static uint32_t loaded_cookie=0x58474f30u;
static const char stage2_path[]="/mnt/sda1/ARCADE/compat-safe.xgc";
enum { STAGE2_SIZE=3929, STAGE2_BASE=0x87180000u };

static void zero(void*p,uint32_t n){uint8_t*q=(uint8_t*)p;while(n--)*q++=0;}
static void cache_stage2(void){
 uintptr_t p=(uintptr_t)STAGE2_BASE,end=(uintptr_t)STAGE2_BASE+STAGE2_SIZE;
 p&=~(uintptr_t)31u; end=(end+31u)&~(uintptr_t)31u;
 for(;p<end;p+=32u)__asm__ volatile("cache 1,0(%0)"::"r"(p):"memory");
 __asm__ volatile("sync":::"memory");
 for(p=(uintptr_t)STAGE2_BASE&~(uintptr_t)31u;p<end;p+=32u)__asm__ volatile("cache 0,0(%0)"::"r"(p):"memory");
 __asm__ volatile("sync":::"memory");
}
int xgo_compat_ensure_loaded(void){
 xgo_stat_t st;int fd,n;
 if(loaded_cookie==0x58474f31u)return 0;
 fd=xgo_stock_fs_open(stage2_path,0,0);if(fd<0)return -1;
 zero(&st,sizeof st);
 if(xgo_stock_fs_fstat(fd,&st)<0||st.s.size!=STAGE2_SIZE){xgo_stock_fs_close(fd);return -1;}
 n=xgo_stock_fs_read(fd,(void*)(uintptr_t)STAGE2_BASE,STAGE2_SIZE);
 xgo_stock_fs_close(fd);
 if(n!=STAGE2_SIZE)return -1;
 cache_stage2();loaded_cookie=0x58474f31u;return 0;
}
