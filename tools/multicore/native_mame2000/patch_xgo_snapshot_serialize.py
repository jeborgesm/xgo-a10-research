#!/usr/bin/env python3
from pathlib import Path
p=Path("/tmp/mame2000/src/libretro/libretro.c")
s=p.read_text()
old='''size_t retro_serialize_size(void)
{
   return 0;
}

bool retro_serialize(void *data_, size_t size)
{
   (void)data_;
   (void)size;
   return false;
}

bool retro_unserialize(const void *data_, size_t size)
{
   (void)data_;
   (void)size;
   return false;
}
'''
new='''extern size_t xgo_snapshot_serialize_size(void);
extern bool xgo_snapshot_serialize(void *data_, size_t size);
extern bool xgo_snapshot_unserialize(const void *data_, size_t size);

size_t retro_serialize_size(void)
{
   return xgo_snapshot_serialize_size();
}

bool retro_serialize(void *data_, size_t size)
{
   return xgo_snapshot_serialize(data_, size);
}

bool retro_unserialize(const void *data_, size_t size)
{
   return xgo_snapshot_unserialize(data_, size);
}
'''
if old not in s:
    raise SystemExit("MAME2000 serializer stub block not found")
p.write_text(s.replace(old,new,1))
print("patched MAME2000 libretro serializer -> XGO fixed-address snapshot")
