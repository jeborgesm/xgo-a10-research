#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/pio.h"
#include "xgo_fixed_r.pio.h"

#define PIN_CLOCK 26u
#define PIN_DATA 27u

static void passive(uint pin) {
    gpio_init(pin);
    gpio_disable_pulls(pin);
    gpio_set_dir(pin, GPIO_IN);
}

int main(void) {
    passive(PIN_CLOCK);
    passive(PIN_DATA);
    stdio_init_all();
    sleep_ms(1500);

    PIO pio = pio0;
    uint sm = 0;
    uint offset = pio_add_program(pio, &xgo_fixed_r_program);
    pio_gpio_init(pio, PIN_CLOCK);
    pio_gpio_init(pio, PIN_DATA);

    /* DATA latch is permanently LOW. PIO only toggles its output-enable. */
    pio_sm_set_pins_with_mask(pio, sm, 0u, 1u << PIN_DATA);
    pio_sm_set_pindirs_with_mask(pio, sm, 0u,
        (1u << PIN_CLOCK) | (1u << PIN_DATA));

    pio_sm_config c = xgo_fixed_r_program_get_default_config(offset);
    sm_config_set_in_pins(&c, PIN_DATA);
    sm_config_set_set_pins(&c, PIN_DATA, 1);
    pio_sm_init(pio, sm, offset, &c);

    pio_sm_set_pindirs_with_mask(pio, sm, 0u,
        (1u << PIN_CLOCK) | (1u << PIN_DATA));
    pio_sm_set_enabled(pio, sm, true);

    printf("\nXGO-P1 FIXED-R RESPONDER v1\n");
    printf("GP26 CLOCK input; GP27 DATA LOW-sink/high-Z only\n");
    while (true) tight_loop_contents();
}
