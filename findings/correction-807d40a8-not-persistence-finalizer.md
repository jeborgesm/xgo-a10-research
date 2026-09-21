# CORRECTION: 0x807D40A8 is path cleanup/unlink-like, NOT a proven persistence finalizer

This supersedes the interpretation in `custom-catalog-missing-native-persistence-finalizer.md` and the narrower follow-up that treated 0x807D40A8 as a post-write VFS finalizer.

## Decisive evidence from Test97 materializer

Test97 MD/refresh.xgc deliberately loads 0x807D40A8 and calls it with literal path strings:

- 0x87001011 = `/mnt/sda1/MD/art/.xgo.jpg`
- 0x8700102C = `/mnt/sda1/MD/art/.xgo.rgb565`

At helper offsets 0x5CC and 0x5DC it calls 0x807D40A8 on those two paths before temporary artwork generation. At 0xC90 and 0xCA0 it calls the same primitive on the same paths during cleanup.

This usage is strongly consistent with unlink/remove of stale temporary files, not fsync/commit.

The lower 0x802ABC30 -> 0x802AF338 path is therefore best treated as pathname-based VFS deletion/unlink-like behavior unless later symbol recovery proves a more exact name.

## Consequence

The call at native scanner 0x807DB540, after closing the third catalog output, CANNOT currently be cited as evidence of a durability flush. The earlier persistence-finalizer claim was overinterpreted and is withdrawn.

Do not claim that custom catalog.xgc corrupts the card because it omitted 0x807D40A8.

The catalog-corruption risk remains real for independent reasons:
- both custom and native catalog paths rewrite live triplet files in-place with `wb`;
- there is no established atomic three-file transaction;
- Test97 leaves the native frontend workspace stale because the native scanner was bypassed;
- immediate MD entry hard-lock forces a power cycle after live catalog writes;
- Windows subsequently found filesystem corruption in wmiui.bvs.

But the exact durability primitive, if any, remains OPEN.

## Native scanner architecture remains preferred

Replacing custom catalog.xgc with 0x807DAE4C(list=2) is still strongly supported because it restores:
- native catalog workspace maintenance;
- native triplet validation/merge;
- native cache lifecycle;
- native 1/0/-1 semantics;
- the same materializer -> native scanner architecture hardware-proven in Test75.

It should NOT be justified by a supposed 0x807D40A8 flush.

## New investigation target

Search native filesystem/VFS code for actual sync/flush semantics by:
1. identifying FILE close's lower writeback behavior;
2. mapping VFS ops-table slots around 0x802AFxxx;
3. tracing SD block/cache writeback calls;
4. determining whether fclose itself provides sufficient durability or merely closes the stream;
5. locating any explicit filesystem sync/unmount/cache-flush primitive.

No hardware package yet.
