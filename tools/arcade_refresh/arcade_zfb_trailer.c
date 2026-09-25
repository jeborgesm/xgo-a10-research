/* Arcade ZFB trailer splice for the Test75 materializer.
 *
 * Link address: 0x87002000.  Entered from patched +0x09B4 with:
 *   a0 = open destination ZFB handle (Test75 frame +0x44)
 *   a1 = NUL-terminated driver stem (golden workspace 0x87600500)
 *
 * Writes: 00 00 00 00 + <stem> + ".zip" + 00 00
 * Returns 0 on exact-write success, -1 on failure.
 */
typedef unsigned int u32;
typedef int s32;
typedef u32 (*write_fn)(const void *,u32,u32,void *);
#define FWRITE ((write_fn)0x802B42ACu)

static u32 slen(const char *s) {
    u32 n=0; while(s[n]) { if(n>=120) return 0xffffffffu; n++; } return n;
}

int arcade_zfb_trailer(void *dst,const char *stem) {
    static const unsigned char zero4[4]={0,0,0,0};
    static const char ext[]=".zip";
    static const unsigned char zero2[2]={0,0};
    u32 n=slen(stem);
    if(n==0xffffffffu || n==0) return -1;
    if(FWRITE(zero4,1,4,dst)!=4) return -1;
    if(FWRITE(stem,1,n,dst)!=n) return -1;
    if(FWRITE(ext,1,4,dst)!=4) return -1;
    if(FWRITE(zero2,1,2,dst)!=2) return -1;
    return 0;
}
