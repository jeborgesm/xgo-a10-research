# XGO Battery ADC and Power-Level Logic

Status: **ADC-based battery-level classifier and its HC15xx ADC initialization path confirmed by static analysis; absolute voltage calibration remains board-dependent**.

## Scope

This pass follows the XGO periodic task around `0x8035c70c` and the battery/status value consumed by the frontend around `0x80354df0`. It also traces the ADC device back through application initialization and the HC15xx SAR-ADC driver.

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

## ADC device is now traced to the HC15xx SAR-ADC block

The previously-open question of what lies behind the handle at `gp - 0xd38` is substantially resolved.

### Driver attachment

The XGO firmware contains an `adc_attach` routine at approximately `0x8027747c`. It allocates/registers an ADC device and explicitly installs this MMIO base:

```text
0xb8818400
```

The device vtable contains the XGO implementations of the routines identified by embedded symbols such as:

```text
sar_adc_open
sar_adc_start
sar_adc_config
sar_adc_set_default_value
```

The relevant operation slots installed by `adc_attach` include:

```text
+0x2c -> 0x8027acc4   # open/configure path
+0x30 -> 0x8027ad2c
+0x34 -> 0x8027ad34   # start path
+0x38 -> 0x8027addc
+0x3c -> 0x8027ae10   # read/current-value path used by battery poller
```

The `+0x3c` reader ultimately reads the ADC controller register at offset `0x00`, shifts right by 16 and masks to eight bits. Therefore the battery classifier receives an **8-bit hardware ADC result** from the HC15xx SAR-ADC block, not an abstract software battery percentage.

### Application initialization

The board/application initialization routine around `0x801b6c70` retrieves the device using the ADC device type value `0x01300000`, builds a small configuration structure, opens/configures the device, and starts conversion.

The configuration bytes constructed on the stack are:

```text
byte +0 = 0x00
byte +1 = 0xff
byte +2 = 0x06
byte +3 = 0x06
byte +4 = 0x01
word +8 = callback/function pointer 0x801b8d58
```

The ADC driver applies these fields directly to MMIO register bitfields before starting the device. The exact vendor names for every field are not yet recovered, so these values should be preserved as **confirmed raw configuration**, not over-labeled.

The initialization sequence is effectively:

```text
get ADC device (type 0x01300000)
configure/open with XGO parameter block
start ADC
```

Later, frontend initialization around `0x8035c6e8` retrieves the same ADC device type and stores the resulting handle at `gp - 0xd38` for the periodic battery poller.

This closes the earlier uncertainty about whether the ADC strings and MMIO block were merely inherited SDK baggage: **the XGO application actively attaches, configures, starts and polls this ADC device.**

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

The battery state at `gp - 0x769c` has numerous direct reads in the frontend/UI region around `0x80354df0..0x80355ba0`, in addition to the battery poller writes.

Normal values are therefore a discrete UI state:

```text
0, 1, 2, 3, 4
```

and `-1` is treated specially.

Combined with the localized frontend warnings already recovered from the resource bundles (`LOW BATTERY!`, `Please charge it in time.`, etc.), this provides strong executable evidence that `gp - 0x769c` is the XGO battery-level state rather than a generic unrelated ADC reading.

## Comparison with UniFrog / SF2000 HC15xx ADC convention

Current UniFrog HC15xx code reads the battery through `/dev/queryadc0` or directly from the HC15xx ADC controller at the same MMIO base:

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

However, **these converted voltages are not yet confirmed for XGO hardware**. The XGO is physically unlike a stock SF2000 and incorporates a much larger power-bank subsystem, so its divider/reference path may differ. The executable raw thresholds are authoritative; the voltage conversion should remain a comparison/hypothesis until measured or the board-level divider is traced.

## Porting implication

A future XGO board target now has a concrete stock behavior to preserve:

```text
attach HC15xx SAR ADC at 0xb8818400
apply XGO ADC configuration
start conversion
sample the 8-bit ADC result periodically
classify with thresholds 191/183/175/169/161
require five consecutive samples below 161 before declaring low
```

The XGO therefore appears to use the same HC15xx SAR-ADC hardware block as sibling devices while applying its own battery curve and board configuration.

## Confidence

### CONFIRMED

- XGO actively attaches the ADC device during application initialization;
- ADC MMIO base is `0xb8818400`;
- ADC device type used by the application is `0x01300000`;
- XGO builds and applies a concrete ADC configuration parameter block;
- the ADC is explicitly started;
- frontend later reacquires the same ADC device for battery polling;
- battery reads use the device's `+0x3c` operation;
- raw ADC result is the 8-bit field in bits 16..23 of the controller's first register;
- read occurs once per 64 invocations of the subtask;
- five exact raw thresholds `191,183,175,169,161`;
- output states `4,3,2,1,0`;
- below-minimum state is debounced;
- five consecutive sub-threshold observations produce signed state `-1`;
- normal readings clear the low confirmation counter;
- frontend consumes this changing status in many UI paths.

### STRONG EVIDENCE

- this ADC channel is the XGO battery-voltage source used by the visible battery indicator.

### COMPARATIVE EVIDENCE

- UniFrog/SF2000 HC15xx uses the same `0xb8818400` ADC controller and documents a `raw * 20 mV` convention.

### OPEN

- vendor semantic names for each byte in the XGO ADC configuration structure;
- whether XGO raw units have exactly the same `20 mV/count` calibration as stock SF2000 hardware;
- charging-state detection, if any, independent of the level curve;
- whether the power-bank PCB conditions/scales the battery voltage before the H1512 ADC;
- exact relationship between the `-1` sentinel and the timing/appearance of the full-screen low-battery warning.
