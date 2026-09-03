# Interactive XGO mapper v3: real pause-row integration

Status: **STATICALLY CLOSED; HARDWARE TEST PENDING**

v1 proved arbitrary six-button remapping on hardware. v2 regressed exit behavior and also confirmed that replacing `gpapi.bvs` alone cannot suppress the stock pause labels because those labels are rendered after the page resource.

## Recovered stock row renderer

The stock pause renderer draws pages 0..3 as four evenly spaced rows. The loop begins with page index 3 at y=0x106 and decrements toward page 1, while page 0 is drawn separately at y=0x46.

v3 extends the same renderer rather than using a ghost fifth page:

```text
0x00354710  li s1,3      -> li s1,4
0x00354718  li s2,0x106  -> li s2,0x146
```

This adds a fifth row at y=326 for page 4 while preserving the stock spacing:

```text
page0 y=70
page1 y=134
page2 y=198
page3 y=262
page4 y=326  MAPPER
```

The page-limit patch remains:

```text
0x00354ec0  slti s0,v1,3 -> slti s0,v1,4
```

## Real confirm-path entry

v3 no longer activates editing merely by landing on page 4. The stock confirm dispatcher is gated at `0x8035519c` so page 3 retains its original handler and page 4 enters the mapper editor. Thus MAPPER behaves like a normal pause-menu item: navigate to it, then confirm to open.

## Editor input and Start hypothesis

The stock pause poll is:

```text
li a0,0x20f8
jal 0x803526a0
```

That mask cannot return standalone bit `0x1000`. The firmware elsewhere identifies the Start+Select trigger as raw state `0x1001`, strongly supporting `0x1000` as one member of that chord. v3 changes only the pause poll mask:

```text
0x00354e78  0x240420f8 -> 0x240430f8
```

While edit mode is active, event `0x1000` commits the staged six-record map and jumps into the already hardware-proven writer/resume continuation at `0x80355804`.

A stock confirm/action `0x2000` fallback is retained in this hardware candidate only to avoid trapping the test unit if standalone Start differs on hardware. It is not the intended final control.

## Rendering

`gpapi.bvs` remains the page-4 resource, but v3 reserves the left 210 pixels for the normal pause menu. The mapper table is placed in the right panel. Once editing starts, the injected renderer clears the left pause-label strip after the stock renderer runs, eliminating the QUIT/LOAD/SAVE overlay from the active editor.

## Candidate identity

Firmware SHA-256:

```text
48a27fade095327ec782c53c34a427891685ef60529ddd4457059ef087d0d80e
```

LCFG CRC-32/MPEG-2:

```text
0x0f9927a2
```

Mapper resource SHA-256:

```text
47e6db3c92b1ed0bec354e1a15c4bb28c0ce3ab9304688473efba850da10a083
```

SD overlay ZIP SHA-256:

```text
1cc5da73524decdc9fd4f61d7ebbf106ec3aa0680c00f5aa8d551210126ccb2c
```

## Hardware test priorities

1. Verify MAPPER appears as a fifth pause row below the existing entries.
2. Verify merely selecting MAPPER does not enter edit mode.
3. Confirm normally to enter; stock left-side labels should disappear in editor and yellow selector markers should appear.
4. Change one mapping.
5. Press START. Expected: staged map commits, `.zsf.kmp` is written, and gameplay resumes immediately.
6. Relaunch the game and verify persistence.
