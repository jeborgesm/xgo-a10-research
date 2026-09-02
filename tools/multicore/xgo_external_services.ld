/*
 * Minimal stock-firmware services exported to XGO external cores.
 *
 * Deliberately DO NOT define malloc/free/realloc/calloc, stdio, string, math,
 * or compiler-runtime symbols here. External cores carry their own static
 * newlib/libm/libgcc and private sbrk() policy. Binding those names to stock
 * firmware would mix allocator/runtime ownership across the 0x87000000 trust
 * boundary.
 */

/* XGO filesystem/VFS primitives. */
fs_sync     = 0x802abc30;
fs_open     = 0x802abd58;
fs_opendir  = 0x802abe28;
fs_mkdir    = 0x802abeb4;
fs_access   = 0x802abfe8;
fs_fstat    = 0x802ac080;
fs_stat     = 0x802ac0a4;
fs_read     = 0x802ac150;
fs_write    = 0x802ac274;
fs_lseek    = 0x802ac394;
fs_readdir  = 0x802ac438;
fs_close    = 0x802ac4d4;
fs_closedir = 0x802ac4f0;

/* Scheduler/timing service used by external libc glue. */
os_get_tick_count = 0x8030fec8;

/* Stock errno mirror used when fs_* reports failure. */
g_errno = 0x80c2d640;

/*
 * Stock 64-MiB scratch arena and preloaded content size. Native NES launch
 * reserves the ROM prefix and gives only the remainder to external newlib.
 */
g_run_file_size = 0x80c33a7c;
gp_buf_64m      = 0x80c33ad8;
