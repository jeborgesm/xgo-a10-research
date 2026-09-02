/*
 * Bottom-level newlib hooks for the first XGO external-core link.
 *
 * Real FCEUmm content I/O uses xgo_fceumm_support.c -> stock XGO stdio.
 * These descriptor syscalls exist only because Codescape newlib's reentrant
 * wrappers are linked into ordinary libc support. Do not map them blindly to
 * XGO fs_*: the descriptor ABI has not been proven equivalent.
 */

typedef unsigned long size_t;
typedef long ssize_t;
typedef long off_t;

extern int dly_tsk(unsigned);

int close(int fd)
{
    (void)fd;
    return -1;
}

off_t lseek(int fd, off_t offset, int whence)
{
    (void)fd;
    (void)offset;
    (void)whence;
    return (off_t)-1;
}

ssize_t read(int fd, void *buf, size_t count)
{
    (void)fd;
    (void)buf;
    (void)count;
    return -1;
}

ssize_t write(int fd, const void *buf, size_t count)
{
    (void)fd;
    (void)buf;
    (void)count;
    return -1;
}

/*
 * FCEUmm's only exit(1) caller is FCEU_gmalloc() after calloc() failure.
 * Returning is impossible because the core was compiled with exit() marked
 * noreturn. Until the loader-level abort trampoline exists, fail closed here
 * while allowing stock RTOS tasks/interrupts to continue running.
 */
__attribute__((noreturn)) void _exit(int status)
{
    (void)status;
    for (;;)
        dly_tsk(1000);
}
