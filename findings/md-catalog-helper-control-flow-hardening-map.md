# MD catalog helper exact control-flow and hardening insertion map

Status: BIN / DESIGN. No hardware candidate.

This note follows the interruption-hardening feasibility audit and uses the exact Test97 MD/catalog.xgc artifact.

Artifact:
- size: 2642 bytes
- SHA-256: 2604672d00ec25f49a96e05214b1a3421b35717d04098800309bd08b26077645

## Exact payload geometry

The helper is dense. Its three MD Resources paths begin at file offsets:
- 0x09E4: /mnt/sda1/Resources/scksp.tax
- 0x0A02: /mnt/sda1/Resources/setxa.nec
- 0x0A20: /mnt/sda1/Resources/wmiui.bvs

The payload ends at 0x0A52 (2642 bytes), after /mnt/sda1/MD plus rb/wb strings.

There are no >=8-byte zero cavities in the executable region before 0x09E4. Robust recovery logic therefore requires deliberate helper growth rather than cavity patching.

## Internal helper calls

Direct JAL inventory in the helper executable body shows only self-contained local helper calls:
- 0x0008 -> local 0x0020
- 0x05BC -> local 0x0784
- 0x05E8 -> local 0x0784
- 0x0614 -> local 0x0784

The external firmware services are reached through the helper's existing indirect-call mechanism. This is favorable for expansion: new recovery routines should reuse the existing service-call convention instead of introducing new absolute firmware dependencies.

## Existing phase boundaries

The existing helper can be treated as four logical phases:

    PHASE A
    read LIVE -> OLD buffers

    PHASE B
    validate OLD triplet

    PHASE C
    scan /MD and construct NEW buffers

    PHASE D
    destructively write NEW TAX/NEC/BVS
    then clear MD count cache

The safest hardening insertion is between B and C, plus a recovery check before normal A/B failure is returned.

## Proposed expanded helper control flow

    START
      |
      v
    read + validate LIVE
      |
      +---------------- valid ----------------+
      |                                       |
    invalid                                   v
      |                              create RECOVERY from OLD
      v                                       |
    load + validate RECOVERY                  v
      |                              re-open / byte-verify
      +-- invalid -> FAIL SAFE                 |
      |                                       v
      +-- valid -> restore LIVE         build NEW generation
                    |                          |
                    v                          v
                 revalidate             commit NEW -> LIVE
                    |                          |
                 invalid -> FAIL              v
                    |                   re-open LIVE triplet
                    v                          |
                 continue               validate generation
                                               |
                                      +--------+--------+
                                      |                 |
                                    valid             invalid
                                      |                 |
                                      v                 v
                                invalidate cache   rollback OLD
                                      |                 |
                                      v                 v
                                   SUCCESS          revalidate
                                                        |
                                                     FAILED

## Same-run versus reboot recovery

Same-run rollback can use OLD directly from 0x87200000 / 0x87210000 / 0x87220000.

Reboot recovery cannot. It requires persistent RECOVERY files.

Therefore a candidate is not considered interruption-hardened merely because it can roll back after fwrite failure. Persistent recovery detection is mandatory.

## Recovery artifact namespace

Do not place backup files in /Resources.

Test91 established that speculative Resources files can interact with native discovery.

Preferred namespace remains under the MD-owned artwork directory, with non-image exact names, e.g.:

    /mnt/sda1/MD/art/.xgo-cat-tax.bak
    /mnt/sda1/MD/art/.xgo-cat-nec.bak
    /mnt/sda1/MD/art/.xgo-cat-bvs.bak

The Test97 materializer contains exact strings for:
- /mnt/sda1/MD/art/.xgo.jpg
- /mnt/sda1/MD/art/.xgo.rgb565
- /mnt/sda1/MD/art/%s.jpg
- /mnt/sda1/MD/art/%s.jpeg

This supports the inference that artwork operations target exact known filenames rather than an arbitrary .xgo-* wildcard. No wildcard purge string was found in the materializer string table.

This placement remains DESIGN until the call sites are fully traced; do not claim HW proof.

## Helper growth requirement

The firmware currently invokes MD/catalog.xgc with explicit size 2642.

Any expanded helper requires:
1. building a larger xgc;
2. changing only the MD catalog helper size constant in the selective dispatcher;
3. confirming the generic runner's 0x87000000 execution/load region can hold the larger payload;
4. keeping the payload far below the runner's 0x86FFFFFF heap guard relationship and all known scratch buffers.

Do not modify FC/SFC helper sizes while proving MD hardening.

## Test gate before candidate construction

A Test104 candidate is blocked until:
- exact artwork cleanup call sites are verified;
- expanded helper size/load safety is closed;
- persistent recovery-file parser/validator is designed;
- all interruption boundaries, including interrupted rollback, are simulated;
- the simulation proves convergence to a coherent old or new generation without relying on rename/fsync.

No hardware request before those gates close.
