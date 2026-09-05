# Hardware Test 16 — durable trace localizes A68K hang before CpsRunInit

Physical trace:

```text
F10 before stock run_emulator
L00 retro_load_game enter
L10 before fba_init
D00 DrvInit enter
D10 before CpsInit
D11 after CpsInit
```

No `D20 before CpsRunInit` marker is committed.

## Localization

This proves the Test14/Test15 A68K failure is NOT in:

- SekInitCPUA68K
- M68000_RESET
- CpsRunInit
- CpsMemInit
- CpsRwInit
- DrvReset
- SekReset
- A68KChangePC

None of those functions has been reached yet.

The hang is inside the narrow section of CPS1 `DrvInit()` after `CpsInit()` returns and before `CpsRunInit()` is entered:

```cpp
Cps1LoadRoms(1);

if (AmendProgRomCallback) AmendProgRomCallback();

SetGameConfig();

if (Cps1Qs) {
    KabukiDecodeFunction();
}

CpsRunInit();
```

For normal SFII, the highest-probability blocking operation is the second `Cps1LoadRoms(1)`, i.e. actual ROM loading/decoding into the buffers allocated by CpsInit.

## Important architectural consequence

The A68K CPU engine has not executed at the point of failure. Therefore Test14/15's loading freeze cannot be attributed to A68K instruction execution or reset behavior.

The failure instead correlates with something changed by BUILD_A68K / binary layout / memory behavior before CPU startup.

Next diagnostic: instrument before/after Cps1LoadRoms(1), AmendProgRomCallback, SetGameConfig, KabukiDecodeFunction and then, if needed, individual ROM-load iterations.
