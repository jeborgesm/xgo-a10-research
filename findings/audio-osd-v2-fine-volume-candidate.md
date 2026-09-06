# Audio OSD v2 candidate — fine-grained volume policy

Date: 2026-09-05
Branch: `research-audio-osd`

Status: **STATICALLY COMPOSED; READY FOR HARDWARE TEST**

## Exact base

Artifact ID:

```text
audio-osd-v1-on-cps1-scheduler
```

Firmware SHA-256:

```text
1fc85114909d6107ff80be6e199d54dd1d9b918454ceede61d5108246d6f50c1
```

## Recovered stock volume policy

The protected firmware's physical-volume path contains:

```text
8035d670  lw    t5,-3360(gp)      # current volume
8035d67c  addiu t4,t5,33
8035d680  slti  t3,t4,101
8035d684  sw    t4,-3360(gp)
8035d688  bnez  t3,keep
8035d690  li    a0,1              # assert mute
8035d694  sw    zero,-3360(gp)    # wrap to zero
```

So the four-step policy is imposed by a single immediate:

```text
+33
```

The wrap threshold remains 101.

## v2 policy

v2 changes only:

```text
0x8035d67c
addiu t4,t5,33
    ->
addiu t4,t5,9
```

With the stock threshold unchanged, the exact cycle becomes:

```text
0
9
18
27
36
45
54
63
72
81
90
99
0
```

That gives **11 nonzero levels plus mute**, while preserving exact maximum 99 and exact zero/mute behavior.

## Continuous OSD visualization

OSD v1 used four visual buckets because the stock frontend exposed only four states.

For v2 that bucket logic is replaced in-place with:

```text
filled_pixels = (volume * 21) >> 5
```

Properties:

```text
0  -> 0 pixels
99 -> 64 pixels
```

and intermediate states increase monotonically in small visible steps.

No extra display call is added.

## Preserved behavior

Unchanged:

- GPIO L29 volume-button input;
- GPIO L23 zero-volume hardware mute;
- `set_audio_volume @ 0x801b3b40`;
- Archive.sys persistence;
- stock sound-device API;
- Audio OSD v1 display hook;
- Mapper;
- native SNES Test02;
- CPS1 scheduler fix.

## Candidate identity

Firmware SHA-256:

```text
6b3261a9871c2b5678428ae1985176718c140178564ea924241bf6889ec714ac
```

LCFG CRC-32/MPEG-2:

```text
0x1f76664e
```

Candidate ZIP SHA-256:

```text
086c60d7595843c778b04663aa5922ccd05ac966b1c4cb5ee736a78edbba428c
```

## Hardware gate

1. Confirm the Volume button now steps through many more audible levels.
2. Confirm each step visibly advances the OSD bar.
3. Confirm the 99 step reaches full bar.
4. Confirm the next press wraps to mute/empty bar.
5. Confirm mute/unmute remains clean.
6. Re-test SF2 performance.
7. Confirm Start+Select and Mapper.
8. Confirm native SNES still works.

Do not promote to `golden/` until the full regression gate passes.
