/* Arcade ZFB trailer splice for the Test75 materializer.
 * Link at 0x87002000. a0=open ZFB handle, a1=driver stem.
 * Writes: 4x00 + stem + ".zip" + 2x00. No GP/data-section dependency.
 */
typedef unsigned int u32;
typedef u32 (*write_fn)(const void *,u32,u32,void *);
#define FWRITE ((write_fn)0x802B42ACu)
static u32 slen(const char *s){u32 n=0;while(s[n]){if(n>=120)return 0xffffffffu;n++;}return n;}
int arcade_zfb_trailer(void *dst,const char *stem){
    u32 words[2]; u32 n=slen(stem);
    if(n==0xffffffffu||n==0)return -1;
    words[0]=0;
    if(FWRITE(&words[0],1,4,dst)!=4)return -1;
    if(FWRITE(stem,1,n,dst)!=n)return -1;
    words[0]=0x70697a2eu;
    if(FWRITE(&words[0],1,4,dst)!=4)return -1;
    words[0]=0;
    if(FWRITE(&words[0],1,2,dst)!=2)return -1;
    return 0;
}
