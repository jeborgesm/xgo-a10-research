# XGO live heap break and Multicore memory guard

Status: **confirmed from allocator executable code**.

## Headline

The XGO's active `sbrk` implementation and all of its key state variables are now mapped:

```text
sbrk                    = 0x80291944
current heap break      = 0x80c337b0
heap ceiling / RAMSIZE  = 0x80c2ce6c
firmware errno          = 0x80c2d640
```

This allows a future injected loader to test whether the live stock heap is still below Multicore's proposed `0x87000000` core-load window instead of relying on a static assumption.

## Reconstructed sbrk logic

With XGO startup `$gp = 0x80c34774`, function `0x80291944` accesses:

```text
gp - 0x0fc4 = 0x80c337b0   current break
gp - 0x7908 = 0x80c2ce6c   heap ceiling
gp - 0x7134 = 0x80c2d640   firmware errno
```

The function executes the equivalent of:

```c
void *xgo_sbrk(unsigned increment)
{
    void *old_break = *(void **)0x80c337b0;
    void *new_break = old_break + increment;

    if ((unsigned)new_break < *(unsigned *)0x80c2ce6c) {
        *(void **)0x80c337b0 = new_break;
        return old_break;
    }

    *(unsigned *)0x80c2d640 = 12;  // ENOMEM
    return (void *)-1;
}
```

The comparison is unsigned and requires the new break to remain strictly below the ceiling.

## Initialization values

Allocator initialization at `0x80291974` writes:

```text
RAMSIZE / heap ceiling = 0x87cdae00
```

Earlier initialization establishes the initial current break as:

```text
0x813b4bb4
```

Therefore the stock allocator begins with a very large address-space interval available below its ceiling.

## Multicore significance

Classic SF2000 Multicore reserves the upper memory window by changing the stock heap ceiling to:

```text
0x87000000
```

and loading an external core at that address.

The XGO port can now make that operation conditional:

```c
if (*(unsigned *)0x80c337b0 >= 0x87000000)
    refuse_external_core_load();
else
    *(unsigned *)0x80c2ce6c = 0x87000000;
```

This converts a previously open assumption into a runtime-enforceable safety invariant.

## Missing Multicore symbol resolved: g_errno

Upstream Multicore's POSIX wrapper layer imports stock `g_errno` so that negative `fs_*` results can be translated into newlib `errno`.

The XGO `sbrk` failure path independently proves:

```text
g_errno = 0x80c2d640
```

because it writes literal error `12` there immediately before returning `-1` on allocation failure.

This is stronger than deriving the address by a data-section delta.

## Porting implication

The first external-core loader no longer needs to assume that the XGO heap stayed below `0x87000000`. It can verify that condition using the firmware's own live allocation state and abort safely if the reservation is unavailable.
