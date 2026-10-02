# Runtime reinit legacy commands resolved through concrete sound-object dispatcher

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **BIN — COMMAND EFFECTS CLOSED, LEGACY SYMBOLIC NAMES PARTLY OPEN**

## Concrete object registration [BIN]

The active sound object is constructed in the registration path around `0x80309C34`.

The object is created for class:

```text
0x01090000
```

and its operation table is populated explicitly.

Most importantly:

```text
object +0x68 = 0x80309370
object +0x70 = 0x802FDF54
object +0x74 = 0x80304C50
object +0x60 = 0x80306CDC
```

The +0x70/+0x74 entries agree with the previously recovered PCM submission path, confirming this is the correct active sound object.

### Address-decoding correction

The constructor uses:

```text
lui   v0,0x8031
addiu v0,v0,0x9370
```

Because `0x9370` is a negative signed immediate, the result is:

```text
0x80309370
```

not `0x80319370`.

This sign-extension rule is essential when reconstructing firmware function pointers.

## +0x68 is a legacy command switch [BIN]

`0x80309370` takes the incoming command, subtracts `0x10`, range-checks it, and dispatches through a jump table at:

```text
0x808D64E0
```

This closes the exact cases used by `sound_init @ 0x8035C998`.

## Reinit command 0x36 [BIN]

Jump-table target:

```text
0x80309834
```

Effect:

```text
private[0x15D] = (uint8_t)arg
return 0
```

The runtime initializer passes:

```text
arg = 0
```

Therefore reinit explicitly clears private flag `+0x15D`.

This field is significant because the lower transfer-service tail previously recovered checks:

```text
private +0x15D == 1
```

before allowing its periodic +0x17C callback path.

Thus sound reinit **disables that periodic callback/notification mode** before rebuilding the frontend FIFO.

The exact public name of the mode remains OPEN.

## Reinit command 0x59 [BIN]

Jump-table target:

```text
0x80309BEC
 -> 0x802FD8C8
 -> 0x8030AB64
```

The initializer passes arg=1.

`0x8030AB64` operates on the SND hardware block at object/private `+0x2C`.

For arg=1 it sets:

```text
bit 0x08000000 in SND register +0x34
```

For arg=0 it clears that bit.

Therefore command `0x59` is a direct hardware feature enable/disable control.

Its exact vendor bit name is still OPEN; do not call it START/DMA/UNDERRUN until register semantics are independently recovered.

## Reinit command 0x5D [BIN]

Jump-table target:

```text
0x80309C0C
```

Effect:

```text
private[0x208] = (uint8_t)arg
return 1
```

The initializer passes arg=1.

Thus reinit enables private boolean/state `+0x208`.

Exact semantic name remains OPEN.

## Reinit command 0x4C [BIN]

Jump-table target:

```text
0x80309B38
 -> helper 0x803092E0
```

Given a non-null configuration structure, the helper copies selected caller fields into private sound state:

```text
cfg +0x00 -> private +0x1AC
cfg +0x04 -> private +0x1B0
cfg +0x24 -> private +0x1D0
```

Thus 0x4C is a configuration-write/apply operation for this legacy sound object.

## Reinit command 0x4D [BIN]

Jump-table target:

```text
0x80309B4C
 -> helper 0x8030930C
```

Given a non-null structure, it copies private sound state outward:

```text
private +0x1AC -> cfg +0x00
private +0x1B0 -> cfg +0x04
private +0x1C8 -> cfg +0x1C
private +0x1CC -> cfg +0x20
private +0x1D0 -> cfg +0x24
```

Thus 0x4D is the matching configuration-read/query operation.

The sound initializer performs 0x4D followed by 0x4C, effectively reading then reapplying the selected configuration fields.

## Reinit sequence, now materially resolved

The formerly opaque sequence:

```text
5D(1)
4D(cfg)
4C(cfg)
36(0)
59(1)
```

can now be stated without invented SDK names:

```text
enable private +0x208 mode
read selected sound configuration
reapply selected sound configuration
disable +0x15D periodic callback/notification mode
enable SND +0x34 bit 0x08000000
```

This occurs while L23 can remain open in the runtime-reinit path.

## What is still OPEN

- symbolic SDK names for commands 36/4C/4D/59/5D;
- meaning of private +0x208;
- meaning of SND +0x34 bit 27;
- whether the 0x59 hardware feature directly starts/stops transport;
- exact meaning of the +0x15D/+0x17C periodic notification path.

## High-value next step

Recover SND register +0x34 bit 27 from sibling/vendor register definitions or from all XGO xrefs to `0x8030AB64`.

If it is a transport/start/flush/fade control, the runtime-reinit lower-queue behavior may close immediately.

## Hardware gate

Not reached.
