# Hardware Test19 — zero-I/O return probe still hangs at Loading

Hardware result:

- SFII remains on `Loading.....`.
- Test19 contains no trace/file I/O.
- The only probe change after the Test15 A68K+ABI baseline is:

```cpp
Cps1LoadRoms(1);
return 1;
```

Interpretation:

Execution does not reach the forced return placed immediately after the second `Cps1LoadRoms(1)` call.

This strongly localizes the stall inside `Cps1LoadRoms(1)`, but before using the visual symptom as a definitive control-flow oracle, Test20 will calibrate the failure path by forcing `Cps1LoadRoms(1)` to return failure immediately on entry.

If Test20 exits/returns cleanly, Test19 proves the real stall is inside the load pass.
If Test20 still sits on Loading, then the frontend's failure presentation is ambiguous and a different non-filesystem observability mechanism is required.
