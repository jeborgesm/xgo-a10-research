# XGO Battery ADC and Power-Level Logic

Status: **ADC-based battery-level classifier confirmed by static analysis; absolute voltage calibration remains board-dependent**.

## Scope

This pass follows the XGO periodic task around `0x8035c70c` and the battery/status value consumed by the frontend around `0x80354df0`. It also compares the raw-unit convention with the current UniFrog HC15xx/SF2000 battery implementation.

No hardware modification or live voltage measurement was required.

## Battery/status poll routine

Function `0x8035c70c` is called from the same periodic task that services controls and other frontend hardware state.

The routine increments a counter and only performs the analog/status read when:

```text
counter & 0x3f == 0
```

so the relatively expensive read/classification happens once every 64 invocations of this subtask.

A device/driver handle initialized earlier is stored at `gp - 0xd38`. On each sampling interval, firmware loads a function pointer from offset `0x3c` of that handle and calls it. The returned integer is then compared against a hard-coded descending threshold table.

The resulting status is stored as a signed halfword at:

```text
gp - 0x769c
```

## Exact XGO thresholds

The executable classifier is:

```text
raw >= 191  -> level 4
raw >= 183  -> level 3
raw >= 175  -> level 2
raw >= 169  -> level 1
raw >= 161  -> level 0
raw <  161  -> low-sample debounce path
```

In hexadecimal:

```text
191 = 0xBF
183 = 0xB7
175 = 0xAF
169 = 0xA9
161 = 0xA1
```

The code sequence is visible at approximately `0x8035c80c..0x8035c908`.

This is a **CONFIRMED five-step battery/status curve plus a separate below-minimum state**.

## Low-level debounce

A value below `161` does not immediately set the low state.

The firmware increments an 8-bit confirmation counter at `gp - 0x5f44`. If fewer than five consecutive below-threshold observations have occurred, it returns without changing the battery status to the final low sentinel.

After the fifth consecutive low sample, firmware writes:

```text
-1 -> gp - 0x769c
```

A valid reading at or above the normal thresholds clears the low-sample confirmation byte.

Therefore the low-battery state is deliberately debounced rather than responding to one transient ADC dip.

## Frontend consumes this as a changing display/status level

The frontend compares `gp - 0x769c` with its previous value at `gp - 0xd68`. A change causes a display path to execute around `0x80354df0`.

Normal values are therefore a discrete UI state:

```text
0, 1, 2, 3, 4
```

and `-1` is treated specially.

Combined with the localized frontend warnings already recovered from the resource bundles (`LOW BATTERY!`, `Please charge it in time.`, etc.), this provides strong executable evidence that `gp - 0x769c` is the XGO battery-level state rather than a generic unrelated ADC reading.

## Comparison with UniFrog / SF2000 HC15xx ADC convention

Current UniFrog HC15xx code reads the battery through `/dev/queryadc0` or directly from the HC15xx ADC controller at MMIO base:

```text
0xb8818400
```

UniFrog documents the stock-family ADC convention as:

```text
millivolts = raw * 20
```

or equivalently raw units of approximately battery volts × 50.

Applying that convention mechanically to the XGO threshold constants would yield:

```text
raw 191 -> ~3820 mV
raw 183 -> ~3660 mV
raw 175 -> ~3500 mV
raw 169 -> ~3380 mV
raw 161 -> ~3220 mV
```

However, **these converted voltages are not yet confirmed for XGO hardware**. The XGO is physically unlike a stock SF2000 and incorporates a much larger power-bank subsystem, so its divider/reference path may differ. The executable raw thresholds are authoritative; the voltage conversion should remain a comparison/hypothesis until measured or traced through the XGO ADC initialization path.

The important porting implication is that an XGO UniFrog board profile should not blindly reuse the stock SF2000 battery curve.

## Porting implication

A future XGO board target now has a concrete stock behavior to preserve:

```text
sample periodically
classify raw ADC into five visible levels
use XGO-specific thresholds 191/183/175/169/161
require five consecutive samples below 161 before declaring low
```

If UniFrog reads the same raw ADC representation on XGO, reproducing the vendor's behavior should be straightforward. If the board uses a different ADC channel or scaling, the raw values can still serve as the baseline to reproduce once the channel is identified.

## Confidence

### CONFIRMED

- periodic analog/status read from a driver callback;
- read occurs once per 64 invocations of the subtask;
- five exact raw thresholds `191,183,175,169,161`;
- output states `4,3,2,1,0`;
- below-minimum state is debounced;
- five consecutive sub-threshold observations produce signed state `-1`;
- normal readings clear the low confirmation counter;
- frontend observes and renders changes to this discrete status.

### STRONG EVIDENCE

- this state is the XGO battery-level classifier, supported by its frontend use and localized low-battery warning resources.

### COMPARATIVE EVIDENCE

- UniFrog/SF2000 HC15xx uses an 8-bit ADC battery reading and documents a `raw * 20 mV` convention.

### OPEN

- exact XGO ADC device/channel initialization behind the driver handle;
- whether XGO raw units have exactly the same `20 mV/count` calibration as stock SF2000 hardware;
- charging-state detection, if any, independent of the level curve;
- whether the power-bank PCB conditions/scales the battery voltage before the H1512 ADC;
- exact relationship between the `-1` sentinel and the timing/appearance of the full-screen low-battery warning.
