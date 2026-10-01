/* XGO Arcade compatibility Stage2 device entry.
 * Link base: 0x87180000.  Static tail scratch is part of Stage2 BSS.
 */
#include <stdint.h>

enum { ZIP_TAIL_MAX = 65557 };
typedef int (*read_at_fn)(void*,uint32_t,void*,uint32_t);
typedef int (*size_fn)(void*,uint32_t*);
typedef struct {void *ctx;read_at_fn read_at;size_fn size;} Reader;
typedef struct {int fd;uint32_t size;} XgoFile;

extern int xgo_reader_open(const char*,XgoFile*,Reader*);
extern void xgo_reader_close(XgoFile*);
extern int xgo_arcade_validate(Reader*,Reader*,const uint8_t[32],uint8_t,const char*,uint8_t*,uint32_t);

static uint8_t zip_tail[ZIP_TAIL_MAX];
static const char manifest_path[]="/mnt/sda1/ARCADE/.xgo-compat";

/* Exact firmware SHA embedded in the XACM v1 generated for this integration
 * checkpoint. Packaging must reject any firmware/XACM mismatch.
 */
static const uint8_t expected_firmware_sha[32]={
 0x86,0x9e,0x05,0x6d,0x00,0x03,0x37,0xe1,
 0xb1,0x0c,0x83,0x4f,0x0a,0x93,0x24,0x4c,
 0x0a,0xbd,0x99,0x45,0x7c,0x1c,0x83,0x74,
 0x36,0x7f,0x7d,0xff,0x20,0xe4,0x3d,0xaf
};

int compat_validate(unsigned family,const char *source_path,const char *stem){
 XgoFile mf={-1,0},zf={-1,0};Reader mr,zr;int v;
 if(family>3||!source_path||!stem)return -1;
 if(xgo_reader_open(manifest_path,&mf,&mr))return -1;
 if(xgo_reader_open(source_path,&zf,&zr)){xgo_reader_close(&mf);return -1;}
 v=xgo_arcade_validate(&mr,&zr,expected_firmware_sha,(uint8_t)family,stem,zip_tail,sizeof zip_tail);
 xgo_reader_close(&zf);xgo_reader_close(&mf);return v;
}
