/* Device Reader adapter for xgo_arcade_compat_engine.c.
 * Uses the already recovered ALi VFS ABI; no stdio/newlib dependency.
 */
#include <stdint.h>
#include <stddef.h>

typedef int (*read_at_fn)(void *ctx,uint32_t off,void *dst,uint32_t n);
typedef int (*size_fn)(void *ctx,uint32_t *out);
typedef struct {void *ctx;read_at_fn read_at;size_fn size;} Reader;

extern int xgo_stock_fs_open(const char*,int,int);
extern int xgo_stock_fs_fstat(int,void*);
extern int xgo_stock_fs_read(int,void*,unsigned);
extern long long xgo_stock_fs_lseek(int,long long,int);
extern int xgo_stock_fs_close(int);

#define FS_O_RDONLY 0
#define SEEK_SET_XGO 0

typedef union {
 struct { unsigned char pad[0x38]; uint32_t size; } s;
 unsigned char raw[160];
} xgo_stat_t;

typedef struct {int fd;uint32_t size;} XgoFile;

static void zero(void*p,uint32_t n){uint8_t*q=(uint8_t*)p;while(n--)*q++=0;}
static int file_read_at(void*ctx,uint32_t off,void*dst,uint32_t n){
 XgoFile*f=(XgoFile*)ctx;long long p;int got;
 if(!f||f->fd<0||off>f->size||n>f->size-off)return -1;
 p=xgo_stock_fs_lseek(f->fd,(long long)off,SEEK_SET_XGO);
 if(p!=(long long)off)return -1;
 got=xgo_stock_fs_read(f->fd,dst,n);
 return got==(int)n?0:-1;
}
static int file_size(void*ctx,uint32_t*out){XgoFile*f=(XgoFile*)ctx;if(!f||!out||f->fd<0)return -1;*out=f->size;return 0;}

int xgo_reader_open(const char*path,XgoFile*f,Reader*r){
 xgo_stat_t st;int fd;if(!path||!f||!r)return -1;
 fd=xgo_stock_fs_open(path,FS_O_RDONLY,0);if(fd<0)return -1;
 zero(&st,sizeof st);if(xgo_stock_fs_fstat(fd,&st)<0){xgo_stock_fs_close(fd);return -1;}
 f->fd=fd;f->size=st.s.size;r->ctx=f;r->read_at=file_read_at;r->size=file_size;return 0;
}
void xgo_reader_close(XgoFile*f){if(f&&f->fd>=0){xgo_stock_fs_close(f->fd);f->fd=-1;}}
