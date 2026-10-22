# Handle P1/P2 toggle — offline audit checkpoint (2026-10-21)

Branch: `research-handle-interface-p1-experimental`. Status: **BIN verified / OPEN firmware toggle**.

## Evidence verified

The uploaded `XGO_Handle_As_P1_Experimental(1).zip` contains `bios/bisrv.asd` of 12,768,452 bytes, SHA-256 `8a8cf7a84f7771b0fc116b80521e13d3dfbd5aace73e6053fb7494eaa7d44c4a`, matching the hardware-positive handoff. Independently recomputed CRC-32/MPEG-2 of the payload from file offset `0x200`; it matches the stored LCFG word at `0x18C`. **The uploaded artifact was read only.**

## Implementation constraints reaffirmed

* Existing hook `0x35D53C` and helper `0xA398E4` are a HW-proven **fixed-P1** route, not a toggle.
* Only 48 bytes of zero space were verified at the helper location; its 44-byte code occupies nearly all of it. Extending in place is unsafe.
* The mode flag must be independently verified writable and reset to P2 on boot. A file zero run alone does not establish RAM lifetime or ownership.
* Native Setup activation and visual feedback must be traced to actual call sites. A test oracle does not constitute firmware integration.
* All candidate writes must be instruction-signature gated, change-audited, LCFG-resealed, and checked against the known-good image.

## Failure / correction log

A prior assistant incorrectly delivered an offline routing checkpoint ZIP as though it were useful to hardware test. **It contains no firmware toggle and must not be installed as a toggle candidate.** A subsequent packaging attempt encountered a local `PermissionError`; neither event changes the hardware-positive image. Do not present source-only artifacts as hardware candidates.

## Next implementation gate

Recover a proved native Setup action hook, writable mode storage, and executable extension; only then assemble a mode-conditional MIPS path and produce a new firmware image. Do not change the protected rollback binary or controller responder firmware. Evidence labels: **HW** fixed-P1 tested; **BIN** hash, CRC and existing hook; **OPEN** mode storage, Setup UI, toggle hardware behavior.
