#include "XGODiagnosticScreen.h"
#include "drivers/xgo/XGODiagnostics.h"
#include <cstdio>
void XGODiagnosticScreen::init() { getRenderer()->clearScreen(); }
int8_t XGODiagnosticScreen::update() { return -1; }
void XGODiagnosticScreen::shutdown() { clearElements(); }
void XGODiagnosticScreen::drawScreen() {
    char line[24];
    const uint32_t raw = xgo_diag_raw.load(std::memory_order_relaxed);
    const uint32_t processed = xgo_diag_processed.load(std::memory_order_relaxed);
    const uint32_t output = xgo_diag_output.load(std::memory_order_relaxed);
    getRenderer()->drawText(0, 0, "XGO DIAGNOSTICS T06");
    getRenderer()->drawText(0, 12, "DPAD / BUTTONS");
    std::snprintf(line, sizeof(line), "RAW %02X / %04X", unsigned(raw >> 16) & 255u, unsigned(raw & 65535u));
    getRenderer()->drawText(0, 24, line);
    std::snprintf(line, sizeof(line), "PROC %02X / %04X", unsigned(processed >> 16) & 255u, unsigned(processed & 65535u));
    getRenderer()->drawText(0, 36, line);
    std::snprintf(line, sizeof(line), "XGO MASK %03X", unsigned(output & 4095u));
    getRenderer()->drawText(0, 48, line);
}
