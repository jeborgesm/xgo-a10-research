#pragma once
#include "GPGFX_UI_widgets.h"
class XGODiagnosticScreen : public GPScreen {
public:
    explicit XGODiagnosticScreen(GPGFX* renderer) { setRenderer(renderer); }
    void init() override;
    int8_t update() override;
    void shutdown() override;
protected:
    void drawScreen() override;
};
