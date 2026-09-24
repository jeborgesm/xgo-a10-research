# Test132 reinterpretation after full Test93–102 historical review

Date: 2026-09-23
Status: HW + repository archaeology

## Test132 HW fact

With the catalog helper bypassed and the command-3 helper pathname corrected:
- /GB/import/Tetris.gb was present;
- GB/refresh.xgc executed;
- UI reported No New Games;
- no /GB/Tetris.zgb was produced.

Thus GB/refresh.xgc returned 0 and did not materialize Tetris.

## Historical evidence that must govern the next step

The Test93–102 MD investigation already established:
- the FC/SFC-derived parser has fixed .xxx geometry;
- two-character extension handling was explicitly investigated;
- Test97 is the only HW-positive two-character foothold;
- Test100 attempted a dynamic extension/stem rewrite and failed;
- Test101 attempted a corrected final-dot stem rewrite and failed;
- the long-term design target already recorded is to locate the final dot and derive
  stem/extension from it;
- Test102's -5 -> -4 DCC adjustment was semantically correct for a .md suffix but
  its hardware result was storage-confounded;
- clean Test97 artifacts later proved metadata and artwork were actually resolved,
  contradicting simplistic static interpretations of the DCC path.

Therefore Test133's proposed NOP of 0x024C is NOT a new discovery and is withdrawn.
Do not install Test133.

## Critical contradiction

The static Test97 helper description says the inherited geometry contains:
  L-4 '.' / redundant dot / m / d
and the exact Test97 helper retains the first dot branch at 0x024C while NOPing
0x027C. Yet HW Test97 imported four ordinary .md files.

This contradiction means isolated instruction labels are insufficient. Before any
new helper mutation, reconstruct the actual dataflow/register values reaching
0x024C/0x027C/0x02A8/0x02D4 and reconcile them with the known Test97 artifacts.

## Rule reinforced

Do not propose another GB filename-gate patch until the Test97 HW success is
explained from full control/data flow. Historical solution recovery is mandatory,
including negative Test100/101 final-dot experiments.
