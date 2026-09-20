# VFS path-operation closure: unlink and directory wrappers separated

This pass resolves several wrappers around 0x807D40A8 and prevents us from using the wrong primitive for transaction hardening.

## 0x807D40A8

The Test97 materializer evidence remains decisive: this one-argument path operation is called on temporary artwork filenames before generation and during cleanup. Treat it as unlink/remove-file-like.

Its lower path:
0x807D40A8 -> 0x802ABC30 -> resolver/copy of 0x400-byte path object -> VFS operation 0x802AF338.

Do not treat it as sync/flush.

## Directory family

0x807D40C4 calls 0x802ABE28, then allocates a 0x404-byte frontend directory object. This is the stock directory-open wrapper used by Refresh scanning.

0x807D4124 operates on that allocated directory object and fills the caller's directory-entry buffer; this is the directory-next/read wrapper.

0x807D41F4 calls 0x802AC4F0 on the underlying object and frees the frontend allocation; this is the directory-close wrapper.

This cleanly separates directory lifecycle from the one-path unlink-like operation.

## Lower VFS shape

0x802ABE28:
- copies/resolves incoming path into a 0x400-byte temporary object;
- calls 0x802AEE00 with a mode/control argument of -1;
- frees the temporary path object;
- returns lower-layer result.

0x802AEE00 resolves a mount/object and invokes another backend operation before releasing the resolver object. This confirms a generic mounted-VFS architecture, but exact POSIX names should not be assigned from shape alone.

## Transaction implications

We have NOT yet identified a safe atomic rename primitive.

The firmware contains diagnostic text:
"[FS]link %s -> %s failed! err code = %d!"

That proves a link-style operation exists somewhere in the firmware, but the exact callable ABI and whether it is hard-link, rename-like, or another VFS link operation are not yet closed.

Therefore:
- do not implement journal/rename hardening yet;
- do not repurpose 0x807D40A8 for commit/rename;
- keep Test103 limited to materializer -> native scanner.

## Safety conclusion

The native scanner repair does not require any newly discovered filesystem primitive. Transaction hardening remains a separate later phase and is gated on exact link/rename semantics.
