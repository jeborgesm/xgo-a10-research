# Correction — selector B/Back cleanup requirement

The earlier finding `refresh-selector-native-back-no-custom-hook.md` is superseded in one respect.

Exact Test106 binary confirms B is already decoded as UI event 0x4000 and performs the native previous-state transition. We should preserve that path, but the inherited Test85 `selector_active` word is global and would remain set after native B unless explicitly cleared.

Therefore the final design still uses the native B transition but requires a tiny cleanup trampoline on the already-decoded B path. This is **not** a custom controller decoder.

Test107 implements that correction at 0x8035A844/A848.
