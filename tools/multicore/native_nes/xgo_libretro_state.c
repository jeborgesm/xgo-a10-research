/*
 * Generic libretro save-state adapter for the stock XGO frontend contract.
 *
 * Preserved XGO firmware behavior:
 *   - gfn_state_save is invoked with a temporary .../save/<game>.kmp path.
 *   - gfn_state_load is invoked with the final .../save/<game>.saN path.
 *   - the core-specific state file prefix is:
 *         uint32_t compressed_state_size;
 *         uint8_t  compressed_state[compressed_state_size];
 *   - the stock frontend owns the remaining thumbnail/bundle construction.
 *
 * The first hardware candidate deliberately keeps the already-proven frontend
 * wiring, which points both state slots at xgo_core_state_io.  The GP veneer
 * enters xgo_state_io_dispatch() below, and the path suffix distinguishes the
 * stock save and load calls without modifying the proven launch lifecycle.
 */

#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#ifndef XGO_STATE_MAX_SERIALIZED
#define XGO_STATE_MAX_SERIALIZED (16u * 1024u * 1024u)
#endif

#ifndef XGO_STATE_MAX_COMPRESSED
#define XGO_STATE_MAX_COMPRESSED (32u * 1024u * 1024u)
#endif

typedef int bool;
#define true 1
#define false 0

extern size_t retro_serialize_size(void);
extern bool retro_serialize(void *data, size_t size);
extern bool retro_unserialize(const void *data, size_t size);

/*
 * GP-safe veneers into the exact helpers used by the stock state path.
 * MIPS32 unsigned long is 32-bit, matching the firmware's length fields.
 */
extern int xgo_stock_state_compress(void *dst, unsigned long *dst_len,
                                    const void *src, unsigned long src_len);
extern int xgo_stock_state_uncompress(void *dst, unsigned long *dst_len,
                                      const void *src, unsigned long src_len);

static int suffix_is(const char *path, const char *suffix)
{
    const char *p;
    const char *s;
    size_t path_len = 0;
    size_t suffix_len = 0;

    if (!path || !suffix)
        return 0;

    for (p = path; *p; ++p)
        ++path_len;
    for (s = suffix; *s; ++s)
        ++suffix_len;

    if (suffix_len > path_len)
        return 0;

    p = path + path_len - suffix_len;
    s = suffix;
    while (*s) {
        if (*p++ != *s++)
            return 0;
    }
    return 1;
}

static int is_stock_slot_path(const char *path)
{
    return suffix_is(path, ".sa0") ||
           suffix_is(path, ".sa1") ||
           suffix_is(path, ".sa2") ||
           suffix_is(path, ".sa3") ||
           suffix_is(path, ".skp");
}

static int xgo_state_save_prefix(const char *path)
{
    FILE *file = NULL;
    void *raw = NULL;
    void *compressed = NULL;
    size_t raw_size;
    size_t compressed_capacity;
    unsigned long compressed_len;
    uint32_t stored_len;
    int ok = 0;

    if (!path || !*path)
        return 0;

    raw_size = retro_serialize_size();
    if (raw_size == 0 || raw_size > XGO_STATE_MAX_SERIALIZED)
        return 0;

    /*
     * Stock NES allocates 2x serialize_size for its compression destination.
     * Preserve that policy for format/behavior parity and reject overflow.
     */
    if (raw_size > (XGO_STATE_MAX_COMPRESSED / 2u))
        return 0;
    compressed_capacity = raw_size * 2u;
    if (compressed_capacity == 0 ||
        compressed_capacity > XGO_STATE_MAX_COMPRESSED)
        return 0;

    raw = malloc(raw_size);
    if (!raw)
        goto out;

    if (!retro_serialize(raw, raw_size))
        goto out;

    compressed = malloc(compressed_capacity);
    if (!compressed)
        goto out;

    compressed_len = (unsigned long)compressed_capacity;
    if (xgo_stock_state_compress(compressed, &compressed_len,
                                 raw, (unsigned long)raw_size) != 0)
        goto out;

    if (compressed_len == 0 || compressed_len > compressed_capacity ||
        compressed_len > 0xffffffffu)
        goto out;

    stored_len = (uint32_t)compressed_len;

    file = fopen(path, "wb");
    if (!file)
        goto out;

    if (fwrite(&stored_len, sizeof(stored_len), 1, file) != 1)
        goto out;
    if (fwrite(compressed, 1, stored_len, file) != stored_len)
        goto out;

    if (fflush(file) != 0)
        goto out;

    ok = 1;

out:
    if (file)
        fclose(file);
    if (compressed)
        free(compressed);
    if (raw)
        free(raw);
    return ok;
}

static int xgo_state_load_prefix(const char *path)
{
    FILE *file = NULL;
    void *raw = NULL;
    void *compressed = NULL;
    size_t serialize_size;
    size_t raw_capacity;
    unsigned long raw_len;
    uint32_t stored_len = 0;
    int ok = 0;

    if (!path || !*path)
        return 0;

    file = fopen(path, "rb");
    if (!file)
        goto out;

    if (fread(&stored_len, sizeof(stored_len), 1, file) != 1)
        goto out;

    if (stored_len == 0 || stored_len > XGO_STATE_MAX_COMPRESSED)
        goto out;

    compressed = malloc((size_t)stored_len);
    if (!compressed)
        goto out;

    if (fread(compressed, 1, stored_len, file) != stored_len)
        goto out;

    /*
     * Deliberately stop after the compressed-state prefix. Final .saN files
     * contain frontend thumbnail metadata after this point; the core loader
     * must ignore it, as the stock NES loader does.
     */
    serialize_size = retro_serialize_size();
    if (serialize_size == 0 || serialize_size > XGO_STATE_MAX_SERIALIZED)
        goto out;

    /* Stock NES loader gives decompression 2x serialize_size headroom. */
    if (serialize_size > (XGO_STATE_MAX_SERIALIZED / 2u))
        goto out;
    raw_capacity = serialize_size * 2u;
    if (raw_capacity == 0 || raw_capacity > XGO_STATE_MAX_SERIALIZED)
        goto out;

    raw = malloc(raw_capacity);
    if (!raw)
        goto out;

    raw_len = (unsigned long)raw_capacity;
    if (xgo_stock_state_uncompress(raw, &raw_len,
                                   compressed, (unsigned long)stored_len) != 0)
        goto out;

    if (raw_len == 0 || raw_len > raw_capacity)
        goto out;

    if (!retro_unserialize(raw, (size_t)raw_len))
        goto out;

    ok = 1;

out:
    if (file)
        fclose(file);
    if (compressed)
        free(compressed);
    if (raw)
        free(raw);
    return ok;
}

int xgo_state_io_dispatch(const char *path)
{
    /*
     * Confirmed stock save scratch path.  This branch must be tested first;
     * preserving the existing single state veneer minimizes the delta from the
     * hardware-proven external FCEUmm build.
     */
    if (suffix_is(path, ".kmp"))
        return xgo_state_save_prefix(path);

    /* Normal final slots, plus the SF2000-family Arcade auto-state extension. */
    if (is_stock_slot_path(path))
        return xgo_state_load_prefix(path);

    return 0;
}
