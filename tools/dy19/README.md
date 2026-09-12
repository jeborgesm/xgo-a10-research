# DY19 Internet Archive extraction notes

This directory contains reproducible probes for the owner-originated Internet Archive item:

`dy-19-firmware-2024315`

The first workflow stage fetches the Internet Archive Metadata API and prints the exact downloadable file inventory, sizes and hashes. Subsequent extraction should avoid downloading bulk ROM content where possible and should recover only firmware/resources/list metadata needed for comparison.

Probe run requested: 2026-09-07.
