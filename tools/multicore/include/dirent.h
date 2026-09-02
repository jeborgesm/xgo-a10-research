#ifndef XGO_DIRENT_H
#define XGO_DIRENT_H

#ifdef __cplusplus
extern "C" {
#endif

#define DT_UNKNOWN 0
#define DT_DIR     4
#define DT_REG     8
#define DT_LNK    10

struct dirent {
    unsigned char d_type;
    char d_name[255];
};

/* Bare-metal newlib has no directory API; XGO supplies opaque fs handles. */
typedef void DIR;

DIR *opendir(const char *path);
int closedir(DIR *dir);
struct dirent *readdir(DIR *dir);

#ifdef __cplusplus
}
#endif

#endif
