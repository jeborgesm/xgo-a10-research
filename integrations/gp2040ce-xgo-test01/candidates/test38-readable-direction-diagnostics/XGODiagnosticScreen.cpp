#include "XGODiagnosticScreen.h"
#include "drivers/xgo/XGODiagnostics.h"
#include <cstdio>
void XGODiagnosticScreen::init() { getRenderer()->clearScreen(); }
int8_t XGODiagnosticScreen::update() { return -1; }
void XGODiagnosticScreen::shutdown() { clearElements(); }
void XGODiagnosticScreen::drawScreen() {
    char line[28];
    // The test unit's top OLED rows are unreliable: metrics only in rows 3-7.
    getRenderer()->drawText(0, 0, "XGO TEST38");
    std::snprintf(line, sizeof(line), "DIR %03X MASK %03X", unsigned((xgo_diag_output.load(std::memory_order_relaxed) >> 8) & 15u), unsigned(xgo_diag_output.load(std::memory_order_relaxed) & 4095u));
    getRenderer()->drawText(0, 3, line);
    std::snprintf(line, sizeof(line), "CHG %lu", (unsigned long)xgo_diag_direction_transitions.load(std::memory_order_relaxed));
    getRenderer()->drawText(0, 4, line);
    std::snprintf(line, sizeof(line), "FAST %lu", (unsigned long)xgo_diag_direction_short_pulses.load(std::memory_order_relaxed));
    getRenderer()->drawText(0, 5, line);
    std::snprintf(line, sizeof(line), "OPPOSITE %lu", (unsigned long)xgo_diag_direction_opposites.load(std::memory_order_relaxed));
    getRenderer()->drawText(0, 6, line);
    std::snprintf(line, sizeof(line), "OK %lu ERR %lu", (unsigned long)xgo_diag_frames_ok.load(std::memory_order_relaxed), (unsigned long)xgo_diag_active_failures.load(std::memory_order_relaxed));
    getRenderer()->drawText(0, 7, line);
}
