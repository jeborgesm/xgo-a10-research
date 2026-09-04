/* Generic libretro save-state adapter for the stock XGO frontend contract. */
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#ifndef XGO_STATE_MAX_SERIALIZED
#define XGO_STATE_MAX_SERIALIZED (16u * 1024u * 1024u)
#endif
#ifndef XGO_STATE_MAX_COMPRESSED
#define XGO_STATE_MAX_COMPRESSED (32u * 1024u * 1024u)
#endif

typedef int bool;
#define true 1
#define false 0

extern size_t retro_serialize_size(void);
extern bool retro_serialize(void *data, size_t size);
extern bool retro_unserialize(const void *data, size_t size);
extern int xgo_stock_state_compress(void *, unsigned long *, const void *, unsigned long);
extern int xgo_stock_state_uncompress(void *, unsigned long *, const void *, unsigned long);
extern int xgo_stock_fs_open(const char *, int, int);
extern int xgo_stock_fs_write(int, const void *, unsigned);
extern int xgo_stock_fs_close(int);

#define FS_O_WRONLY 0x0001
#define FS_O_CREAT  0x0100
#define FS_O_TRUNC  0x0200
#define PROBE_PATH "/mnt/sda1/xgo-state-probe.txt"

static unsigned append_text(char *dst, unsigned pos, unsigned cap, const char *src)
{
    while (src && *src && pos + 1u < cap) dst[pos++] = *src++;
    if (cap) dst[pos < cap ? pos : cap - 1u] = 0;
    return pos;
}

static void probe_stage(const char *stage, const char *path)
{
    char buf[512]; unsigned n = 0; int fd;
    n = append_text(buf,n,sizeof(buf),"stage="); n = append_text(buf,n,sizeof(buf),stage);
    n = append_text(buf,n,sizeof(buf),"\npath="); n = append_text(buf,n,sizeof(buf),path ? path : "(null)");
    n = append_text(buf,n,sizeof(buf),"\n");
    fd = xgo_stock_fs_open(PROBE_PATH, FS_O_WRONLY|FS_O_CREAT|FS_O_TRUNC, 0666);
    if (fd >= 0) { (void)xgo_stock_fs_write(fd,buf,n); (void)xgo_stock_fs_close(fd); }
}

int xgo_state_save(const char *path)
{
    FILE *file = NULL; void *raw = NULL, *compressed = NULL;
    size_t raw_size, compressed_capacity; unsigned long compressed_len;
    uint32_t stored_len; int ok = 0;
    probe_stage("S1-save-entered", path);
    if (!path || !*path) return 0;
    raw_size = retro_serialize_size();
    if (!raw_size || raw_size > XGO_STATE_MAX_SERIALIZED) { probe_stage("S2-serialize-size-fail",path); return 0; }
    probe_stage("S2-serialize-size-ok",path);
    if (raw_size > XGO_STATE_MAX_COMPRESSED/2u) return 0;
    compressed_capacity = raw_size*2u;
    raw = malloc(raw_size); if (!raw) { probe_stage("S3-raw-malloc-fail",path); goto out; }
    probe_stage("S3-raw-malloc-ok",path);
    if (!retro_serialize(raw,raw_size)) { probe_stage("S4-serialize-fail",path); goto out; }
    probe_stage("S4-serialize-ok",path);
    compressed = malloc(compressed_capacity); if (!compressed) { probe_stage("S5-compressed-malloc-fail",path); goto out; }
    probe_stage("S5-compressed-malloc-ok",path);
    compressed_len=(unsigned long)compressed_capacity;
    if (xgo_stock_state_compress(compressed,&compressed_len,raw,(unsigned long)raw_size)!=0) { probe_stage("S6-compress-fail",path); goto out; }
    if (!compressed_len || compressed_len>compressed_capacity || compressed_len>0xffffffffu) { probe_stage("S6-compress-length-fail",path); goto out; }
    probe_stage("S6-compress-ok",path); stored_len=(uint32_t)compressed_len;
    file=fopen(path,"wb"); if (!file) { probe_stage("S7-fopen-fail",path); goto out; }
    probe_stage("S7-fopen-ok",path);
    if (fwrite(&stored_len,sizeof(stored_len),1,file)!=1) { probe_stage("S8-header-write-fail",path); goto out; }
    probe_stage("S8-header-write-ok",path);
    if (fwrite(compressed,1,stored_len,file)!=stored_len) { probe_stage("S9-payload-write-fail",path); goto out; }
    probe_stage("S9-payload-write-ok",path);
    if (fflush(file)!=0) { probe_stage("S10-fflush-fail",path); goto out; }
    probe_stage("S10-save-success",path); ok=1;
out: if(file)fclose(file); if(compressed)free(compressed); if(raw)free(raw); return ok;
}

int xgo_state_load(const char *path)
{
    FILE *file=NULL; void *raw=NULL,*compressed=NULL; size_t serialize_size,raw_capacity;
    unsigned long raw_len; uint32_t stored_len=0; int ok=0;
    probe_stage("L1-load-entered",path); if(!path||!*path)return 0;
    file=fopen(path,"rb"); if(!file){probe_stage("L2-fopen-fail",path);goto out;} probe_stage("L2-fopen-ok",path);
    if(fread(&stored_len,sizeof(stored_len),1,file)!=1){probe_stage("L3-header-read-fail",path);goto out;}
    if(!stored_len||stored_len>XGO_STATE_MAX_COMPRESSED){probe_stage("L3-header-invalid",path);goto out;}
    compressed=malloc((size_t)stored_len); if(!compressed){probe_stage("L4-compressed-malloc-fail",path);goto out;}
    if(fread(compressed,1,stored_len,file)!=stored_len){probe_stage("L5-payload-read-fail",path);goto out;}
    serialize_size=retro_serialize_size(); if(!serialize_size||serialize_size>XGO_STATE_MAX_SERIALIZED){probe_stage("L6-serialize-size-fail",path);goto out;}
    if(serialize_size>XGO_STATE_MAX_SERIALIZED/2u)goto out; raw_capacity=serialize_size*2u;
    raw=malloc(raw_capacity); if(!raw){probe_stage("L7-raw-malloc-fail",path);goto out;}
    raw_len=(unsigned long)raw_capacity;
    if(xgo_stock_state_uncompress(raw,&raw_len,compressed,(unsigned long)stored_len)!=0){probe_stage("L8-uncompress-fail",path);goto out;}
    if(!raw_len||raw_len>raw_capacity){probe_stage("L8-uncompress-length-fail",path);goto out;}
    if(!retro_unserialize(raw,(size_t)raw_len)){probe_stage("L9-unserialize-fail",path);goto out;}
    probe_stage("L10-load-success",path); ok=1;
out: if(file)fclose(file); if(compressed)free(compressed); if(raw)free(raw); return ok;
}
