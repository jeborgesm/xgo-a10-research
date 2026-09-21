# Persistence primitive audit — correction and narrowed conclusion

This note corrects an overstatement in commit b1fa0462.

## 0x807D40A8 exact name remains unresolved

Earlier notes historically called 0x807D40A8 remove(path). The previous commit then promoted it to a filesystem finalizer. Deeper VFS disassembly shows the architectural-finalizer interpretation is plausible, but the exact public semantic name is NOT yet proven and must remain OPEN.

What is now proven:

```
807D40A8 -> 802ABC30
```

0x802ABC30:
- preserves a0;
- allocates a 1024-byte temporary object;
- copies 1024 bytes from the a0 object into it;
- invokes lower VFS routine 0x802AF338;
- frees the temporary object.

0x802AF338:
- resolves/acquires a filesystem object;
- locks filesystem/VFS state;
- invokes a filesystem operation through an ops-table function pointer;
- unlocks/releases the object;
- returns the lower operation status.

The lower operation receives a filesystem object, not an obvious parent/name pair. This is compatible with a sync/finalize-style vnode operation and is less naturally shaped like a conventional unlink implementation, but symbol-free static analysis is not sufficient yet to name it.

## Call-site evidence

The stock native catalog scanner invokes 0x807D40A8 immediately after all three successful catalog writes/closes and before count-cache invalidation / success return.

Test97 materializer also invokes 0x807D40A8 around its temporary artwork/output paths.

Custom catalog.xgc contains no call to 0x807D40A8.

Therefore the safe claim is:

**The native catalog lifecycle contains a post-write VFS operation that the custom catalog.xgc omitted.**

Do not call it remove, fsync, sync, or commit in canonical documentation until the lower op is identified.

## Native scanner substitution remains justified independently

Even if 0x807D40A8's exact semantic label changes, replacing custom catalog.xgc with native scanner remains the correct architecture because it restores the complete native sequence as a unit:
- native triplet load/validation
- native workspace maintenance
- wrapper scan/merge
- stock write path
- post-write VFS operation
- stock cache invalidation
- stock return semantics

No custom reimplementation needs to guess the VFS primitive.

## Test103 safety implication

This uncertainty is another reason NOT to patch custom catalog.xgc by simply inserting a call to 0x807D40A8. Its argument contract at the native scanner call site is subtle and not yet closed.

Call the native scanner instead.

## Next research target

Identify 0x802AF338's VFS ops-table slot by comparing adjacent lower VFS routines and their call shapes. Also recover whether there is a separate rename/unlink primitive for future transaction hardening.
