/* Minimal MAME2000 path support on top of proven XGO newlib syscalls.
 *
 * MAME2000 needs path_basedir() and path_mkdir(). Pulling generic
 * libretro-common file_path_io.c also pulls unsupported bare-metal VFS/dirent.
 * These two functions intentionally implement only the semantics MAME2000 uses.
 */
#include <sys/stat.h>
#include <string.h>
#include <stdlib.h>

typedef int bool;
#define true 1
#define false 0

void path_basedir(char *path)
{
    char *p;
    if (!path || !*path)
        return;

    p = path + strlen(path);
    while (p > path) {
        --p;
        if (*p == '/' || *p == '\\') {
            if (p == path)
                p[1] = 0;
            else
                *p = 0;
            return;
        }
    }

    path[0] = '.';
    path[1] = 0;
}

static int is_dir(const char *path)
{
    struct stat st;
    return path && *path && stat(path, &st) == 0 && S_ISDIR(st.st_mode);
}

bool path_mkdir(const char *dir)
{
    char temp[256];
    unsigned i, n;

    if (!dir || !*dir)
        return false;
    if (is_dir(dir))
        return true;

    n = (unsigned)strlen(dir);
    if (n == 0 || n >= sizeof(temp))
        return false;

    for (i = 0; i <= n; ++i)
        temp[i] = dir[i];

    /* Recursively ensure the parent exists. */
    for (i = n; i > 0; --i) {
        if (temp[i-1] == '/' || temp[i-1] == '\\') {
            char saved = temp[i-1];
            if (i > 1) {
                temp[i-1] = 0;
                if (!is_dir(temp) && !path_mkdir(temp))
                    return false;
                temp[i-1] = saved;
            }
            break;
        }
    }

    if (mkdir(dir, 0777) == 0)
        return true;
    return is_dir(dir);
}
