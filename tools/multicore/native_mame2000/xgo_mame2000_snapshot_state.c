/*
 * XGO MAME2000 fixed-address runtime snapshot.
 *
 * MAME2000 0.37b5 has no libretro serialization. XGO gives us a stronger
 * property: this core and its private heap use stable addresses every launch.
 * Serialize the complete mutable core image plus the live private heap.
 */
#include <stddef.h>
#include <stdint.h>
#include <string.h>

typedef int bool;
#define true 1
#define false 0

#define XGO_SNAPSHOT_MAGIC 0x31534d58u /* XMS1 */
#define XGO_SNAPSHOT_VERSION 1u

extern unsigned char _fdata[];
extern unsigned char __image_end[];

extern uintptr_t xgo_mame_heap_floor(void);
extern uintptr_t xgo_mame_heap_ptr(void);
extern uintptr_t xgo_mame_heap_limit(void);
extern int xgo_mame_heap_restore(uintptr_t ptr);
extern size_t xgo_mame_state_raw_capacity(void);

struct xgo_mame_snapshot_header {
    uint32_t magic;
    uint32_t version;
    uint32_t data_size;
    uint32_t heap_floor;
    uint32_t heap_size;
    uint32_t total_size;
};

static size_t snapshot_size_now(void)
{
    uintptr_t floor=xgo_mame_heap_floor();
    uintptr_t ptr=xgo_mame_heap_ptr();
    size_t data_size=(size_t)(__image_end-_fdata);
    size_t heap_size;

    if(!floor || ptr<floor || ptr>xgo_mame_heap_limit()) return 0;
    heap_size=(size_t)(ptr-floor);
    if(data_size > 0xffffffffu || heap_size > 0xffffffffu) return 0;
    if(sizeof(struct xgo_mame_snapshot_header)+data_size+heap_size >
       xgo_mame_state_raw_capacity()) return 0;
    return sizeof(struct xgo_mame_snapshot_header)+data_size+heap_size;
}

size_t xgo_snapshot_serialize_size(void)
{
    return snapshot_size_now();
}

bool xgo_snapshot_serialize(void *data,size_t size)
{
    struct xgo_mame_snapshot_header *h=(struct xgo_mame_snapshot_header*)data;
    uintptr_t floor=xgo_mame_heap_floor();
    uintptr_t ptr=xgo_mame_heap_ptr();
    size_t data_size=(size_t)(__image_end-_fdata);
    size_t heap_size;
    unsigned char *p;

    if(!data || !floor || ptr<floor || ptr>xgo_mame_heap_limit()) return false;
    heap_size=(size_t)(ptr-floor);
    if(size != sizeof(*h)+data_size+heap_size) return false;
    if(size > xgo_mame_state_raw_capacity()) return false;

    h->magic=XGO_SNAPSHOT_MAGIC;
    h->version=XGO_SNAPSHOT_VERSION;
    h->data_size=(uint32_t)data_size;
    h->heap_floor=(uint32_t)floor;
    h->heap_size=(uint32_t)heap_size;
    h->total_size=(uint32_t)size;

    p=(unsigned char*)(h+1);
    memcpy(p,_fdata,data_size);
    p+=data_size;
    memcpy(p,(const void*)floor,heap_size);
    return true;
}

bool xgo_snapshot_unserialize(const void *data,size_t size)
{
    const struct xgo_mame_snapshot_header *h=(const struct xgo_mame_snapshot_header*)data;
    uintptr_t floor=xgo_mame_heap_floor();
    size_t expected_data=(size_t)(__image_end-_fdata);
    const unsigned char *p;

    if(!data || size<sizeof(*h)) return false;
    if(h->magic!=XGO_SNAPSHOT_MAGIC || h->version!=XGO_SNAPSHOT_VERSION) return false;
    if(h->data_size!=expected_data || h->heap_floor!=floor) return false;
    if(h->total_size!=size) return false;
    if(sizeof(*h)+(size_t)h->data_size+(size_t)h->heap_size!=size) return false;
    if((uintptr_t)h->heap_floor+(uintptr_t)h->heap_size>xgo_mame_heap_limit()) return false;

    p=(const unsigned char*)(h+1);

    /* Heap first. The state scratch buffer lives above the reserved heap limit. */
    memcpy((void*)floor,p+h->data_size,h->heap_size);

    /* Restore all mutable core globals, libc state, libco handles, etc. */
    memcpy(_fdata,p,h->data_size);

    /* Be explicit even though the saved data image also contains heap_ptr. */
    if(!xgo_mame_heap_restore(floor+h->heap_size)) return false;
    return true;
}
