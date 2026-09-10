/* XGO stock .saN adapter using fixed scratch buffers for MAME2000 snapshot state. */
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

typedef int bool;
#define true 1
#define false 0

extern size_t retro_serialize_size(void);
extern bool retro_serialize(void*,size_t);
extern bool retro_unserialize(const void*,size_t);
extern int xgo_stock_state_compress(void*,unsigned long*,const void*,unsigned long);
extern int xgo_stock_state_uncompress(void*,unsigned long*,const void*,unsigned long);
extern void *xgo_mame_state_raw_buffer(void);
extern void *xgo_mame_state_comp_buffer(void);
extern size_t xgo_mame_state_raw_capacity(void);
extern size_t xgo_mame_state_comp_capacity(void);

int xgo_state_save(const char *path)
{
    FILE*f=0;void*raw=xgo_mame_state_raw_buffer();void*comp=xgo_mame_state_comp_buffer();
    size_t raw_size;unsigned long clen;uint32_t stored;int ok=0;
    if(!path||!*path||!raw||!comp)return 0;
    raw_size=retro_serialize_size();
    if(!raw_size||raw_size>xgo_mame_state_raw_capacity())return 0;
    if(!retro_serialize(raw,raw_size))return 0;
    clen=(unsigned long)xgo_mame_state_comp_capacity();
    if(xgo_stock_state_compress(comp,&clen,raw,(unsigned long)raw_size)!=0)return 0;
    if(!clen||clen>xgo_mame_state_comp_capacity()||clen>0xffffffffu)return 0;
    stored=(uint32_t)clen;
    f=fopen(path,"wb");if(!f)return 0;
    if(fwrite(&stored,sizeof(stored),1,f)!=1)goto out;
    if(fwrite(comp,1,stored,f)!=stored)goto out;
    if(fflush(f)!=0)goto out;
    ok=1;
out:
    if(fclose(f)!=0)ok=0;return ok;
}

int xgo_state_load(const char *path)
{
    FILE*f=0;void*raw=xgo_mame_state_raw_buffer();void*comp=xgo_mame_state_comp_buffer();
    uint32_t stored=0;unsigned long raw_len;int ok=0;
    if(!path||!*path||!raw||!comp)return 0;
    f=fopen(path,"rb");if(!f)return 0;
    if(fread(&stored,sizeof(stored),1,f)!=1)goto out;
    if(!stored||stored>xgo_mame_state_comp_capacity())goto out;
    if(fread(comp,1,stored,f)!=stored)goto out;
    if(fclose(f)!=0)return 0;f=0;
    raw_len=(unsigned long)xgo_mame_state_raw_capacity();
    if(xgo_stock_state_uncompress(raw,&raw_len,comp,(unsigned long)stored)!=0)return 0;
    if(!raw_len||raw_len>xgo_mame_state_raw_capacity())return 0;
    if(!retro_unserialize(raw,(size_t)raw_len))return 0;
    ok=1;
out:
    if(f)fclose(f);return ok;
}
