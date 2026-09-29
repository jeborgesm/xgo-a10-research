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
static int ends_zip(const char *s){size_t n=0;while(s[n])n++;return n>4&&s[n-4]=='.'&&(s[n-3]=='z'||s[n-3]=='Z')&&(s[n-2]=='i'||s[n-2]=='I')&&(s[n-1]=='p'||s[n-1]=='P');}
int xgo_arcade_preflight_family(unsigned fam, validate_fn validate, materialize_fn materialize){
 dir_open_fn op=(dir_open_fn)(uintptr_t)0x807d40c4u;dir_next_fn nx=(dir_next_fn)(uintptr_t)0x807d4124u;dir_close_fn cl=(dir_close_fn)(uintptr_t)0x807d41f4u;
 Entry e;XDir*d=op(roots[fam]);if(!d)return 0;int changed=0;
 while(nx(d,&e)>=0){if(e.is_dir||!ends_zip(e.name))continue;char path[320],stem[256];size_t i=0,j=0;const char*r=roots[fam];while(r[i]&&i<sizeof(path)-2){path[i]=r[i];i++;}path[i++]='/';while(e.name[j]&&i<sizeof(path)-1){path[i++]=e.name[j++];}path[i]=0;j=0;while(e.name[j]&&j<sizeof(stem)-1&&e.name[j]!='.'){stem[j]=e.name[j];j++;}stem[j]=0;int v=validate(fam,path,stem);if(v<0){cl(d);return -1;}if(v==0){int m=materialize();if(m<0){cl(d);return -1;}changed|=(m>0);}}
 cl(d);return changed;
}
