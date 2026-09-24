# Arcade Refresh - family catalog discovery bridge

Date: 2026-09-24
Branch: research-arcade-refresh-four-family
Status: DIRECT BIN FINDING / ARCHITECTURE CORRECTION

## Critical finding before Stage2 construction

Direct disassembly of the exact HW-proven Test106 7000-byte Stage2 shows that
its catalog engine is not fed an explicit list of additions. It opens one root
directory and discovers candidate wrappers by filename suffix.

For MD:
- root literal +0x0A3E = /mnt/sda1/MD
- directory open at +0x02EC
- filename workspace = 0x872A0008
- suffix predicate at +0x03D8..+0x0478 is case-insensitive .zmd
- exact expected bytes:
  - dot  +0x03E4 = 0x2E
  - z    +0x0414 = 0x7A
  - m    +0x0444 = 0x6D
  - d    +0x0470 = 0x64

This means the earlier idea of simply changing the root to /ARCADE is WRONG:
all top-level .zfb wrappers from CPS1/CPS2/IGS/NeoGeo would be visible to every
family engine, because ZFB bytes and names contain no family tag.

This was caught before constructing any candidate.

## Safe bridge: per-family catalog ledger

The materializer will maintain a tiny persistent discovery ledger under each
family root:

/ARCADE/CPS1/.catalog/<friendly>.zfb
/ARCADE/CPS2/.catalog/<friendly>.zfb
/ARCADE/IGS/.catalog/<friendly>.zfb
/ARCADE/NEOGEO/.catalog/<friendly>.zfb

These are marker files, not launch wrappers. Their filename is the exact slot0
identity that must be appended to that family's real Resources catalog.

The real launch assets remain:
/ARCADE/bin/<driver>.zip
/ARCADE/<friendly>.zfb

## Marker creation rule

A family marker may be created only after:
1. source ZIP validated;
2. /ARCADE/bin/<driver>.zip converged and byte-verified;
3. /ARCADE/<friendly>.zfb converged and embedded driver verified;
4. cross-family collision checks pass.

Therefore a marker means: this family owns a physically launchable top-level
ZFB identity and it is eligible for catalog convergence.

Marker content is irrelevant to the catalog scanner. Use a zero-byte file if
the stock file-create wrapper supports it cleanly; otherwise a fixed tiny
sentinel may be used. The catalog engine consumes only directory entry names.

Markers are persistent. They are not transaction backups and are not removed
after catalog append.

## Why this preserves the proven Test106 engine

Each specialized Stage2 changes:
- scan root -> family .catalog directory;
- suffix predicate .zmd -> .zfb;
- LIVE triplet paths -> exact family Resources triplet;
- backup paths -> family recovery namespace;
- MD count-cache write -> NOPs.

The core stable-append, backup, recovery, rollback, LIVE commit and byte-verify
machinery stays mechanically inherited from Test106.

Because the marker filename is <friendly>.zfb, Test106's existing basename
fallback behavior naturally produces:
- slot0 = <friendly>.zfb
- slot1 = <friendly>
- slot2 = <friendly>

which is exactly the desired Arcade catalog record.

## Idempotence and recovery

Existing family marker + already cataloged slot0 -> no append.
Existing family marker + missing catalog entry -> append/recover.
Valid physical assets + marker missing -> materializer recreates marker.
Marker present but physical assets inconsistent -> materializer must fail
before catalog stage; command 6 therefore never calls catalog after a negative
materializer result.

Cross-family duplicate protection remains a materializer responsibility.

## Exact Test106 suffix specialization

Only three extension-character immediates change:
- +0x0444: m (0x6D) -> f (0x66)
- +0x0470: d (0x64) -> b (0x62)
- dot and z remain unchanged.

The four-character geometry remains identical (.zmd -> .zfb).

## Evidence boundary

This ledger is a new Arcade-specific design mechanism, not HW-proven yet.
The underlying directory scanner/catalog transaction engine remains HW-proven
Test106 ancestry. The marker bridge is chosen specifically to avoid rewriting
that engine into an unproven manifest parser or attempting to infer family from
ZFB/ZIP contents.
