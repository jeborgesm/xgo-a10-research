/*
 * XGO Arcade Refresh compatibility engine.
 *
 * Pure decision engine shared by the host harness and the future XGO wrapper.
 * I/O is deliberately callback-based: no libc allocation, no decompression,
 * no FBA globals.  The device wrapper only has to supply read-at/file-size.
 */
#include <stdint.h>
#include <stddef.h>

enum { XGO_COMPAT=0, XGO_INCOMPATIBLE=1, XGO_UNSUPPORTED=2, XGO_VALIDATOR_ERROR=-1 };
enum { XACM_HEADER=52, XACM_FAMILY=12, XACM_DRIVER=20, XACM_ROM=16 };
#define EOCD 0x06054b50u
#define CEN  0x02014b50u
#define ZIP_TAIL_MAX 65557u
#define NAME_MAX 255u

typedef int (*read_at_fn)(void *ctx, uint32_t off, void *dst, uint32_t n);
typedef int (*size_fn)(void *ctx, uint32_t *out);

typedef struct { void *ctx; read_at_fn read_at; size_fn size; } Reader;
typedef struct { uint32_t name,size,crc,type; } Rom;
typedef struct { uint32_t no,po,bo,first; uint16_t count; uint8_t family,res; } Driver;

static uint16_t u16(const uint8_t*p){return (uint16_t)(p[0]|((uint16_t)p[1]<<8));}
static uint32_t u32(const uint8_t*p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static int eq(const char*a,const char*b){while(*a&&*a==*b){a++;b++;}return *a==*b;}
static char lower(char c){return c>='A'&&c<='Z'?(char)(c+32):c;}
static int ends_slash(const char*s){char last=0;while(*s)last=*s++;return last=='/';}
static int ieq(const char*a,const char*b){while(*a&&*b&&lower(*a)==lower(*b)){a++;b++;}return !*a&&!*b;}
static int rd(Reader*r,uint32_t o,void*d,uint32_t n){return r&&r->read_at&&r->read_at(r->ctx,o,d,n)==0;}

typedef struct {
 Reader *r; uint32_t nfam,ndrv,nrom,nstr,fam_off,drv_off,rom_off,str_off,total;
 uint8_t firmware_sha[32];
} Manifest;

static int manifest_open(Reader*r,const uint8_t expected_sha[32],Manifest*m){
 uint8_t h[XACM_HEADER]; uint32_t sz,i;
 if(!r||!m||!r->size||r->size(r->ctx,&sz)||!rd(r,0,h,sizeof h))return -1;
 if(h[0]!='X'||h[1]!='A'||h[2]!='C'||h[3]!='M'||u16(h+4)!=1||u16(h+6)!=4)return -1;
 m->r=r;m->nfam=4;m->ndrv=u32(h+8);m->nrom=u32(h+12);m->nstr=u32(h+16);
 for(i=0;i<32;i++){m->firmware_sha[i]=h[20+i];if(expected_sha&&h[20+i]!=expected_sha[i])return -1;}
 m->fam_off=52;m->drv_off=m->fam_off+4*12u;m->rom_off=m->drv_off+m->ndrv*20u;
 m->str_off=m->rom_off+m->nrom*16u;m->total=m->str_off+m->nstr;
 return m->total==sz?0:-1;
}
static int mstr(Manifest*m,uint32_t off,char*out,uint32_t cap){
 uint32_t i;if(!out||cap<1)return -1;if(!off){out[0]=0;return 0;}if(off>=m->nstr)return -1;
 for(i=0;i+1<cap&&off+i<m->nstr;i++){if(!rd(m->r,m->str_off+off+i,out+i,1))return -1;if(!out[i])return 0;}
 out[cap-1]=0;return -1;
}
static int driver_at(Manifest*m,uint32_t i,Driver*d){
 uint8_t b[20];if(i>=m->ndrv||!rd(m->r,m->drv_off+i*20u,b,20))return -1;
 d->no=u32(b);d->po=u32(b+4);d->bo=u32(b+8);d->first=u32(b+12);d->count=u16(b+16);d->family=b[18];d->res=b[19];
 return d->first+d->count<=m->nrom?0:-1;
}
static int rom_at(Manifest*m,uint32_t i,Rom*x){
 uint8_t b[16];if(i>=m->nrom||!rd(m->r,m->rom_off+i*16u,b,16))return -1;
 x->name=u32(b);x->size=u32(b+4);x->crc=u32(b+8);x->type=u32(b+12);return 0;
}

/* Enumerate metadata twice if necessary; keeps RAM bounded instead of retaining
 * a potentially large central directory. */
typedef struct { uint32_t cd_off,cd_size,count; } Zip;
static int zip_open(Reader*r,Zip*z,uint8_t*tail,uint32_t tailcap){
 uint32_t sz,n,start,p;const uint8_t *e;
 if(!r||!z||!tail||tailcap<ZIP_TAIL_MAX||r->size(r->ctx,&sz))return -1;
 n=sz<ZIP_TAIL_MAX?sz:ZIP_TAIL_MAX;start=sz-n;if(!rd(r,start,tail,n))return -1;
 if(n<22)return -1;\n p=n-22;
 for(;;){if(u32(tail+p)==EOCD)break;if(!p)return -1;p--;}
 e=tail+p;if(p+22u>n||p+22u+u16(e+20)!=n)return -1;
 if(u16(e+4)||u16(e+6)||u16(e+8)!=u16(e+10))return -1;
 if(u16(e+10)==0xffff||u32(e+12)==0xffffffffu||u32(e+16)==0xffffffffu)return -1;
 z->count=u16(e+10);z->cd_size=u32(e+12);z->cd_off=u32(e+16);
 if(z->cd_off>sz||z->cd_size>sz-z->cd_off)return -1;
 /* Close count/size geometry once here so every later entry lookup inherits it. */
 {uint32_t o=z->cd_off,used=0,i;uint8_t h[46];
  for(i=0;i<z->count;i++){uint32_t need;uint16_t nl,xl,cl;
   if(used+46u>z->cd_size||!rd(r,o,h,46)||u32(h)!=CEN)return -1;
   nl=u16(h+28);xl=u16(h+30);cl=u16(h+32);need=46u+nl+xl+cl;
   if(need>z->cd_size-used)return -1;\n   o+=need;used+=need;
  }
  if(used!=z->cd_size)return -1;
 }
 return 0;
}
typedef struct {char name[NAME_MAX+1];uint32_t size,crc;} Entry;
static int zip_entry(Reader*r,Zip*z,uint32_t wanted,Entry*out){
 uint32_t o=z->cd_off,i,used=0;uint8_t h[46];
 for(i=0;i<=wanted;i++){
  uint16_t flags,nl,xl,cl,ds;uint32_t cs,us,lo,need;
  if(used+46u>z->cd_size||!rd(r,o,h,46)||u32(h)!=CEN)return -1;
  flags=u16(h+8);out->crc=u32(h+16);cs=u32(h+20);us=u32(h+24);nl=u16(h+28);xl=u16(h+30);cl=u16(h+32);ds=u16(h+34);lo=u32(h+42);
  if((flags&1)||cs==0xffffffffu||us==0xffffffffu||lo==0xffffffffu||ds==0xffff||ds)return -1;
  need=46u+nl+xl+cl;if(need>z->cd_size-used||nl>NAME_MAX)return -1;
  if(i==wanted){uint32_t j,base=0;if(!rd(r,o+46,out->name,nl))return -1;out->name[nl]=0;
   for(j=0;j<nl;j++)if(out->name[j]=='/')base=j+1;
   if(base){for(j=0;base+j<=nl;j++)out->name[j]=out->name[base+j];}
   out->size=us;return 0;}
  o+=need;used+=need;
 }
 return -1;
}

int xgo_arcade_validate(Reader*xacm,Reader*zip,const uint8_t expected_sha[32],uint8_t family,const char*stem,uint8_t*tail,uint32_t tailcap){
 Manifest m;Driver d;Rom rr;Zip z;Entry e;char s[NAME_MAX+1];uint8_t fb[12];uint32_t first,count,i,j;int found=0;
 if(family>=4||!stem||manifest_open(xacm,expected_sha,&m))return XGO_VALIDATOR_ERROR;
 if(!rd(xacm,m.fam_off+family*12u,fb,12))return XGO_VALIDATOR_ERROR;\n first=u32(fb+4);count=u32(fb+8);
 if(first>m.ndrv||count>m.ndrv-first)return XGO_VALIDATOR_ERROR;
 for(i=0;i<count;i++){if(driver_at(&m,first+i,&d)||d.family!=family||d.res||mstr(&m,d.no,s,sizeof s))return XGO_VALIDATOR_ERROR;if(eq(s,stem)){found=1;break;}}
 if(!found)return XGO_UNSUPPORTED;\n if(zip_open(zip,&z,tail,tailcap))return XGO_VALIDATOR_ERROR;
 for(i=0;i<d.count;i++){int crc_hit=0,name_hit=0;if(rom_at(&m,d.first+i,&rr)||mstr(&m,rr.name,s,sizeof s))return XGO_VALIDATOR_ERROR;
  if(!rr.type||!rr.size||!rr.crc||(rr.type&(1u<<27)))continue;
  for(j=0;j<z.count;j++){if(zip_entry(zip,&z,j,&e))return XGO_VALIDATOR_ERROR;if(!e.name[0]||ends_slash(e.name))continue;if(e.crc==rr.crc&&e.size==rr.size){crc_hit=1;break;}if(ieq(e.name,s))name_hit=1;}
  if(!crc_hit&&!name_hit)return XGO_INCOMPATIBLE;
 }
 return XGO_COMPAT;
}
