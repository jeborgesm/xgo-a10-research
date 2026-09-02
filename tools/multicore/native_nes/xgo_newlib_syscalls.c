/*
 * Minimal newlib/POSIX bridge for XGO external cores.
 *
 * Memory allocation is intentionally NOT implemented here. The external core
 * supplies its own sbrk() (native NES: xgo_preloaded_rom_sbrk.c) so malloc and
 * friends remain isolated from the stock firmware allocator.
 *
 * This file exposes ordinary POSIX-ish calls expected by newlib/libretro-common
 * and translates them to the already-mapped XGO fs_* primitives.
 */

#include <sys/types.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <fcntl.h>
#include <errno.h>
#include <stdint.h>
#include <stddef.h>
#include <time.h>
#include <unistd.h>

/* Resolved by xgo_external_stock_services.ld. */
extern int fs_open(const char *path, int flags, int mode);
extern int fs_read(int fd, void *buf, unsigned count);
extern int fs_write(int fd, const void *buf, unsigned count);
extern long long fs_lseek(int fd, long long offset, int whence);
extern int fs_close(int fd);
extern int fs_stat(const char *path, void *buf);
extern int fs_fstat(int fd, void *buf);
extern int fs_mkdir(const char *path, int mode);
extern unsigned os_get_tick_count(void);
extern int g_errno;

/* XGO/VFS flag values follow the same ALi filesystem contract used upstream. */
#ifndef FS_O_RDONLY
#define FS_O_RDONLY 0x0000
#define FS_O_WRONLY 0x0001
#define FS_O_RDWR   0x0002
#define FS_O_APPEND 0x0008
#define FS_O_CREAT  0x0200
#define FS_O_TRUNC  0x0400
#endif

/* Stock fs_stat/fs_fstat return a much larger ALi structure. Only the fields
 * needed by external libretro-common are translated into struct stat. */
typedef union {
    struct {
        unsigned char pad_type[0x18];
        uint32_t type;
    } t;
    struct {
        unsigned char pad_size[0x38];
        uint32_t size;
    } s;
    unsigned char raw[160];
} xgo_fs_stat_t;

static void import_errno(void)
{
    if (g_errno)
        errno = g_errno;
}

int open(const char *path, int flags, ...)
{
    int f = 0;
    int ret;

    if ((flags & O_ACCMODE) == O_WRONLY) f |= FS_O_WRONLY;
    else if ((flags & O_ACCMODE) == O_RDWR) f |= FS_O_RDWR;
    else f |= FS_O_RDONLY;
    if (flags & O_APPEND) f |= FS_O_APPEND;
    if (flags & O_CREAT)  f |= FS_O_CREAT;
    if (flags & O_TRUNC)  f |= FS_O_TRUNC;

    ret = fs_open(path, f, 0666);
    if (ret < 0) {
        import_errno();
        return -1;
    }

    /* Reserve 0/1/2 for standard descriptors, matching SF2000 Multicore. */
    return ret + 5;
}

ssize_t read(int fd, void *buf, size_t count)
{
    int ret;
    if (fd <= 2)
        return 0;
    ret = fs_read(fd - 5, buf, (unsigned)count);
    if (ret < 0) import_errno();
    return ret;
}

ssize_t write(int fd, const void *buf, size_t count)
{
    int ret;

    /* First bring-up has no external console sink. Treat stdout/stderr as
     * successfully consumed so newlib logging cannot block emulation. */
    if (fd == 1 || fd == 2)
        return (ssize_t)count;
    if (fd == 0)
        return -1;

    ret = fs_write(fd - 5, buf, (unsigned)count);
    if (ret < 0) import_errno();
    return ret;
}

off_t lseek(int fd, off_t offset, int whence)
{
    long long ret;
    if (fd <= 2)
        return (off_t)-1;
    ret = fs_lseek(fd - 5, (long long)offset, whence);
    if (ret < 0) {
        import_errno();
        return (off_t)-1;
    }
    return (off_t)ret;
}

int close(int fd)
{
    int ret;
    if (fd <= 2)
        return -1;
    ret = fs_close(fd - 5);
    if (ret < 0) import_errno();
    return ret;
}

static int translate_stat(int ret, const xgo_fs_stat_t *x, struct stat *st)
{
    if (ret < 0) {
        import_errno();
        return -1;
    }

    /* Avoid depending on libc memset before the C runtime is fully proven. */
    {
        unsigned char *p = (unsigned char *)st;
        size_t i;
        for (i = 0; i < sizeof(*st); ++i) p[i] = 0;
    }

    /* ALi values observed by upstream: 0x81b6 file, 0x41ff directory. */
    if ((x->t.type & 0xF000u) == 0x8000u)
        st->st_mode = S_IFREG | S_IRUSR | S_IWUSR;
    else if ((x->t.type & 0xF000u) == 0x4000u)
        st->st_mode = S_IFDIR | S_IRUSR | S_IWUSR;
    st->st_size = (off_t)x->s.size;
    return 0;
}

int stat(const char *path, struct stat *st)
{
    xgo_fs_stat_t x = {{0}};
    return translate_stat(fs_stat(path, &x), &x, st);
}

int fstat(int fd, struct stat *st)
{
    xgo_fs_stat_t x = {{0}};
    if (fd <= 2) {
        unsigned char *p = (unsigned char *)st;
        size_t i;
        for (i = 0; i < sizeof(*st); ++i) p[i] = 0;
        st->st_mode = S_IFCHR;
        return 0;
    }
    return translate_stat(fs_fstat(fd - 5, &x), &x, st);
}

int access(const char *path, int mode)
{
    struct stat st;
    (void)mode;
    return stat(path, &st);
}

int mkdir(const char *path, mode_t mode)
{
    int ret = fs_mkdir(path, (int)mode);
    if (ret < 0) import_errno();
    return ret;
}

int isatty(int fd)
{
    return fd >= 0 && fd <= 2;
}

pid_t getpid(void)
{
    return 1;
}

int kill(pid_t pid, int sig)
{
    (void)pid;
    (void)sig;
    errno = EINVAL;
    return -1;
}

int gettimeofday(struct timeval *tv, void *tz)
{
    uint32_t ms;
    (void)tz;
    if (!tv) {
        errno = EINVAL;
        return -1;
    }
    ms = os_get_tick_count();
    tv->tv_sec = (time_t)(ms / 1000u);
    tv->tv_usec = (suseconds_t)((ms % 1000u) * 1000u);
    return 0;
}

clock_t clock(void)
{
    uint32_t ms = os_get_tick_count();
    return (clock_t)(((uint64_t)ms * (uint64_t)CLOCKS_PER_SEC) / 1000u);
}

/* Newlib ports differ on whether they reference underscored syscall names
 * directly. Provide aliases so either convention resolves to the same bridge. */
ssize_t _read(int fd, void *buf, size_t n) { return read(fd, buf, n); }
ssize_t _write(int fd, const void *buf, size_t n) { return write(fd, buf, n); }
off_t _lseek(int fd, off_t off, int whence) { return lseek(fd, off, whence); }
int _close(int fd) { return close(fd); }
int _fstat(int fd, struct stat *st) { return fstat(fd, st); }
int _isatty(int fd) { return isatty(fd); }
pid_t _getpid(void) { return getpid(); }
int _kill(pid_t pid, int sig) { return kill(pid, sig); }
