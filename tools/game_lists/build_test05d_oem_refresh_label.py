#!/usr/bin/env python3
"""Build XGO Game-List Test05d: OEM-style Refresh label menu (no writes).

Inputs:
  --v8-zip       exact hardware-confirmed Audio OSD v8 golden ZIP
  --ui-source    private stock setup-UI source ZIP containing qasf.bel plus six
                 language-specific 640x480 RGB565 User Menu screens

Test05d changes only the User Menu UI/navigation/dispatch surface:
  - 3 columns -> 2x2 layout shifted upward 20 px;
  - selector wraps 0..3 instead of 0..2;
  - row 3 is visible as Refresh and is a harmless no-op stub;
  - rows 0..2 retain their stock destinations;
  - NTSC/PAL is relocated into the moved TV tile;
  - setup background refresh is expanded through row 429 so old selector overlays are erased while the stock footer remains untouched;
  - NO catalog/resource mutation path is installed.

This isolates the UI integration before binding row 3 to the hardware-proven
Test04 writer/scanner work.
"""
from __future__ import annotations
import argparse, base64, hashlib, math, struct, tarfile, zipfile, zlib
from pathlib import Path

V8_ZIP_SHA = "ba3dad99471c6144fd8f6e9f5891bc88d44b955c5de8a21df905d0d396cdb83a"
V8_FW_SHA = "4b8f7af994d16371a2664a3d46c983e52ffd1aefbebc5b5a4a9ae63dc6cbe954"
UI_SOURCE_SHAS = {
    "zip": "16d4ee25357d725ddc574c86b69f5b570c73deb83dab8f2b98056ed31ab37843",
    "tar.xz": "fac668aff96315caab6ee86d5a3e8d5b5c20dc1477a6fe41ecb7361a814b028e",
    "tar.xz-verified": "6a1264b9ebf49f4bb28f2185168ca400fbc883a9bacfde6874796baaf813701c",
    "mapper-v19-card": "c45925f965cf86b4e1efc622b02aabb5545122814743aaf7723d4dbf6ba4ec81",
}
UI_MEMBERS = {
    "qasf.bel":  (614400,"907a008fe8562ade903d8a1494546783636b5d705a84ca2e60b9e8d3cd45cce4"),
    "dxkgi.ctp": (614400,"dbd09592acc4531c75d195663c1fcb47acffa119387224100bd77df0ba7094bd"),
    "itiss.ers": (614400,"a73ed67960aa44528ac1ecf1b61db345956d6e7e830630edf62689d83823521c"),
    "esent.bvs": (614400,"eb2a5a562de3053c52cfc0c1108711ab92e6bf81c34d819aa18a7a48913e3fa0"),
    "awusa.tax": (614400,"80e381d3c3ba6c15bdfdfedfbebe9b1f94d92070c596a35bc0b1d81dddfd8d6e"),
    "vssvc.nec": (614400,"e1962a21fb3d45b223b9f38dedbd1d1b2f957f5333229ffec83856d293d30839"),
    "vidca.bvs": (614400,"fd55e3ad16c03c431591962cbfce69325b48a199f149d1a05db8c04db1e6218e"),
}

BASE=0x80000000
POLY=0x04C11DB7
CAVE=0x807DAB98
CAVE_LIMIT=0x807DBBA0
UP_WRAP=0x80359AA4
RENDER_START=0x80359B1C
DOWN_LIMIT=0x80359E60
DISPATCH=0x80359EA8
STOCK_TV=0x80359EB0
STOCK_OTHER=0x80356BFC
MENU_REDRAW=0x80359ABC
NTSC_X=0x80359B88
NTSC_Y=0x80359B8C
TVMODE_A_X=0x8035AC98
TVMODE_A_Y=0x8035AC9C
TVMODE_B_X=0x8035ACD0
TVMODE_B_Y=0x8035ACD4

R={'zero':0,'at':1,'v0':2,'v1':3,'a0':4,'a1':5,'a2':6,'a3':7,'t0':8,'t1':9,'t2':10,'t3':11,'t4':12,'t5':13,'t6':14,'t7':15,'s0':16,'s1':17,'s2':18,'s3':19,'s4':20,'s5':21,'s6':22,'s7':23,'t8':24,'t9':25,'k0':26,'k1':27,'gp':28,'sp':29,'fp':30,'ra':31}
def sha(b): return hashlib.sha256(b).hexdigest()
def rtype(rs,rt,rd,sh,fn): return (R[rs]<<21)|(R[rt]<<16)|(R[rd]<<11)|(sh<<6)|fn
def iop(op,rs,rt,imm): return (op<<26)|(R[rs]<<21)|(R[rt]<<16)|(imm&0xffff)
def jop(op,addr): return (op<<26)|((addr>>2)&0x03ffffff)
def addiu(rt,rs,imm): return iop(9,rs,rt,imm)
def andi(rt,rs,imm): return iop(12,rs,rt,imm)
def sll(rd,rt,sh): return rtype('zero',rt,rd,sh,0)
def subu(rd,rs,rt): return rtype(rs,rt,rd,0,0x23)
def j(addr): return jop(2,addr)
def beq(rs,rt,off): return iop(4,rs,rt,off)
def nop(): return 0

def branch_word(pc,rs,rt,target):
    d=target-(pc+4); assert d%4==0
    return beq(rs,rt,d//4)

def build_stub():
    # Entry is reached only after rows 0 and 1 were already handled by stock code.
    # The original delay slot at 0x80359eac still runs: li s2,1.
    pc=CAVE; words=[]; labels={}
    def emit(w):
        nonlocal pc; words.append((pc,w)); pc+=4
    def label(n): labels[n]=pc
    emit(addiu('t0','zero',2)); words.append((pc,('beq','v1','t0','row2')));pc+=4;emit(nop())
    emit(addiu('t0','zero',3)); words.append((pc,('beq','v1','t0','row3')));pc+=4;emit(nop())
    emit(j(STOCK_OTHER));emit(nop())
    label('row2');emit(j(STOCK_TV));emit(nop())
    label('row3');emit(addiu('fp','zero',1));emit(addiu('s2','zero',1));emit(j(MENU_REDRAW));emit(nop())
    out=bytearray()
    for at,w in words:
        if isinstance(w,tuple):
            _,rs,rt,l=w; w=branch_word(at,rs,rt,labels[l])
        out += struct.pack('<I',w)
    return bytes(out)

LABEL_X = {
    'dxkgi.ctp': [(35,225),(235,410),(420,620)],
    'itiss.ers': [(40,230),(250,400),(410,620)],
    'esent.bvs': [(35,230),(260,390),(400,620)],
    'awusa.tax': [(20,260),(260,400),(400,620)],
    'vssvc.nec': [(40,220),(240,410),(420,620)],
    'vidca.bvs': [(5,275),(275,400),(390,625)],
}
REFRESH_W=84
REFRESH_H=17
REFRESH_ALPHA_ZB64='eNqdkl1IU2EYxx9XDpNaSqub6INSJNKLrG4iCKLoEwua9gF9XMybgii86CaiEKSLgtGHyhq00rLNK82g8kIRYdOlVHjRGNhaRFuthVPbprZ/7/ue007vTofI/8V5Pv7P+R3O+z5UBFWTb2+uJr1WdMRm2+mfssGvFYz52MF0pzuO5E798H1EnQ3/z9yiZBYPvi7VDY+hlmjeTFr8HSd1w2FsV7OC4nkwaQBNPFQ9jGQS/WdMLH0ijrrHDte6vh+tske0wf0+PRm8XSaYg6aLY6mJ3m15zCE0smftDAZbeqbhKSA65UjC66g/gY7hQLNd9mjzFHwu12t8q+LMXnfM7QwiVSExrVM4QrRmGqdZUT4Oe+7f6/DZyymy14krfOISPJyZ8C0hMvtw409myVOMm4mu47koj+JNjmkDKngheyPYzYvCveViYhMvLuCltku3uuIIV7JuAOeUG8uiVGNGRU/22jG0UbujmIjHMSyYqsINy3g3gS6HUApbNeYo6b21EeDd3ZpihRlQ2a+0f6/DF6vopnMfwS6N6f+bV3otxLKJxoXahMSkF3gkYhz7dfv5+408j2l9/bMsHEbMsjQO8OjHWUNmnqfoEDKFBky6io8WFpowIErzseU6puRZDteQeiIrjZhFIbQqO8iXb0EzOnVMybOmktW8eRBRkxGT9iC7g9/WDPwtbREEV+mYsncec33Oe/0/52xkyCQvQotYqHzwIZMYvVyiP888b1/3p9lMuK2aZOYvZ0O8yQ=='
def pix_get(b,x,y): return b[(y*640+x)*2] | (b[(y*640+x)*2+1]<<8)
def pix_set(b,x,y,v=0xffff):
    o=(y*640+x)*2; b[o]=v&255; b[o+1]=(v>>8)&255

def copy_rect(dst,src,sx,sy,w,h,dx,dy):
    for row in range(h):
        so=((sy+row)*640+sx)*2; do=((dy+row)*640+dx)*2
        dst[do:do+w*2]=src[so:so+w*2]

def is_label_pixel(v):
    r=(v>>11)&31; g=(v>>5)&63; b=v&31
    return r>=24 and g>=48 and b>=24

def move_label(dst,src,x0,x1,dest_center,dest_y):
    pts=[]
    for y in range(315,390):
        for x in range(x0,x1):
            v=pix_get(src,x,y)
            if is_label_pixel(v): pts.append((x,y,v))
    assert pts
    bx0=min(x for x,_,_ in pts); bx1=max(x for x,_,_ in pts)+1
    by0=min(y for _,y,_ in pts)
    dx=int(dest_center-(bx1-bx0)/2)
    for x,y,v in pts:
        nx=dx+(x-bx0); ny=dest_y+(y-by0)
        if 0<=nx<640 and 0<=ny<480: pix_set(dst,nx,ny,v)

def draw_refresh(dst,cx,cy):
    for y in range(cy-45,cy+46):
        for x in range(cx-45,cx+46):
            dx=x-cx; dy=y-cy; d=(dx*dx+dy*dy)**0.5
            if not 34<=d<=40: continue
            a=(math.degrees(math.atan2(dy,dx))+360)%360
            if (35<=a<=200) or (215<=a<=359) or (0<=a<=20): pix_set(dst,x,y)
    for yy in range(cy-33,cy-18):
        span=(yy-(cy-33))//2+2
        for x in range(cx-40,cx-40+span): pix_set(dst,x,yy)
    for yy in range(cy+18,cy+33):
        span=(cy+33-yy)//2+2
        for x in range(cx+40-span,cx+40): pix_set(dst,x,yy)

def draw_refresh_label(dst,cx,y):
    alpha=zlib.decompress(base64.b64decode(REFRESH_ALPHA_ZB64))
    assert len(alpha)==REFRESH_W*REFRESH_H
    x0=int(cx-REFRESH_W/2)
    for yy in range(REFRESH_H):
        for xx in range(REFRESH_W):
            a=alpha[yy*REFRESH_W+xx]
            if not a: continue
            x=x0+xx; py=y+yy
            if not (0<=x<640 and 0<=py<480): continue
            o=(py*640+x)*2
            v=dst[o] | (dst[o+1]<<8)
            r=(v>>11)&31; g=(v>>5)&63; b=v&31
            r=(r*(255-a)+31*a+127)//255
            g=(g*(255-a)+63*a+127)//255
            b=(b*(255-a)+31*a+127)//255
            nv=(r<<11)|(g<<5)|b
            dst[o]=nv&255; dst[o+1]=(nv>>8)&255

def build_screen(src,blank,name):
    assert len(src)==len(blank)==614400
    dst=bytearray(blank)
    copy_rect(dst,src,490,0,150,135,490,0)
    for sx,(dx,dy) in zip((54,240,427),((106,6),(362,6),(106,230))):
        copy_rect(dst,src,sx,153,159,159,dx,dy)
    copy_rect(dst,src,54,153,159,159,362,230)
    draw_refresh(dst,362+79,230+79)
    for bounds,cx,dy in zip(LABEL_X[name],(185,441,185),(168,168,392)):
        move_label(dst,src,*bounds,cx,dy)
    draw_refresh_label(dst,441,392)
    return bytes(dst)

def crc32_mpeg2(data):
    crc=0xffffffff
    for byte in data:
        crc ^= byte<<24
        for _ in range(8): crc=(((crc<<1)^POLY) if crc&0x80000000 else crc<<1)&0xffffffff
    return crc

def zi(name):
    z=zipfile.ZipInfo(name,(2026,9,7,15,0,0)); z.compress_type=zipfile.ZIP_DEFLATED
    z.create_system=3; z.external_attr=0o600<<16; return z

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--v8-zip',type=Path,required=True); ap.add_argument('--ui-source',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); args=ap.parse_args()
    assert sha(args.v8_zip.read_bytes())==V8_ZIP_SHA
    source_hash=sha(args.ui_source.read_bytes())
    assert source_hash in UI_SOURCE_SHAS.values(), source_hash
    with zipfile.ZipFile(args.v8_zip) as z: fw=bytearray(z.read('bios/bisrv.asd'))
    assert sha(fw)==V8_FW_SHA
    if source_hash == UI_SOURCE_SHAS['zip']:
        with zipfile.ZipFile(args.ui_source) as z:
            ui={n:z.read(n) for n in UI_MEMBERS}
    elif source_hash == UI_SOURCE_SHAS['mapper-v19-card']:
        with zipfile.ZipFile(args.ui_source) as z:
            ui={n:z.read('Resources/'+n) for n in UI_MEMBERS}
    else:
        with tarfile.open(args.ui_source, 'r:xz') as t:
            members={m.name.lstrip('./'):m for m in t.getmembers() if m.isfile()}
            ui={n:t.extractfile(members[n]).read() for n in UI_MEMBERS}
    for n,b in ui.items(): assert (len(b),sha(b))==UI_MEMBERS[n]

    def word(addr): return struct.unpack_from('<I',fw,addr-BASE)[0]
    def put(addr,w): struct.pack_into('<I',fw,addr-BASE,w)
    assert word(UP_WRAP)==0x24190002
    assert word(DOWN_LIMIT)==0x24020002
    assert word(DISPATCH)==0x1469f354
    assert word(DISPATCH+4)==0x24120001
    expected=[0x00053840,0x00e52021,0x00046940,0x01a46023,0x000c1040,0x241900ac,0x244a0034,0x241f0097]
    assert [word(RENDER_START+i*4) for i in range(8)]==expected
    assert word(0x80359B4C)==0xAFB90014
    assert word(0x80359B64)==0xAFB90010
    assert word(TVMODE_A_X)==0x240501c6
    assert word(TVMODE_A_Y)==0x240600dc
    assert word(TVMODE_B_X)==0x240501ce
    assert word(TVMODE_B_Y)==0x240600dc

    put(UP_WRAP,addiu('t9','zero',3)); put(DOWN_LIMIT,addiu('v0','zero',3))
    render=[
        andi('t2','a1',1), sll('t2','t2',8), addiu('t2','t2',100),
        andi('ra','a1',2), sll('t4','ra',7), sll('ra','ra',4), subu('ra','t4','ra'), addiu('ra','ra',0),
    ]
    for i,w in enumerate(render): put(RENDER_START+i*4,w)
    put(0x80359B4C, iop(43,'sp','a3',20))
    # Redraw through row 429 (430*640*2 = 0x86600 bytes). This covers both
    # selector rows but deliberately leaves the stock footer/action overlays alone.
    put(0x80359AFC, iop(15,'zero','a2',0x0008))
    put(0x80359B00, iop(13,'a2','a2',0x6600))
    put(0x80359B04, rtype('t1','zero','a0',0,0x21))
    put(0x80359B0C, rtype('t3','zero','a1',0,0x21))
    put(0x80359B64, iop(43,'sp','a3',16))
    put(NTSC_X, addiu('a1','zero',125))
    put(NTSC_Y, addiu('a2','zero',297))
    # TV mode text is also redrawn from the TV-change handler. Preserve the
    # stock 8-pixel relative centering difference while applying the same
    # relocation delta used by the setup-entry path.
    put(TVMODE_A_X, addiu('a1','zero',133))
    put(TVMODE_A_Y, addiu('a2','zero',297))
    put(TVMODE_B_X, addiu('a1','zero',141))
    put(TVMODE_B_Y, addiu('a2','zero',297))

    stub=build_stub(); caveoff=CAVE-BASE
    assert CAVE+len(stub)<CAVE_LIMIT
    assert fw[caveoff:caveoff+len(stub)]==b'\0'*len(stub)
    fw[caveoff:caveoff+len(stub)]=stub
    put(DISPATCH,j(CAVE))
    crc=crc32_mpeg2(fw[0x200:]); struct.pack_into('<I',fw,0x18c,crc)

    screens={n:build_screen(ui[n],ui['qasf.bel'],n) for n in LABEL_X}
    readme=f"""XGO GAME-LIST TEST05b — POLISHED EXPLICIT REFRESH MENU (UI-ONLY STUB)

PURPOSE
-------
Correct the Test05 hardware UI defects while keeping the fourth command completely write-free.

Protected base: Audio OSD v8
firmware SHA-256 {V8_FW_SHA}

VISIBLE USER MENU
-----------------
0 User Games
1 Language
2 TV System
3 Refresh

The stock 3-column setup layout is rearranged into a 2x2 layout. The selector
keeps the stock 172x172 highlight footprint but now wraps 0..3.

ROW 3 IS DELIBERATELY A NO-OP STUB.
Selecting REFRESH stays on User Menu and performs NO file/catalog writes.
This isolates renderer/navigation/dispatch safety before attaching the proven
Test04 runtime writer and the real scanner/stable-merge engine.

HARDWARE GATE
-------------
1. Install on the disposable test clone.
2. Open User Menu: four visible options must appear in the raised 2x2 layout.
3. Navigate repeatedly in both directions; wrap must be 0<->3 and exactly one selector border/A badge should remain visible.
4. Select User Games: stock User Games behavior must remain unchanged.
5. Select Language: stock language UI/change behavior must remain unchanged.
6. Select TV System only if safe for the current display setup; otherwise confirm navigation/selection only.
7. Confirm both NTSC and PAL remain inside the relocated TV tile before and after changing the setting.
8. Select Refresh several times: it must remain on User Menu and MUST NOT change any game count/catalog.
8. Confirm SFC count remains whatever it was before Test05; no XGO list mutation is expected from REFRESH.
9. Reboot and repeat navigation.

NOTE
----
The fourth label is intentionally the universal ASCII word Refresh in all six
localized setup bitmaps for this UI proof. Existing three labels remain their
OEM localized raster glyphs. Final polish can localize the new label after the
fourth-command mechanics are hardware-confirmed.

Firmware cave: 0x{CAVE:08x}
stub bytes: {len(stub)}
stub SHA-256: {sha(stub)}
LCFG CRC-32/MPEG-2: 0x{crc:08x}
Candidate firmware SHA-256: {sha(fw)}
""".encode()
    with zipfile.ZipFile(args.output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        z.writestr(zi('README-HARDWARE-TEST.txt'),readme)
        z.writestr(zi('bios/bisrv.asd'),bytes(fw))
        for n,b in screens.items(): z.writestr(zi('Resources/'+n),b)
    print('stub',len(stub),sha(stub)); print('firmware',sha(fw));
    for n,b in screens.items(): print(n,sha(b))
    print('zip',args.output.stat().st_size,sha(args.output.read_bytes()))
if __name__=='__main__': main()
