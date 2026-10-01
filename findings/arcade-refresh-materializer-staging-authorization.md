# Arcade materializer — staging authorization gate

Date: 2026-09-25
Branch: research-arcade-refresh-four-family
Status: SRC CONTRACT CLOSED; device materializer construction continues

The transient .refresh-set handoff is now explicitly downstream of physical
asset convergence.

For each source ZIP in a family pass:

1. derive/validate driver ZIP basename from the source input;
2. copy or byte-verify /ARCADE/bin/<driver>.zip;
3. resolve metadata/friendly outer identity;
4. decode JPG/JPEG through the unchanged golden decoder path;
5. construct or verify /ARCADE/<friendly>.zfb using exact stock ZFB geometry;
6. only after steps 2 and 5 both succeed, authorize a zero-byte marker:
   /ARCADE/<FAMILY>/.refresh-set/<friendly>.zfb.

At the beginning of the family pass, the staging set is recreated/cleared.
Therefore stale markers from a prior Refresh invocation cannot cause catalog
mutation.

Failure rule:
- if runtime ZIP or ZFB fails verification, no marker is emitted and the
  materializer returns failure;
- catalog helper is not invoked for that family after materializer failure.

Converged/idempotent rule:
- already-identical runtime ZIP + already-compatible ZFB is success;
- the marker is recreated for this invocation;
- catalog helper then decides exact slot0 present/missing.

This preserves recovery of a physically-created-but-unindexed wrapper without
requiring persistent family metadata.

Host reference:
tools/arcade_refresh/materializer_staging_contract.py

This supersedes the text .refresh-list serialization but preserves its
invocation-local family identity principle.
