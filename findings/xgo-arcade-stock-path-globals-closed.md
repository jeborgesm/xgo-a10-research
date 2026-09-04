# XGO arcade content handoff — stock path globals closed

Status: **STATIC FIRMWARE CONTRACT CONFIRMED**

## Why Test 06/07 failed

The on-disk XGO arcade `.zfb` arithmetic was correct, but the external CPS1 frontend incorrectly assumed the stock ROM buffer still contained the untouched wrapper at the corrected arcade runtime hook.

Static firmware tracing now proves that stock XGO has already resolved the real arcade archive path before that point.

## Exact stock path construction

The stock firmware string table contains:

```text
%s/bin/%s
```

at runtime address:

```text
0x809a3554
```

The arcade preprocessing branch around `0x8035ae04` loads that format and calls the stock sprintf-like formatter with:

```text
destination = temporary path buffer
format      = "%s/bin/%s"
arg1        = *(0x809a3674) = 0x810a0eb0
arg2        = *(0x809a3680) = 0x8109fce8
```

Equivalent logic:

```c
sprintf(temp_path,
        "%s/bin/%s",
        (char *)0x810a0eb0,
        (char *)0x8109fce8);
```

## Meaning of 0x810a0eb0

Immediately beforehand, stock code constructs this buffer using:

```text
sprintf(0x810a0eb0, "%s/%s", root, per_list_directory)
```

The per-list directory is indexed from the active frontend list ID.

Therefore:

```text
0x810a0eb0 = current selected system/list directory
```

For arcade lists this is the active ARCADE directory path.

## Meaning of 0x8109fce8

The same address is used independently by the stock save-state path:

```text
sprintf(..., "%s/save/%s.sa%d",
             0x810a0eb0,
             0x8109fce8,
             slot)
```

Therefore `0x8109fce8` is not an incidental parser scratch buffer. It is the frontend's persistent current-game/archive filename component.

For arcade launch, stock feeds this same value into `%s/bin/%s`.

## Consequence

The CPS1 external frontend must not parse `ROM_BUFFER` for the embedded ZIP name.

Instead it should use the exact stock-produced values:

```text
system directory  0x810a0eb0
archive filename  0x8109fce8
```

and construct:

```text
<system directory>/bin/<archive filename>
```

This matches the stock arcade path construction directly and avoids all assumptions about whether the raw `.zfb` remains present in memory after preprocessing.

## Baseline invariants

Keep unchanged:

- mapper v19;
- external NES;
- external Snes9x2005;
- active-list CPS1 discriminator;
- CPS2/IGS/Neo Geo stock fallthrough;
- corrected arcade runtime hook at `0x80360df8`;
- untouched arcade cleanup at `0x80360e00`.

The next candidate should change only the CPS1 XGOC frontend content-path resolution.
