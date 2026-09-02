#ifndef XGO_STOCK_GP_REDIRECTS_H
#define XGO_STOCK_GP_REDIRECTS_H

/*
 * Compile-time symbol redirection for C glue that was written against the
 * recovered stock service names. The corresponding declarations in the C
 * source are macro-expanded too, preserving the original function signatures
 * while ensuring no external-core C call enters stock firmware with core _gp.
 */
#define fs_open           xgo_stock_fs_open
#define fs_opendir        xgo_stock_fs_opendir
#define fs_mkdir          xgo_stock_fs_mkdir
#define fs_fstat          xgo_stock_fs_fstat
#define fs_stat           xgo_stock_fs_stat
#define fs_read           xgo_stock_fs_read
#define fs_write          xgo_stock_fs_write
#define fs_lseek          xgo_stock_fs_lseek
#define fs_readdir        xgo_stock_fs_readdir
#define fs_close          xgo_stock_fs_close
#define fs_closedir       xgo_stock_fs_closedir
#define os_get_tick_count xgo_stock_os_get_tick_count
#define dly_tsk           xgo_stock_dly_tsk

#endif
