// GP2040-CE XGO experimental output driver; upstream base pinned in README.
#pragma once
#include "gpdriver.h"
class XGODriver final : public GPDriver {
public:
 void initialize() override;
 // Core1-only, dedicated USB PHY transaction loop in XGO mode.
 static void runResponder();
 void initializeAux() override {}
 bool process(Gamepad *gamepad) override;
 void processAux() override {}
 uint16_t get_report(uint8_t, hid_report_type_t, uint8_t *, uint16_t) override { return 0; }
 void set_report(uint8_t, hid_report_type_t, uint8_t const *, uint16_t) override {}
 bool vendor_control_xfer_cb(uint8_t, uint8_t, tusb_control_request_t const *) override { return false; }
 const uint16_t *get_descriptor_string_cb(uint8_t, uint16_t) override { return nullptr; }
 const uint8_t *get_descriptor_device_cb() override { return nullptr; }
 const uint8_t *get_hid_descriptor_report_cb(uint8_t) override { return nullptr; }
 const uint8_t *get_descriptor_configuration_cb(uint8_t) override { return nullptr; }
 const uint8_t *get_descriptor_device_qualifier_cb() override { return nullptr; }
 uint16_t GetJoystickMidValue() override { return 0x8000; }
 USBListener *get_usb_auth_listener() override { return nullptr; }
};
