#pragma once
#include <atomic>
#include <cstdint>
// Read-only OLED diagnostics; stores GPIO-derived and processed button/dpad masks.
// Each value is an independently atomic snapshot (not a transaction log).
extern std::atomic<uint32_t> xgo_diag_raw;
extern std::atomic<uint32_t> xgo_diag_processed;
extern std::atomic<uint32_t> xgo_diag_output;
extern std::atomic<uint32_t> xgo_diag_frames_ok;
extern std::atomic<uint32_t> xgo_diag_frames_failed;
extern std::atomic<uint32_t> xgo_diag_load_timeouts;
extern std::atomic<uint32_t> xgo_diag_release_timeouts;
extern std::atomic<uint32_t> xgo_diag_clock_timeouts;
extern std::atomic<uint32_t> xgo_diag_last_failure_slot;
// Test09: coarse microsecond observations; no changes to serial thresholds.
extern std::atomic<uint32_t> xgo_diag_load_low_last_us;
extern std::atomic<uint32_t> xgo_diag_load_low_max_us;
extern std::atomic<uint32_t> xgo_diag_clock_failure_slots[13];
// Test10: per-transaction mask transitions; zero frames are not automatically faults.
extern std::atomic<uint32_t> xgo_diag_mask_changes;
extern std::atomic<uint32_t> xgo_diag_zero_frames;
extern std::atomic<uint32_t> xgo_diag_last_nonzero_mask;
extern std::atomic<uint32_t> xgo_diag_nonzero_to_zero;
// Test11: distinguish missed LOAD acquisition from active-frame failures.
// A frame attempt starts only after DATA LOW is detected.
extern std::atomic<uint32_t> xgo_diag_active_attempts;
extern std::atomic<uint32_t> xgo_diag_active_failures;
extern std::atomic<uint32_t> xgo_diag_fail_after_success;
extern std::atomic<uint32_t> xgo_diag_consecutive_active_failures;
extern std::atomic<uint32_t> xgo_diag_max_active_failure_streak;
