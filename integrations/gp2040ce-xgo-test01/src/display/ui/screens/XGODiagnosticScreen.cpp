#include "XGODiagnosticScreen.h"
#include "drivers/xgo/XGODiagnostics.h"
#include <cstdio>
void XGODiagnosticScreen::init() { getRenderer()->clearScreen(); }
int8_t XGODiagnosticScreen::update() { return -1; }
void XGODiagnosticScreen::shutdown() { clearElements(); }
void XGODiagnosticScreen::drawScreen() {
    char line[28];
    // The test unit's top OLED rows are unreliable: metrics only in rows 3-7.
    getRenderer()->drawText(0, 0, "XGO TEST11");
    std::snprintf(line, sizeof(line), "MASK %03X RAW %04X", unsigned(xgo_diag_output.load(std::memory_order_relaxed) & 4095u), unsigned(xgo_diag_raw.load(std::memory_order_relaxed) & 65535u));
    getRenderer()->drawText(0, 3, line);
    std::snprintf(line, sizeof(line), "OK %lu FAIL %lu", (unsigned long)xgo_diag_frames_ok.load(std::memory_order_relaxed), (unsigned long)xgo_diag_frames_failed.load(std::memory_order_relaxed));
    getRenderer()->drawText(0, 4, line);
    std::snprintf(line, sizeof(line), "NOLOAD %lu", (unsigned long)xgo_diag_load_timeouts.load(std::memory_order_relaxed));
    getRenderer()->drawText(0, 5, line);
    std::snprintf(line, sizeof(line), "ACTIVE %lu F %lu", (unsigned long)xgo_diag_active_attempts.load(std::memory_order_relaxed), (unsigned long)xgo_diag_active_failures.load(std::memory_order_relaxed));
    getRenderer()->drawText(0, 6, line);
    std::snprintf(line, sizeof(line), "AFTER %lu MAX %lu", (unsigned long)xgo_diag_fail_after_success.load(std::memory_order_relaxed), (unsigned long)xgo_diag_max_active_failure_streak.load(std::memory_order_relaxed));
    getRenderer()->drawText(0, 7, line);
}
