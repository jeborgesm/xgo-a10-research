# FBA2012 CPS1 SF2000 lineage check — first-frame stall is not a later regression

Status: **STATIC COMPARISON CLOSED**

The dedicated CPS1 fork received its SF2000 support in:

```text
fc405965c0a5fc21f5df57b87464cfb789d2cce2
Add SF2000 platform
2023-10-28
```

Current multicore catalogs pin:

```text
5714c8dc311f4dda6e54533bc8dd901a29700635
```

A direct Git comparison shows 20 commits between those points, but the changed files are limited to:

- `.gitmodules`;
- libretro-common submodule/plumbing;
- removed vendored libretro-common headers;
- core-option translations.

There are **no changes to CPS1 execution code, m68000 backend code, or the libretro frame loop** between the original SF2000 port and the current pinned head.

Therefore the hardware Test 08/09 first-frame stall is not explained by a later upstream regression after SF2000 support was added.

## CPU backend observation

The SF2000 build currently selects:

```text
EMU_C68K = 0
-> -DEMU_M68K
-> SekRun()
-> m68k_execute()
```

The same source tree also contains a C68K backend selectable through:

```text
EMU_C68K=1
```

This is a high-value next diagnostic because:

1. Test 09 has already ruled out libretro input polling.
2. The stall boundary lies inside/under `BurnDrvFrame()`.
3. CPS1 `Cps1Frame()` enters `SekRun()` immediately after frame setup.
4. The current backend ultimately calls `m68k_execute()`.
5. A C68K build changes the 68000 execution engine without changing the XGO frontend, content path, mapper, SNES, or non-CPS1 arcade routing.

If C68K advances past the self-test, the failure is localized to the current M68K backend on HC15xx/XGO. It may also provide the performance improvement that motivated Core #3.
