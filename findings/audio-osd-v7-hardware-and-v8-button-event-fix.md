# Audio OSD v7 hardware result and v8 boot-event correction

Date: 2026-09-05

## V7 hardware result

The 1-pixel medium-gray RGB565 border works correctly on physical hardware.

Observed benefit: the full OSD range remains visible over black game backgrounds, solving the ambiguity of a black unused-volume region disappearing into the scene.

Border:

```text
RGB565 0x8410
footprint remains 64x8
```

No new gameplay regression was reported from the border change.

## Remaining V7 defect

The volume OSD still appears automatically immediately after the device splash screen and remains visible even though the user has not pressed Volume.

The timing observation is important:

```text
device splash screen
    -> transition to main frontend
    -> volume OSD appears without user input
```

## Root cause

The previous OSD implementations inferred a physical Volume-button event from:

```text
g_volume changed
```

That inference is invalid during boot.

The splash/presentation path can initialize the OSD before startup has restored the persisted volume from `Resources/Archive.sys`. When the settings restore later writes the saved value into `g_volume`, the OSD interprets that legitimate startup state restoration as a user volume change.

This explains why controller-side attempts to clear the initial OSD did not reliably solve the problem: the false event can occur later, when persisted state is applied.

## V8 semantic correction

V8 no longer uses `g_volume changed` as the definition of user intent.

The confirmed physical Volume-button path is:

```text
GPIO L29 press
  -> debounce gate
  -> g_volume += 9
  -> wrap at >=101
  -> hardware mute gate
  -> set_audio_volume()
  -> Archive.sys persistence @ 0x80353a20
```

At runtime `0x8035d6a8`, the existing call to the persistence routine is replaced by a wrapper that:

1. invokes the original persistence routine unchanged;
2. increments a private `user_volume_event_serial`.

Only this physical-button path can increment the serial.

Startup `Archive.sys` restoration changes `g_volume` but does not increment the serial.

The OSD and main-menu refresh code now react to the serial rather than raw volume changes.

Shared state:

```text
0x80002ff0 user_volume_event_serial
0x80002ff4 game_active
0x80002ff8 menu_last_event
0x80002ffc menu_deadline
```

This creates the intended semantic contract:

```text
boot restores volume
    -> audio state changes
    -> NO OSD

physical Volume press
    -> audio state changes
    -> explicit event serial increments
    -> OSD appears
```

## V8 candidate

```text
xgo-audio-osd-v8-button-event-only-test.zip
firmware SHA-256:
4b8f7af994d16371a2664a3d46c983e52ffd1aefbebc5b5a4a9ae63dc6cbe954

ZIP SHA-256:
ba3dad99471c6144fd8f6e9f5891bc88d44b955c5de8a21df905d0d396cdb83a
```

The gray border, fine volume levels, frontend-only repaint gate, Mapper, SNES integration and CPS1 scheduler remain unchanged.

## Future note: splash customization

The user noted that replacing/customizing the device splash screen would be a fun future enhancement, but explicitly does not want to pursue it during the current audio-OSD branch.

Record this only as a future archaeology/UI target; do not expand current scope.
