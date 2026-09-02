/* Minimal newlib/POSIX glue for XGO external libretro cores. */
#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stddef.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <sys/types.h>
#include <time.h>
#include <stdarg.h>
#include <string.h>
#include <dirent.h>

#define FS_O_RDONLY 0x0000
#define FS_O_WRONLY 0x0001
#define FS_O_RDWR   0x0002
#define FS_O_APPEND 0x0008
#define FS_O_CREAT  0x0100
#define FS_O_TRUNC  0x0200

extern int fs_open(const char *, int, int);
extern int fs_close(int);
extern int64_t fs_lseek(int, int64_t, int);
extern ssize_t fs_read(int, void *, size_t);
extern ssize_t fs_write(int, const void *, size_t);
extern int fs_stat(const char *, void *);
extern int fs_fstat(int, void *);
extern int fs_access(const char *, int);
extern int fs_mkdir(const char *, int);
extern int fs_opendir(const char *);
extern int fs_closedir(int);
extern int fs_readdir(int, void *);
extern uint32_t os_get_tick_count(void);
extern int g_errno;

static int translate_open_flags(int flags)
{
    int out = 0;
    switch (flags & O_ACCMODE) {
    case O_WRONLY: out |= FS_O_WRONLY; break;
    case O_RDWR:   out |= FS_O_RDWR; break;
    default:       out |= FS_O_RDONLY; break;
    }
    if (flags & O_APPEND) out |= FS_O_APPEND;
    if (flags & O_CREAT)  out |= FS_O_CREAT;
    if (flags & O_TRUNC)  out |= FS_O_TRUNC;
    return out;
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
    if (ret < 0) { errno = g_errno; return -1; }
    return ret + 5;
}

int close(int fd)
{
    int ret;
    if (fd <= 2) return -1;
    ret = fs_close(fd - 5);
    if (ret < 0) { errno = g_errno; return -1; }
    return ret;
}

ssize_t read(int fd, void *buf, size_t count)
{
    ssize_t ret;
    if (fd <= 2) return 0;
    ret = fs_read(fd - 5, buf, count);
    if (ret < 0) { errno = g_errno; return -1; }
    return ret;
}

ssize_t write(int fd, const void *buf, size_t count)
{
    ssize_t ret;
    if (fd == 1 || fd == 2) return (ssize_t)count;
    if (fd == 0) return -1;
    ret = fs_write(fd - 5, buf, count);
    if (ret < 0) { errno = g_errno; return -1; }
    return ret;
}

off_t lseek(int fd, off_t offset, int whence)
{
    int64_t ret;
    if (fd <= 2) return (off_t)-1;
    ret = fs_lseek(fd - 5, (int64_t)offset, whence);
    if (ret < 0) { errno = g_errno; return (off_t)-1; }
    return (off_t)ret;
}

typedef struct {
    union {
        struct { uint8_t pad[0x18]; uint32_t type; } t;
        struct { uint8_t pad[0x38]; uint32_t size; } s;
        uint8_t raw[160];
    } u;
} xgo_fs_stat_t;

static int stat_common(int ret, const xgo_fs_stat_t *in, struct stat *out)
{
    if (ret != 0) return -1;
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
    if (ret < 0) { errno = g_errno; return -1; }
    return ret;
}

int mkdir(const char *path, mode_t mode)
{
    int ret = fs_mkdir(path, (int)mode);
    if (ret < 0) { errno = g_errno; return -1; }
    return ret;
}

typedef struct {
    union {
        struct { uint8_t pad[0x10]; uint32_t type; } t;
        struct { uint8_t pad[0x22]; char name[0x225]; } n;
        uint8_t raw[0x428];
    } u;
} xgo_fs_dirent_t;

DIR *opendir(const char *path)
{
    int fd = fs_opendir(path);
    if (fd < 0) { errno = g_errno; return (DIR *)0; }
    return (DIR *)(uintptr_t)(fd + 1);
}

int closedir(DIR *dir)
{
    int fd = (int)(uintptr_t)dir - 1;
    int ret;
    if (fd < 0) return -1;
    ret = fs_closedir(fd);
    if (ret < 0) { errno = g_errno; return -1; }
    return ret;
}

struct dirent *readdir(DIR *dir)
{
    static struct dirent out;
    xgo_fs_dirent_t tmp;
    int fd = (int)(uintptr_t)dir - 1;
    unsigned type;
    if (fd < 0) return (struct dirent *)0;
    memset(&tmp, 0, sizeof(tmp));
    if (fs_readdir(fd, &tmp) < 0) return (struct dirent *)0;
    type = tmp.u.t.type;
    if ((type & 0xf000u) == 0x8000u) out.d_type = DT_REG;
    else if ((type & 0xf000u) == 0x4000u) out.d_type = DT_DIR;
    else out.d_type = DT_UNKNOWN;
    strncpy(out.d_name, tmp.u.n.name, sizeof(out.d_name) - 1u);
    out.d_name[sizeof(out.d_name) - 1u] = 0;
    return &out;
}

int isatty(int fd) { return fd >= 0 && fd <= 2; }
pid_t getpid(void) { return 1; }
int kill(pid_t pid, int sig)
{
    (void)pid; (void)sig;
    errno = EINVAL;
    return -1;
}

int gettimeofday(struct timeval *tv, void *tz)
{
    uint32_t ms;
    (void)tz;
    if (!tv) return -1;
    ms = os_get_tick_count();
    tv->tv_sec = ms / 1000u;
    tv->tv_usec = (ms % 1000u) * 1000u;
    return 0;
}

clock_t clock(void)
{
    return (clock_t)((uint64_t)os_get_tick_count() * CLOCKS_PER_SEC / 1000u);
}

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
