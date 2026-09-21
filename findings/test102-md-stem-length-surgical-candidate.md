# Test102 — MD surgical stem-length candidate

Status: **offline-audited; not yet hardware-proven**.

Test102 is derived from the **exact hardware-successful Test97 package**, not Test85/Test100/Test101.

## Offline call-site audit

The shared stem helper at helper offset `0x0DCC` has exactly two direct call sites:

- `0x02E4`
- `0x0524`

The code surrounding both call sites (`0x02E0..0x059F`) is byte-identical between hardware-proven FC, hardware-proven SFC, and Test97 MD. The stem helper itself is also byte-identical across those three before specialization. This shows MD inherited the same fixed `.xxx` stem contract rather than having a separate two-character implementation.

## Surgical change

Test97 contains:

```
0x0DF8: 2441 FFFB   # inherited -5 adjustment
```

Test102 changes only:

```
0x0DF8: FB -> FC
instruction semantic adjustment: -5 -> -4
```

The complete MD helper differs from Test97 by exactly **one byte**. Test97's hardware-proven NOP at `0x027C` remains untouched.

No dynamic parser rewrite is present. Tests100/101 remain rejected.

## Hashes

- Test102 ZIP SHA-256: `3acf1c8d225b5d941403310ea8968595b574362fc6d524b731b6fb454c9cbdff`
- Test102 MD helper SHA-256: `f30fed42ca55be730908f74c789785bd8e4bf787258e651ae48226f17a9cef12`
- Firmware SHA-256: `b66dbcd86ad785875a6804bb7d07c6eb1195ceedb01c0bce8107f65eee2ab66e`

## Scope

This candidate isolates the inferred MD stem/artwork defect only. The separately observed live MD catalog/count/cache invalidation after successful import is unchanged and remains a separate investigation.
