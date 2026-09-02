# Dormant ALi multimedia framework in XGO firmware

Status: **compiled implementation confirmed; stock XGO frontend exposure not found**.

## Finding

A firmware-wide string and format-dispatch pass shows that `bisrv.asd` contains a much larger multimedia framework than the game-console UI exposes. This is consistent with the already established ALi set-top-box/media SDK ancestry, but the XGO binary contains concrete decoder/parser implementation diagnostics rather than only generic SDK labels.

Representative strings and image offsets include:

```text
0x0099e0f4  FLV File Decoder
0x0099e20c  MusicEngine: wav_init() MALLOC failed!
0x0099e328  MusicEngine: wav_read_data(): Wav file end!
0x0099e448  error!!!
0x0099e468  ==>In play file:%s
0x0099e4f0  <%s> pe_cache_open failed!
0x0099e8ac  matroska,webm
0x0099e8c0  MKV File Decoder
0x0099e913  ?mp3
0x0099e918  https://
0x0099e928  .MP3
0x0099e930  .MP2
0x0099e938  .MP1
0x0099e940  OggS
0x0099e9b0  seek pe cache fail!
0x0099ea18  MP4 File Decoder
0x0099ea34  DECV_AVS_0
0x0099ea40  MPEG1/2
0x0099ea64  mpeg
0x0099ea74  MPEG File Decoder
0x0099ea90  vorbis
0x0099eaf4  .OGG
0x0099eb28  <<<H265  video>>>
0x0099ecc4  Mpeg1/2
0x0099eccc  H.264
0x0099ecd8  H.265
0x0099ece8  m2ts
0x0099edf8  TS File Decoder
0x0099ee14  .WAV
```

The surrounding strings are implementation-level state/error messages: allocation failures, packet reads, seeking, metadata parsing, audio task creation, Ogg synchronization, transport-stream buffering, A/V PTS synchronization, H.264 SPS/PPS/VUI parsing, and decoder-device names. This is substantially stronger than finding a list of media extensions in a resource table.

## Formats represented in the compiled image

The binary contains identifiable support code for at least:

- FLV;
- Matroska / WebM;
- MP4/MOV-family parsing;
- MPEG program/elementary streams;
- MPEG transport streams / M2TS;
- WAV/PCM;
- MP1/MP2/MP3;
- Ogg/Vorbis;
- MPEG-1/2 video;
- H.264/AVC;
- H.265/HEVC.

The H.264 area contains detailed SPS/PPS/VUI parser diagnostics, while the transport-stream code contains explicit H.265 identification. This indicates real linked media-library code, not merely frontend text.

## Frontend reachability

The previously reconstructed XGO ROM-extension dispatcher routes game formats and wrappers such as NES, SFC, GBA, GB/GBC, MD/SMS, ZIP/BKP and ZFC/ZSF/ZMD/ZGB/ZFB. No normal stock-XGO launch route for `.mp3`, `.wav`, `.ogg`, `.mkv`, `.webm`, `.mp4`, `.flv`, `.m2ts` or comparable media files has been identified.

Therefore the correct interpretation is:

**CONFIRMED:** substantial ALi multimedia playback/decoder infrastructure is linked into the shipped XGO application image.

**CONFIRMED:** the known stock XGO game-extension dispatcher does not expose those media formats.

**STRONG EVIDENCE:** this is dormant inherited ALi SDK functionality retained in the OEM firmware rather than an advertised/normal XGO feature.

It should not be interpreted as proof that every represented codec is usable on the XGO board without additional initialization, memory, frontend and hardware-decoder work.

## Why it matters

This greatly expands the known software ancestry of the XGO. `bisrv.asd` is not simply a small game launcher plus libretro cores: it carries a sizeable portion of a general ALi media-player/STB software stack. These dormant subsystems are useful symbol anchors for future disassembly because public ALi SDK source can potentially name many otherwise anonymous XGO functions.
