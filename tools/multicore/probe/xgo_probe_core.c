/*
 * Freestanding XGO external-payload proof core.
 *
 * Linked at 0x87000000. Draws a generated RGB565 test pattern through the
 * stock XGO screen path and samples the already-mapped P1/P2 final state words.
 * This is a transport/input proof, not an emulator.
 */

typedef unsigned int u32;
typedef unsigned short u16;

static void (*const run_screen_write)(const void *, int, int, unsigned) =
    (void *)0x8035c398;
static int (*const dly_tsk)(unsigned) = (void *)0x8030f480;

static volatile u32 *const p1_state = (void *)0x80c33ac4;
static volatile u32 *const p2_state = (void *)0x80c33ac8;

void __start(void)
{
    u16 *fb = (void *)0x87100000;
    unsigned frame, x, y;
    u32 p1, p2;

    for (frame = 0; frame < 300; ++frame) {
        p1 = *p1_state;
        p2 = *p2_state;

        for (y = 0; y < 240; ++y) {
            for (x = 0; x < 320; ++x) {
                u16 c = (u16)((((x + frame) & 31) << 11) |
                              ((((y >> 1) + (p1 ? 24 : 0)) & 63) << 5) |
                              ((x ^ y ^ (p2 ? 31 : 0)) & 31));

                /* Top strip visualizes P1 bits; bottom strip visualizes P2. */
                if (y < 12 && (p1 & (1u << (x / 27))))
                    c = 0xffff;
                if (y >= 228 && (p2 & (1u << (x / 27))))
                    c = 0xffff;

                fb[y * 320 + x] = c;
            }
        }

        run_screen_write(fb, 320, 240, 640);

        /* START is 0x0010 in the preserved XGO logical button contract. */
        if ((p1 | p2) & 0x0010)
            break;

        dly_tsk(16);
    }
}
