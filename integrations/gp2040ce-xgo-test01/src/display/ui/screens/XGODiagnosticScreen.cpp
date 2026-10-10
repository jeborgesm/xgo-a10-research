#include "XGODiagnosticScreen.h"
#include "drivers/xgo/XGODiagnostics.h"
#include <cstdio>
void XGODiagnosticScreen::init() { getRenderer()->clearScreen(); }
int8_t XGODiagnosticScreen::update() { return -1; }
void XGODiagnosticScreen::shutdown() { clearElements(); }
void XGODiagnosticScreen::drawScreen() {
    char line[26];
    // The upper OLED area is defective on the test unit: reserve rows 0-2.
    getRenderer()->drawText(0, 0, "XGO TEST10");
    const uint32_t raw = xgo_diag_raw.load(std::memory_order_relaxed);
    const uint32_t processed = xgo_diag_processed.load(std::memory_order_relaxed);
    const uint32_t output = xgo_diag_output.load(std::memory_order_relaxed);
    std::snprintf(line, sizeof(line), "R%02X/%04X P%02X/%04X", unsigned(raw >> 16) & 255u, unsigned(raw & 65535u), unsigned(processed >> 16) & 255u, unsigned(processed & 65535u));
    getRenderer()->drawText(0, 3, line);
    std::snprintf(line, sizeof(line), "MASK %03X LAST %03X", unsigned(output & 4095u), unsigned(xgo_diag_last_nonzero_mask.load(std::memory_order_relaxed) & 4095u));
    getRenderer()->drawText(0, 4, line);
    std::snprintf(line, sizeof(line), "CHG %lu DROP %lu", (unsigned long)xgo_diag_mask_changes.load(std::memory_order_relaxed), (unsigned long)xgo_diag_nonzero_to_zero.load(std::memory_order_relaxed));
    getRenderer()->drawText(0, 5, line);
    std::snprintf(line, sizeof(line), "OK %lu FAIL %lu", (unsigned long)xgo_diag_frames_ok.load(std::memory_order_relaxed), (unsigned long)xgo_diag_frames_failed.load(std::memory_order_relaxed));
    getRenderer()->drawText(0, 6, line);
    std::snprintf(line, sizeof(line), "REL %lu CLK %lu", (unsigned long)xgo_diag_release_timeouts.load(std::memory_order_relaxed), (unsigned long)xgo_diag_clock_timeouts.load(std::memory_order_relaxed));
    getRenderer()->drawText(0, 7, line);
}
