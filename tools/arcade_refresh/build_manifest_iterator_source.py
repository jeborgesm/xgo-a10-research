#!/usr/bin/env python3
"""Generate the source template for the on-device Arcade manifest iterator.

The iterator is intentionally independent of catalog serialization.  It feeds
one exact outer .zfb basename into the current-candidate workspace used by the
HW-proven GBA catalog comparison engine.

This file is construction source, not a firmware candidate.
"""
from __future__ import annotations

MAX_NAME=127
CHUNK=128

C_TEMPLATE=r'''
/* XGO A10 Arcade transient manifest iterator.
 * Build as MIPS32 little-endian freestanding code at the catalog-helper
 * execution address chosen by the binary builder.
 *
 * ABI supplied by the builder:
 *   FOPEN/FREAD/FCLOSE = stock callbacks already used by the golden helper
 *   manifest_path       = family-specific compile-time literal
 *   current_name        = existing helper filename workspace
 *
 * next_name() returns:
 *   1  validated .zfb basename copied to current_name
 *   0  EOF
 *  -1  malformed input / I/O failure
 */
typedef unsigned int u32;
typedef int s32;

static int ascii_zfb(const char *s, u32 n) {
    if (n <= 4 || n > 127) return 0;
    for (u32 i=0;i<n;i++) {
        unsigned char c=(unsigned char)s[i];
        if (!c || c=='/' || c=='\\' || c=='\r' || c=='\n') return 0;
    }
    unsigned char a=(unsigned char)s[n-3];
    unsigned char b=(unsigned char)s[n-2];
    unsigned char c=(unsigned char)s[n-1];
    if (a>='A'&&a<='Z') a+=32;
    if (b>='A'&&b<='Z') b+=32;
    if (c>='A'&&c<='Z') c+=32;
    return s[n-4]=='.' && a=='z' && b=='f' && c=='b';
}

/* Reader state is deliberately bounded.  The final binary builder binds the
 * stock file ABI and workspace addresses and then audits every relocation. */
struct manifest_state { void *fp; u32 pos, used, eof; unsigned char buf[128]; };
'''.lstrip()

def main():
    print(C_TEMPLATE)

if __name__=="__main__": main()
