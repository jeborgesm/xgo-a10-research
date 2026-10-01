# Arcade catalog helper emitter milestone

Date: 2026-09-25
Branch: research-arcade-refresh-four-family
Status: SOURCE EMITTER COMPLETE; binary execution/audit pending

A guarded binary emitter now exists:
tools/arcade_refresh/emit_arcade_catalog_helpers.py

It accepts only the exact final HW-proven GBA catalog helper:
- size 0x0A52 / 2642
- SHA db7c1173f5b98adb3506b2676a035ba6e54b35a4391709cbbcd7ad92b983cbc6

For each CPS1/CPS2/IGS/NEOGEO helper it:
1. changes only the middle suffix byte .zgb -> .zfb at +0x0444;
2. NOPs only +0x0730..+0x0738, the isolated GBA count-cache invalidation;
3. appends a new family-specific literal table after +0x0A52;
4. retargets exactly seven proven catalog/root address constructions;
5. retains the original GBA code/catalog engine otherwise;
6. emits SHA/size/literal offsets for the subsequent delta audit.

The emitter validates the parent hash and instruction forms before patching and
refuses an unexpected binary.

No hardware candidate exists yet. The next gate is executing the emitter
against the exact parent and independently checking:
- all seven references resolve to appended literals;
- no other pre-0x0A52 bytes changed;
- GBA cache store is absent;
- .zfb predicate is exact;
- helper sizes match the command-6 runner byte counts that will later be wired.
