/*
 * Minimal libretro-common compatibility slice for XGO FCEUmm bring-up.
 *
 * Purposefully implements only the symbols actually referenced by the pinned
 * HC15xx FCEUmm archive. The file-stream subset is read-only because static
 * disassembly of every FCEUmm filestream_open() call shows mode == 1
 * (RETRO_VFS_FILE_ACCESS_READ) and hints == 0.
 *
 * The final link resolves stdio/allocator/string primitives to stock XGO
 * firmware where mapped, with Codescape runtime libraries filling ordinary
 * compiler/libm gaps.
 */

typedef unsigned char uint8_t;
typedef unsigned int uint32_t;
typedef unsigned long size_t;
typedef signed long long int64_t;
typedef unsigned long long uint64_t;
typedef int bool;

#define NULL ((void *)0)
#define SEEK_SET 0
#define SEEK_CUR 1
#define SEEK_END 2
#define EOF_VALUE (-1)
#define RETRO_VFS_FILE_ACCESS_READ 1u

/* Opaque stock/newlib FILE type. */
typedef struct xgo_FILE FILE;

extern void *malloc(size_t);
extern void free(void *);
extern void *memcpy(void *, const void *, size_t);
extern int strcmp(const char *, const char *);
extern size_t strlen(const char *);

/* XGO stock stdio symbols supplied by xgo_stockfw_symbols.ld. */
extern FILE *fopen(const char *, const char *);
extern size_t fw_fread(void *, size_t, size_t, FILE *);
extern int fseeko(FILE *, long, int);
extern long ftello(FILE *);
extern int fclose(FILE *);

/* ---------------------------------------------------------------------- */
/* File stream: exact FCEUmm-required read-only subset.                    */

struct RFILE {
    FILE *fp;
};
typedef struct RFILE RFILE;

void filestream_vfs_init(const void *vfs_info)
{
    (void)vfs_info;
    /* XGO deliberately bypasses libretro-common's POSIX/default VFS. */
}

RFILE *filestream_open(const char *path, unsigned mode, unsigned hints)
{
    RFILE *stream;
    FILE *fp;

    (void)hints;
    if (!path || mode != RETRO_VFS_FILE_ACCESS_READ)
        return NULL;

    fp = fopen(path, "rb");
    if (!fp)
        return NULL;

    stream = (RFILE *)malloc(sizeof(*stream));
    if (!stream) {
        fclose(fp);
        return NULL;
    }

    stream->fp = fp;
    return stream;
}

int64_t filestream_read(RFILE *stream, void *data, int64_t len)
{
    size_t got;
    if (!stream || !stream->fp || !data || len < 0)
        return -1;
    if ((uint64_t)len > 0xffffffffu)
        return -1;

    got = fw_fread(data, 1, (size_t)len, stream->fp);
    return (int64_t)got;
}

int64_t filestream_seek(RFILE *stream, int64_t offset, int seek_position)
{
    /* XGO's stock fseeko uses the same 32-bit off_t ABI as this firmware. */
    long narrow;
    if (!stream || !stream->fp)
        return -1;
    narrow = (long)offset;
    if ((int64_t)narrow != offset)
        return -1;
    if (fseeko(stream->fp, narrow, seek_position) != 0)
        return -1;
    return (int64_t)ftello(stream->fp);
}

int64_t filestream_tell(RFILE *stream)
{
    if (!stream || !stream->fp)
        return -1;
    return (int64_t)ftello(stream->fp);
}

int filestream_close(RFILE *stream)
{
    int rc;
    if (!stream)
        return -1;
    rc = stream->fp ? fclose(stream->fp) : -1;
    free(stream);
    return rc;
}

bool path_is_valid(const char *path)
{
    FILE *fp;
    if (!path || !*path)
        return 0;
    fp = fopen(path, "rb");
    if (!fp)
        return 0;
    fclose(fp);
    return 1;
}

/* ---------------------------------------------------------------------- */
/* Memory stream: minimal ABI-compatible implementation used by states.    */

static uint8_t *g_mem_buffer;
static uint64_t g_mem_size;
static uint64_t g_mem_last_size;

struct memstream {
    uint64_t size;
    uint64_t ptr;
    uint64_t max_ptr;
    uint8_t *buf;
    unsigned writing;
};
typedef struct memstream memstream_t;

void memstream_set_buffer(uint8_t *buffer, uint64_t size)
{
    g_mem_buffer = buffer;
    g_mem_size = size;
}

uint64_t memstream_get_last_size(void)
{
    return g_mem_last_size;
}

memstream_t *memstream_open(unsigned writing)
{
    memstream_t *s;
    if (!g_mem_buffer || !g_mem_size)
        return NULL;

    s = (memstream_t *)malloc(sizeof(*s));
    if (!s)
        return NULL;

    s->size = g_mem_size;
    s->ptr = 0;
    s->max_ptr = 0;
    s->buf = g_mem_buffer;
    s->writing = writing;
    g_mem_buffer = NULL;
    g_mem_size = 0;
    return s;
}

void memstream_close(memstream_t *s)
{
    if (!s)
        return;
    g_mem_last_size = s->writing ? s->max_ptr : s->size;
    free(s);
}

uint64_t memstream_read(memstream_t *s, void *data, uint64_t bytes)
{
    uint64_t avail;
    if (!s || s->ptr > s->size)
        return 0;
    avail = s->size - s->ptr;
    if (bytes > avail)
        bytes = avail;
    memcpy(data, s->buf + (size_t)s->ptr, (size_t)bytes);
    s->ptr += bytes;
    if (s->ptr > s->max_ptr)
        s->max_ptr = s->ptr;
    return bytes;
}

uint64_t memstream_write(memstream_t *s, const void *data, uint64_t bytes)
{
    uint64_t avail;
    if (!s || s->ptr > s->size)
        return 0;
    avail = s->size - s->ptr;
    if (bytes > avail)
        bytes = avail;
    memcpy(s->buf + (size_t)s->ptr, data, (size_t)bytes);
    s->ptr += bytes;
    if (s->ptr > s->max_ptr)
        s->max_ptr = s->ptr;
    return bytes;
}

int64_t memstream_seek(memstream_t *s, int64_t offset, int whence)
{
    int64_t base;
    int64_t next;
    if (!s)
        return -1;

    if (whence == SEEK_SET)
        base = 0;
    else if (whence == SEEK_CUR)
        base = (int64_t)s->ptr;
    else if (whence == SEEK_END)
        base = (int64_t)(s->writing ? s->max_ptr : s->size);
    else
        return -1;

    next = base + offset;
    if (next < 0 || (uint64_t)next > s->size)
        return -1;
    s->ptr = (uint64_t)next;
    return 0;
}

uint64_t memstream_pos(memstream_t *s)
{
    return s ? s->ptr : 0;
}

int memstream_getc(memstream_t *s)
{
    int value;
    if (!s || s->ptr >= s->size)
        return EOF_VALUE;
    value = s->buf[(size_t)s->ptr++];
    if (s->ptr > s->max_ptr)
        s->max_ptr = s->ptr;
    return value;
}

void memstream_putc(memstream_t *s, int c)
{
    if (!s || s->ptr >= s->size)
        return;
    s->buf[(size_t)s->ptr++] = (uint8_t)c;
    if (s->ptr > s->max_ptr)
        s->max_ptr = s->ptr;
}

/* ---------------------------------------------------------------------- */
/* Path/string helpers required by the pinned FCEUmm archive.              */

size_t strlcpy_retro__(char *dst, const char *src, size_t size)
{
    size_t src_len = 0;
    size_t i;
    while (src[src_len])
        ++src_len;

    if (size) {
        size_t copy = src_len < (size - 1) ? src_len : (size - 1);
        for (i = 0; i < copy; ++i)
            dst[i] = src[i];
        dst[copy] = '\0';
    }
    return src_len;
}

size_t fill_pathname_join(char *out, const char *dir, const char *path,
                          size_t size)
{
    size_t dlen;
    size_t used;
    size_t i;
    int need_slash;

    if (!out || !size)
        return 0;
    if (!dir)
        dir = "";
    if (!path)
        path = "";

    dlen = strlen(dir);
    need_slash = dlen && dir[dlen - 1] != '/' && path[0] != '/';
    used = strlcpy_retro__(out, dir, size);
    if (used >= size)
        used = size - 1;

    if (need_slash && used + 1 < size) {
        out[used++] = '/';
        out[used] = '\0';
    }

    if (path[0] == '/' && used && out[used - 1] == '/')
        ++path;

    for (i = 0; path[i] && used + 1 < size; ++i)
        out[used++] = path[i];
    out[used] = '\0';

    return dlen + (need_slash ? 1u : 0u) + strlen(path);
}

static int xgo_is_space(unsigned char c)
{
    return c == ' ' || c == '\t' || c == '\n' || c == '\r' || c == '\v' || c == '\f';
}

char *string_trim_whitespace(char *s)
{
    char *start;
    char *end;
    char *dst;

    if (!s)
        return NULL;

    start = s;
    while (*start && xgo_is_space((unsigned char)*start))
        ++start;

    if (start != s) {
        dst = s;
        while ((*dst++ = *start++) != '\0')
            ;
    }

    end = s + strlen(s);
    while (end > s && xgo_is_space((unsigned char)end[-1]))
        --end;
    *end = '\0';
    return s;
}
