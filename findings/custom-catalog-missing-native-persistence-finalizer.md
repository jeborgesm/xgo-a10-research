# CRITICAL closure: custom catalog.xgc omitted the native post-write persistence finalizer

Continued static audit resolves the previously misidentified 0x807D40A8 call enough to establish its architectural role.

## 0x807D40A8 is NOT remove(path)

Wrapper:
```
807D40A8  addiu sp,sp,-24
807D40AC  sw    ra,16(sp)
807D40B0  jal   0x802ABC30
...
```

0x802ABC30 copies a 1024-byte object supplied in a0 into temporary memory and invokes lower filesystem routine 0x802AF338. This is not compatible with a simple pathname unlink/remove interpretation.

Native call sites also disprove the old label:
- 0x807DB540 calls 0x807D40A8 immediately after closing the THIRD catalog output;
- a0 still carries the file/object argument from the preceding fclose path;
- unrelated stock writers call the same primitive after completing/closing file writes.

Treat 0x807D40A8 as a native post-write filesystem finalizer/commit-like primitive until the exact lower-level name is recovered.

## Decisive native-vs-custom difference

Native stock scanner persistence tail:
1. write TAX, close
2. write NEC, close
3. write BVS, close
4. **jal 0x807D40A8**
5. invalidate frontend count cache
6. return success

Custom MD/catalog.xgc persistence tail:
1. write TAX, close
2. write NEC, close
3. write BVS, close
4. **NO 0x807D40A8 CALL**
5. invalidate frontend count cache
6. return success

Binary search confirms MD/catalog.xgc contains zero calls to 0x807D40A8.

This is now a direct architectural defect in the custom catalog writer.

## Corruption correlation

User's damaged file was wmiui.bvs, exactly the third/last MD catalog file. Windows returned 0x80070570 for it after the Test97 update + immediate frontend hard lock + forced power cycle.

The native scanner explicitly invokes its post-write finalizer after that third file. Our custom catalog writer omitted the finalizer and immediately returned Games Updated.

Therefore the corruption sequence has a much stronger explanation:

```
custom catalog.xgc
  TAX write/close
  NEC write/close
  BVS write/close
  [MISSING native post-write finalizer]
  clear cache
  return Games Updated
       |
       v
frontend native workspace stale
       |
       v
MD entry hard-lock
       |
       v
forced power cut
       |
       v
dirty/uncommitted final catalog/FAT state
       |
       v
wmiui.bvs unreadable/corrupt
```

This connects BOTH major Test97 defects to bypassing the native scanner:
- stale native catalog/frontend workspace -> immediate MD hard lock;
- omitted native persistence finalizer -> catalog filesystem state left vulnerable before forced power cut.

## Materializer contrast

Test97 refresh.xgc itself DOES reference/use 0x807D40A8 in its output cleanup/finalization path. The omission is specifically in catalog.xgc, not a universal mistake across our helpers.

## Architectural conclusion strengthened

Replacing MD/catalog.xgc with native scanner 0x807DAE4C(list=2) restores:
- native catalog workspace maintenance;
- native triplet validation/merge;
- native post-write persistence finalizer 0x807D40A8;
- native count-cache invalidation;
- native 1/0/-1 return semantics.

This is substantially safer than attempting to patch custom catalog.xgc with a guessed flush call, because the native scanner provides the entire known stock lifecycle as one unit.

## Test103 direction

Do NOT preserve custom catalog.xgc in the execution path.

Candidate remains:
```
MD/refresh.xgc
    ↓
native scanner 0x807DAE4C(a0=2)
    ↓
existing selective status logic
```

The static case for this substitution is now materially stronger.

Still do not hardware-test until:
- current SD catalog triplet is restored to a known-consistent state;
- exact Test103 binary diff is audited;
- recovery/rollback instructions are prepared;
- preferably capture pristine current Resources before test.

The transaction/journal enhancement can remain a later hardening layer. Restoring the native finalizer and native workspace lifecycle is the immediate correctness/safety repair.
