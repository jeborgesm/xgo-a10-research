#include <stdint.h>
#include <stddef.h>
typedef void XDir;
typedef struct { uint8_t is_dir; uint8_t pad[7]; char name[0x230]; } Entry;
typedef XDir *(*dir_open_fn)(const char *);
typedef int (*dir_next_fn)(XDir *, Entry *);
typedef void (*dir_close_fn)(XDir *);
typedef int (*validate_fn)(unsigned,const char*,const char*);
typedef int (*materialize_fn)(void);
static const char *roots[4]={"/mnt/sda1/ARCADE/CPS1/import","/mnt/sda1/ARCADE/CPS2/import","/mnt/sda1/ARCADE/IGS/import","/mnt/sda1/ARCADE/NEOGEO/import"};
static int ends_zip(const char*s){size_t n=0;while(s[n])n++;return n>4&&s[n-4]=='.'&&(s[n-3]=='z'||s[n-3]=='Z')&&(s[n-2]=='i'||s[n-2]=='I')&&(s[n-1]=='p'||s[n-1]=='P');}
/* Preflight is deliberately a phase boundary: enumerate and validate the
 * complete family before the materializer is entered. No artwork/ZFB/runtime
 * publication occurs while the directory/validator transaction is active.
 * Test11 uses an all-compatible family as the dynamic-enumeration proof.
 */
int xgo_arcade_preflight_family(unsigned fam,validate_fn validate,materialize_fn materialize){
 dir_open_fn op=(dir_open_fn)(uintptr_t)0x807d40c4u;dir_next_fn nx=(dir_next_fn)(uintptr_t)0x807d4124u;dir_close_fn cl=(dir_close_fn)(uintptr_t)0x807d41f4u;
 Entry e;XDir*d;int saw=0;
 if(fam>3||!validate||!materialize)return -1;
 d=op(roots[fam]);if(!d)return 0;
 while(nx(d,&e)>=0){
  char path[320],stem[256];size_t i=0,j=0;int v;const char*r=roots[fam];
  if(e.is_dir||!ends_zip(e.name))continue;
  while(r[i]&&i<sizeof(path)-2){path[i]=r[i];i++;}path[i++]='/';
  while(e.name[j]&&i<sizeof(path)-1){path[i++]=e.name[j++];}path[i]=0;
  j=0;while(e.name[j]&&j<sizeof(stem)-1&&e.name[j]!='.'){stem[j]=e.name[j];j++;}stem[j]=0;
  v=validate(fam,path,stem);
  if(v!=0){cl(d);return v<0?-1:0;}
  saw=1;
 }
 cl(d);
 if(!saw)return 0;
 return materialize();
}
