#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/pio.h"
#include "xgo_scripted.pio.h"

#define PIN_CLOCK 26u
#define PIN_DATA 27u

#define R_BIT      (1u << 0)
#define A_BIT      (1u << 4)
#define B_BIT      (1u << 5)
#define DOWN_BIT   (1u << 9)
#define LEFT_BIT   (1u << 10)
#define RIGHT_BIT  (1u << 11)

/* Current Contra mapper observation: raw R reaches FC A (jump).
   For the complementary FC B action (shoot), use raw B initially.
   If the user's current .kmp maps another physical action to FC B,
   change SHOOT_BIT only; transport logic remains unchanged. */
#define JUMP_BIT R_BIT
#define SHOOT_BIT B_BIT

typedef struct {
    uint16_t mask;
    uint16_t polls;
} phase_t;

/* ~62.37 polls/sec. Visible autonomous loop:
   RIGHT -> jump+shoot -> LEFT -> DOWN -> jump+shoot -> brief idle. */
static const phase_t script[] = {
    { RIGHT_BIT,              50 },
    { RIGHT_BIT|JUMP_BIT|SHOOT_BIT, 12 },
    { RIGHT_BIT,              18 },
    { 0,                       8 },
    { LEFT_BIT,               50 },
    { DOWN_BIT,               24 },
    { JUMP_BIT|SHOOT_BIT,     12 },
    { 0,                      24 },
};

static void passive(uint pin) {
    gpio_init(pin);
    gpio_disable_pulls(pin);
    gpio_set_dir(pin, GPIO_IN);
}

static inline uint32_t fifo_word(uint16_t pressed) {
    /* PIO shifts right; bit0 is serialized first. PINDIRS bit=1 sinks LOW. */
    return pressed & 0x0fffu;
}

int main(void) {
    passive(PIN_CLOCK);
    passive(PIN_DATA);
    stdio_init_all();
    sleep_ms(1500);

    PIO pio = pio0;
    uint sm = 0;
    uint offset = pio_add_program(pio, &xgo_scripted_program);
    pio_gpio_init(pio, PIN_CLOCK);
    pio_gpio_init(pio, PIN_DATA);

    /* Permanent LOW output latch. Only OE/direction is serialized. */
    pio_sm_set_pins_with_mask(pio, sm, 0u, 1u << PIN_DATA);
    pio_sm_set_pindirs_with_mask(pio, sm, 0u,
        (1u << PIN_CLOCK) | (1u << PIN_DATA));

    pio_sm_config c = xgo_scripted_program_get_default_config(offset);
    sm_config_set_in_pins(&c, PIN_DATA);
    sm_config_set_out_pins(&c, PIN_DATA, 1);
    sm_config_set_set_pins(&c, PIN_DATA, 1);
    sm_config_set_out_shift(&c, true, false, 32);
    pio_sm_init(pio, sm, offset, &c);
    pio_sm_set_pindirs_with_mask(pio, sm, 0u,
        (1u << PIN_CLOCK) | (1u << PIN_DATA));

    /* Seed first transaction before enabling: no FIFO starvation at first poll. */
    size_t phase = 0;
    uint16_t remaining = script[0].polls;
    pio_sm_put_blocking(pio, sm, fifo_word(script[0].mask));
    pio_sm_set_enabled(pio, sm, true);

    printf("\nXGO-P2 SCRIPTED CONTRA v1\n");
    printf("RIGHT -> jump+shoot -> LEFT -> DOWN -> jump+shoot\n");

    while (true) {
        /* One FIFO word is consumed per XGO poll. Keep exactly the next state queued.
           Blocking here naturally paces the script from the host's ~62.37Hz polls. */
        pio_sm_put_blocking(pio, sm, fifo_word(script[phase].mask));
        if (--remaining == 0) {
            phase = (phase + 1) % (sizeof(script) / sizeof(script[0]));
            remaining = script[phase].polls;
        }
    }
}
