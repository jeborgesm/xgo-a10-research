# Street Fighter frame timing as an XGO input-integrity diagnostic — 2026-10-12

## HW — new user observation

User reports that **light punch (LP/jab) and light kick (LK) work well**, while stronger/slower attacks, especially HK and HP, expose missed taps, repeated attacks during sustained holds, and occasional wrong attacks. Slower attack animations prevent immediate acceptance of another attack; their startup/recovery windows make repeated or misdirected commands observable. This is a discriminating observation, not a request to change firmware immediately.

Prior Test15 hardware negative result: `findings/gp2040ce-test15-hardware-failure-2026-10-12.md`. OLED consistently correct. Do not mischaracterize LP/LK as failing; they can appear *unexpectedly* during an HK/HP hold despite working correctly when deliberately pressed.

## WEB — game mechanics, not XGO proof

- Capcom's Hyper Street Fighter II manual explicitly identifies six attack inputs: LP/MP/HP and LK/MK/HK. https://game.capcom.com/manual/CFC/en/ps4/page/10/1
- Street Fighter II gameplay guide states light attacks are generally faster and heavy attacks slower: https://strategywiki.org/wiki/Street_Fighter_II/Gameplay
- General frame-data explanation distinguishes startup, active, and recovery; recovery restricts when a new attack can be executed: https://streetfighter.fandom.com/wiki/Frame_Data and https://streetfighter.fandom.com/wiki/Frame
- Exact frame counts and hold/negative-edge rules are **version-, character-, move-, and game-engine-dependent**. Do not import Street Fighter 6 buffer rules into the XGO's specific SFII build without confirming the ROM/core and gameplay path.

## Diagnostic inference

1. **Recovery is an observation gate, not necessarily the electrical cause.** A wrong serial bit arriving while the fighter is committed to HP/HK may become visible only after the game can accept the next move. A missed short HK press could be input sampled during an unavailable window, even if controller transport were perfect. Conversely, unexpected LP/LK after recovery may represent corrupted/repeated host-side input; both must be distinguished.
2. A held button that generates repeated attacks after recovery **does not, on its own, prove a transport-level release/repress**. Need exact SFII variant and game/core held-button behavior. The user's expected single attack per hold is a hardware observation/acceptance criterion; do not override it with generalized game behavior.
3. **Prioritize unexpected attack *identity***: an LP during sole HK, or LK during sole HP, is more discriminating than the mere absence of a second heavy attack.
4. **Separate input chronology from animation chronology**. Record requested button transition, published Core0 mask, transmitted Core1 mask, host decoded slot, and game-accepted attack as separate layers. OLED validates the first layers only indirectly.
5. Six-button mapping is unresolved. XGO has six attack-capable slots (R1, B4, B3, L1, B1, B2), but game-side binding must be established before associating physical HK with a serial bit or claiming which clock shift would cause LP/LK.
6. A good next offline experiment is to model game attack lockout plus synthetic spurious bits and evaluate whether wrong attacks surface only at recovery. Such a model would be **MODEL**, not hardware proof.

## Decision

**Do not issue Test16 based solely on frame data.** Investigate end-to-end mask-to-host decoding, game-side mappings and per-variant input semantics. Treat LP/LK reliability as a positive control and heavy attack recovery as a temporal amplifier for faults.
