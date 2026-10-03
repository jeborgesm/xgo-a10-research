# Test C — conditional internal-speaker mono fold — hardware result

Date: 2026-10-02
Branch: `research-audio-mono-routing`
Status: **HW PASS for internal gameplay + AV mode smoke; high-volume distortion observation remains**

## Candidate policy

Test C derives from HW-PASS native-22050 Test A.

- LCD/internal mode (cached L15=1): `L'=(L>>1)+(R>>1)`, `R'=R`
- TV/AV mode (cached L15=0): preserve original `L,R`
- stereo S16 transport geometry is unchanged
- Test A rate/scheduler/ring/queue/OSD behavior is unchanged

## Hardware report

User report:

> sounds ok, a little distortion on the very high volume, not sure if it is the speaker being strained. I tried the av out and it works fine, plays smooth and the sound is fine. unfortunately, I don't have a cable to connect it to video, left and right, just video and a single audio.

## Evidence

**HW**
- Test C boots and gameplay audio sounds normal in the tested internal-speaker path.
- At very high volume the user hears a little distortion.
- AV-out mode activates and gameplay remains smooth with sound present and subjectively fine.
- Available AV lead exposes video + one audio connector, so independent external L/R stereo preservation was not tested.

**INF**
- The high-volume distortion is not yet attributable. It may be speaker/amplifier headroom or fold-related; this result alone does not distinguish them.
- AV smoke success supports that the L15-conditioned bypass does not break the tested external audio path.
- True two-channel AV stereo preservation remains OPEN because the user's cable cannot expose independent left/right outputs.

## Promotion rule

Do not call the high-volume distortion closed or claim external stereo HW proof.

The internal-speaker mono mechanism itself is hardware-successful. Before golden promotion, compare the same high-volume passage on unmodified Test A versus Test C at the same volume. If both distort similarly, the observation belongs to speaker/amp/headroom rather than the fold. If Test C alone distorts materially more, revisit fold gain/headroom.
