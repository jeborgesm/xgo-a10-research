# Held-button fault isolation — executable receiver-policy counterexample

The Test14 integrated responder has no event/repeat generator: `process()` publishes a 12-bit mask; `emit_frame()` drives it at each host poll. That **does not establish** that the host decodes it consistently.

An offline model with an explicit hypothetical receiver policy (partial transaction decoded with remaining bits released) demonstrates that a single failed frame at/before the asserted slot causes one artificial release and one re-press in a sustained hold. Under a receiver that discards invalid transactions or retains the last complete state, the same conclusion does not follow. This is a **MODEL**, not measured hardware behavior.

Crucially, an early failed frame would affect direction slots 8..11 as well as action slots 0..5. Therefore generic frame failure **alone does not explain** the user's observation that directions hold reliably while action buttons repeat. The direction/action asymmetry must be preserved as a required discriminator; don't promote this model to root-cause proof.

Next gate: identify host receiver behavior for partial frames from XGO firmware, and inspect the live Gamepad processed-state path for intermittent action-only transitions. Only after that can a targeted fix be justified. No Test14 modifications or UF2 from this model.
