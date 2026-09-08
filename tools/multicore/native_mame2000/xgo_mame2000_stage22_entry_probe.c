/*
 * Test22 production-entry probe.
 * This C function is entered through the real xgo_core_entry.s veneer with
 * external-core GP established exactly as in the full MAME2000 image.
 */
int __core_entry_c(const char *filename, int load_state)
{
    (void)filename;
    (void)load_state;
    return (int)0x58474f31u; /* XGO1 */
}
