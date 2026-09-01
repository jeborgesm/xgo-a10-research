/*
 * Minimal external code module for xgo_external_exec_loader.c.
 *
 * Linked at 0x87000000. Returning 0x58474f21 ('XGO!') lets the loader prove
 * that bytes read from SD into the Multicore core window were actually
 * executed after the cache flush.
 */

__attribute__((section(".entry"), used))
unsigned xgo_external_probe(void)
{
    return 0x58474f21u;
}
