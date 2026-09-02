/*
 * Minimal newlib/POSIX glue for XGO external libretro cores.
 *
 * This is intentionally derived from the proven SF2000 Multicore strategy but
 * binds only to XGO stock fs_*/timer symbols already mapped in
 * xgo_stockfw_symbols.ld. Heap ownership is supplied separately by either
 * xgo_full_arena_sbrk.c or xgo_preloaded_rom_sbrk.c.
 *
 * Build only with the external-core newlib toolchain.
 */

#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stddef.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <sys/types.h>
#include <time.h>
#include <unistd.h>
#include <stdarg.h>
#include <string.h>

#define FS_O_RDONLY 0x0000
#define FS_O_WRONLY 0x0001
#define FS_O_RDWR   0x0002
#define FS_O_APPEND 0x0008
#define FS_O_CREAT  0x0100
#define FS_O_TRUNC  0x0200

extern int fs_open(const char *path, int oflag, int perms);
extern int fs_close(int fd);
extern int64_t fs_lseek(int fd, int64_t offset, int whence);
extern ssize_t fs_read(int fd, void *buf, size_t nbyte);
extern ssize_t fs_write(int fd, const void *buf, size_t nbyte);
extern int fs_stat(const char *path, void *sbuf);
extern int fs_fstat(int fd, void *sbuf);
extern int fs_access(const char *path, int mode);
extern int fs_mkdir(const char *path, int mode);
extern uint32_t os_get_tick_count(void);
extern int g_errno;

static int translate_open_flags(int flags)
{
    int fs_flags = 0;

    /* O_RDONLY is zero on newlib, so select by O_ACCMODE rather than '&'. */
    switch (flags & O_ACCMODE) {
    case O_WRONLY:
        fs_flags |= FS_O_WRONLY;
        break;
    case O_RDWR:
        fs_flags |= FS_O_RDWR;
        break;
    default:
        fs_flags |= FS_O_RDONLY;
        break;
    }

    if (flags & O_APPEND) fs_flags |= FS_O_APPEND;
    if (flags & O_CREAT)  fs_flags |= FS_O_CREAT;
    if (flags & O_TRUNC)  fs_flags |= FS_O_TRUNC;
    return fs_flags;
}

int open(const char *path, int flags, ...)
{
    int mode = 0666;
    int ret;

    if (flags & O_CREAT) {
        va_list ap;
        va_start(ap, flags);
        mode = va_arg(ap, int);
        va_end(ap);
    }

    ret = fs_open(path, translate_open_flags(flags), mode);
    if (ret < 0) {
        errno = g_errno;
        return -1;
    }

    /* Keep stdin/stdout/stderr at 0..2 and reserve 3..4 for libc internals. */
    return ret + 5;
}

int close(int fd)
{
    int ret;
    if (fd <= 2)
        return -1;
    ret = fs_close(fd - 5);
    if (ret < 0) {
        errno = g_errno;
        return -1;
    }
    return ret;
}

ssize_t read(int fd, void *buf, size_t count)
{
    ssize_t ret;
    if (fd <= 2)
        return 0;
    ret = fs_read(fd - 5, buf, count);
    if (ret < 0) {
        errno = g_errno;
        return -1;
    }
    return ret;
}

ssize_t write(int fd, const void *buf, size_t count)
{
    ssize_t ret;

    /* Research build has no console backend. Treat stdout/stderr as consumed. */
    if (fd == 1 || fd == 2)
        return (ssize_t)count;
    if (fd == 0)
        return -1;

    ret = fs_write(fd - 5, buf, count);
    if (ret < 0) {
        errno = g_errno;
        return -1;
    }
    return ret;
}

off_t lseek(int fd, off_t offset, int whence)
{
    int64_t ret;
    if (fd <= 2)
        return (off_t)-1;
    ret = fs_lseek(fd - 5, (int64_t)offset, whence);
    if (ret < 0) {
        errno = g_errno;
        return (off_t)-1;
    }
    return (off_t)ret;
}

typedef struct {
    union {
        struct {
            uint8_t pad_type[0x18];
            uint32_t type;
        } t;
        struct {
            uint8_t pad_size[0x38];
            uint32_t size;
        } s;
        uint8_t raw[160];
    } u;
} xgo_fs_stat_t;

static int stat_common(int ret, const xgo_fs_stat_t *in, struct stat *out)
{
    if (ret != 0)
        return -1;

    memset(out, 0, sizeof(*out));
    if ((in->u.t.type & 0xf000u) == 0x8000u)
        out->st_mode = S_IFREG | S_IRUSR | S_IWUSR;
    else if ((in->u.t.type & 0xf000u) == 0x4000u)
        out->st_mode = S_IFDIR | S_IRUSR | S_IWUSR;
    else
        out->st_mode = S_IRUSR | S_IWUSR;
    out->st_size = (off_t)in->u.s.size;
    return 0;
}

int stat(const char *path, struct stat *out)
{
    xgo_fs_stat_t tmp;
    memset(&tmp, 0, sizeof(tmp));
    return stat_common(fs_stat(path, &tmp), &tmp, out);
}

int fstat(int fd, struct stat *out)
{
    xgo_fs_stat_t tmp;
    if (fd <= 2) {
        memset(out, 0, sizeof(*out));
        out->st_mode = S_IFCHR;
        return 0;
    }
    memset(&tmp, 0, sizeof(tmp));
    return stat_common(fs_fstat(fd - 5, &tmp), &tmp, out);
}

int access(const char *path, int mode)
{
    int ret = fs_access(path, mode);
    if (ret < 0) {
        errno = g_errno;
        return -1;
    }
    return ret;
}

int mkdir(const char *path, mode_t mode)
{
    int ret = fs_mkdir(path, (int)mode);
    if (ret < 0) {
        errno = g_errno;
        return -1;
    }
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
    if (!tv)
        return -1;
    ms = os_get_tick_count();
    tv->tv_sec = ms / 1000u;
    tv->tv_usec = (ms % 1000u) * 1000u;
    return 0;
}

clock_t clock(void)
{
    return (clock_t)((uint64_t)os_get_tick_count() * CLOCKS_PER_SEC / 1000u);
}

/*
 * Some newlib builds call underscore-prefixed syscall names directly. Keep
 * tiny forwarding wrappers so the runtime does not depend on one exact newlib
 * configuration.
 */
int _open(const char *path, int flags, ...)
{
    int mode = 0666;
    if (flags & O_CREAT) {
        va_list ap;
        va_start(ap, flags);
        mode = va_arg(ap, int);
        va_end(ap);
    }
    return open(path, flags, mode);
}
int _close(int fd) { return close(fd); }
ssize_t _read(int fd, void *buf, size_t n) { return read(fd, buf, n); }
ssize_t _write(int fd, const void *buf, size_t n) { return write(fd, buf, n); }
off_t _lseek(int fd, off_t off, int whence) { return lseek(fd, off, whence); }
int _fstat(int fd, struct stat *st) { return fstat(fd, st); }
int _isatty(int fd) { return isatty(fd); }
pid_t _getpid(void) { return getpid(); }
int _kill(pid_t pid, int sig) { return kill(pid, sig); }
