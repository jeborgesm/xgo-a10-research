#!/usr/bin/env python3
"""Host checks for snapshot ownership, roundtrip and rejection before mutation."""
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "tools/multicore/native_mame2000"

def run(source):
    with tempfile.TemporaryDirectory() as d:
        c = Path(d) / "test.c"
        c.write_text(source)
        subprocess.run(["cc", "-std=gnu99", "-O0", "-fno-pie", "-no-pie",
                        "-I", str(SRC), str(c), "-o", str(Path(d)/"test")], check=True)
        subprocess.run([str(Path(d)/"test")], check=True)

run(r'''
#define sbrk test_sbrk
#include "xgo_mame2000_snapshot_sbrk.c"
void *gp_buf_64m;
unsigned g_run_file_size;
int g_errno;
#define CHECK(x) do {if(!(x))return __LINE__;}while(0)
int main(void) {
    unsigned bases[]={0x81000000u,0x82000000u,0x84000000u};
    unsigned i;
    for(i=0;i<3;++i) {
        unsigned end=bases[i]+ARENA_SIZE;
        if(end>CORE_BASE)end=CORE_BASE;
        gp_buf_64m=(void*)(unsigned long)bases[i];g_run_file_size=59936;
        heap_floor=heap_ptr=heap_end=0;
        CHECK(heap_init());
        CHECK(state_raw_base>=bases[i]+g_run_file_size);
        CHECK(state_comp_base+STATE_COMP_CAP==end);
        CHECK(heap_end==state_raw_base);
        CHECK(test_sbrk(64)!=(void*)-1);
        CHECK(xgo_mame_heap_restore(heap_end));
        CHECK(test_sbrk(1)==(void*)-1);
        CHECK(!xgo_mame_heap_restore(heap_end+1));
    }
    gp_buf_64m=(void*)0x86f00000u;g_run_file_size=64;
    heap_floor=heap_ptr=heap_end=0;
    CHECK(!heap_init());
    CHECK(!xgo_mame_state_raw_buffer());
    return 0;
}
''')

run(r'''
#include <sys/mman.h>
#include <string.h>
#include "xgo_mame2000_snapshot_state.c"
unsigned char region[128];
__asm__(".globl __image_start\n.set __image_start,region\n"
        ".globl _fdata\n.set _fdata,region+64\n"
        ".globl __image_end\n.set __image_end,region+128\n");
uintptr_t xgo_mame_heap_floor(void){return 0x82000000u;}
uintptr_t xgo_mame_heap_ptr(void){return 0x82000020u;}
uintptr_t xgo_mame_heap_limit(void){return 0x82001000u;}
int xgo_mame_heap_restore(uintptr_t p){return p==0x82000020u;}
size_t xgo_mame_state_raw_capacity(void){return 4096;}
#define CHECK(x) do {if(!(x))return __LINE__;}while(0)
int main(void) {
    unsigned char raw[4096];size_t n;
    struct xgo_mame_snapshot_header *h=(void*)raw;
    CHECK(mmap((void*)0x81090000u,0x20000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void*)-1);
    CHECK(mmap((void*)0x82000000u,0x1000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void*)-1);
    strcpy((void*)0x810a0eb0u,"/mnt/sda1/CLASSIC");
    strcpy((void*)0x8109fce8u,"pacman.zip");
    memset(region,1,128);memset((void*)0x82000000u,2,32);
    n=xgo_snapshot_serialize_size();CHECK(xgo_snapshot_serialize(raw,n));
    memset(region+64,3,64);memset((void*)0x82000000u,4,32);
    CHECK(xgo_snapshot_unserialize(raw,n));
    CHECK(region[64]==1 && *(unsigned char*)0x82000000u==2);
    region[64]=9;
    h->heap_size=0xffffffffu;
    CHECK(!xgo_snapshot_unserialize(raw,n) && region[64]==9);
    h->heap_size=32;
    strcpy((void*)0x8109fce8u,"galaga.zip");
    CHECK(!xgo_snapshot_unserialize(raw,n) && region[64]==9);
    strcpy((void*)0x8109fce8u,"pacman.zip");
    region[0]=7;
    CHECK(!xgo_snapshot_unserialize(raw,n) && region[64]==9);
    CHECK(!xgo_snapshot_unserialize(raw,n-1));
    return 0;
}
''')
print("PASS: arena ownership, bounds, snapshot roundtrip, wrong game/core and malformed state rejection")
