#include <stdio.h>
#include <stdint.h>
#include "pico/stdlib.h"
#include "hardware/clocks.h"
#include "hardware/pio.h"
#include "xgo_sampler.pio.h"

#define PIN_YELLOW 26u
#define PIN_GREEN  27u
#define SAMPLE_HZ 10000000u
#define CAPTURE_WORDS 16384u

static uint32_t capture[CAPTURE_WORDS];

static void force_passive_input(uint pin) {
    gpio_init(pin);
    gpio_disable_pulls(pin);
    gpio_set_dir(pin, GPIO_IN);
}

int main(void) {
    /* Safety first: establish GPIO input/high-Z before assigning PIO function. */
    force_passive_input(PIN_YELLOW);
    force_passive_input(PIN_GREEN);

    stdio_init_all();
    sleep_ms(1500);

    PIO pio = pio0;
    uint sm = 0;
    uint offset = pio_add_program(pio, &xgo_sampler_program);

    pio_gpio_init(pio, PIN_YELLOW);
    pio_gpio_init(pio, PIN_GREEN);

    pio_sm_config c = xgo_sampler_program_get_default_config(offset);
    sm_config_set_in_pins(&c, PIN_YELLOW);
    sm_config_set_in_shift(&c, true, true, 32);

    float div = (float)clock_get_hz(clk_sys) / (float)SAMPLE_HZ;
    sm_config_set_clkdiv(&c, div);

    /* GPIO OE remains disabled: neither firmware nor PIO ever sets these pins as outputs. */
    pio_sm_init(pio, sm, offset, &c);
    pio_sm_set_enabled(pio, sm, true);

    printf("\nXGO-P0 PASSIVE CAPTURE v1\n");
    printf("GP26=YELLOW GP27=GREEN rate=%uHz words=%u samples=%u\n",
           SAMPLE_HZ, CAPTURE_WORDS, CAPTURE_WORDS * 16u);
    printf("Each 32-bit word contains 16 chronological 2-bit samples.\n");
    printf("bit0=GP26/YELLOW bit1=GP27/GREEN. Command: c + Enter\n");

    while (true) {
        int ch = getchar_timeout_us(1000);
        if (ch != 'c' && ch != 'C') continue;

        pio_sm_clear_fifos(pio, sm);
        pio_sm_restart(pio, sm);

        for (uint i = 0; i < CAPTURE_WORDS; ++i)
            capture[i] = pio_sm_get_blocking(pio, sm);

        printf("BEGIN XGO_P0 rate=%u words=%u\n", SAMPLE_HZ, CAPTURE_WORDS);
        for (uint i = 0; i < CAPTURE_WORDS; ++i)
            printf("%08lx\n", (unsigned long)capture[i]);
        printf("END XGO_P0\n");
        printf("READY\n");
    }
}
