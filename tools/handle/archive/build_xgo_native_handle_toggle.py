#!/usr/bin/env python3
"""Build an experimental XGO native Setup Handle P1/P2 toggle from exact HW-P1 base.

Conservatively patches known code seams, allocates only audited zero runs, and
ships original fixed-P1 recovery. This is an OFFLINE-VERIFIED hardware TEST,
not a claim of hardware validation.
"""
import hashlib, json, math, struct, zipfile
from pathlib import Path

ROOT=Path('/mnt/data')
BASE_ZIP=ROOT/'XGO_Handle_As_P1_Experimental(1).zip'
RESOURCE_ZIP=ROOT/'XGoAnalisis.zip'
OUTPUT=ROOT/'XGO_Native_Setup_Handle_P1_P2_Toggle_Hardware_Test.zip'
BASE_SHA='8a8cf7a84f7771b0fc116b80521e13d3dfbd5aace73e6053fb7494eaa7d44c4a'
MODE=0x80A39910
GATE=0x80A38664
DISPATCH=0x807DBB70
COORDS=0x80A37F68
STATUS=0x80A37FA4
CONT=0x80359B3C
NORMALIZE_CONT=0x8035D544
FIXED_P1=0x80A398E4
RESTORE=0x80A38F70
BASE=0x80000000
POLY=0x04C11DB7
LANGS=('dxkgi.ctp','itiss.ers','esent.bvs','awusa.tax','vssvc.nec','vidca.bvs')
LABEL_X={
 'dxkgi.ctp': [(35,225),(235,410),(420,620)],
 'itiss.ers': [(40,230),(250,400),(410,620)],
 'esent.bvs': [(35,230),(260,390),(400,620)],
 'awusa.tax': [(20,260),(260,400),(400,620)],
 'vssvc.nec': [(40,220),(240,410),(420,620)],
 'vidca.bvs': [(5,275),(275,400),(390,625)],
}
F={
'A':['01110','10001','10001','11111','10001','10001','10001'],
'D':['11110','10001','10001','10001','10001','10001','11110'],
'E':['11111','10000','10000','11110','10000','10000','11111'],
'F':['11111','10000','10000','11110','10000','10000','10000'],
'H':['10001','10001','10001','11111','10001','10001','10001'],
'L':['10000','10000','10000','10000','10000','10000','11111'],
'N':['10001','11001','10101','10011','10001','10001','10001'],
'P':['11110','10001','10001','11110','10000','10000','10000'],
'R':['11110','10001','10001','11110','10100','10010','10001'],
'S':['01111','10000','10000','01110','00001','00001','11110'],
'T':['11111','00100','00100','00100','00100','00100','00100'],
'U':['10001','10001','10001','10001','10001','10001','01110'],
'1':['00100','01100','00100','00100','00100','00100','01110'],
'2':['01110','10001','00001','00010','00100','01000','11111'],
' ':['00000']*7,
}

def sha(data):return hashlib.sha256(data).hexdigest()
def i(op,rs,rt,imm):return (op<<26)|(rs<<21)|(rt<<16)|(imm&65535)
def r(rs,rt,rd,sh,fun):return (rs<<21)|(rt<<16)|(rd<<11)|(sh<<6)|fun
def j(addr):return 0x08000000|((addr>>2)&0x03ffffff)
def b(op,rs,rt,pc,dest):
 assert (dest-pc-4)%4==0
 delta=(dest-pc-4)//4
 assert -32768<=delta<=32767,(hex(pc),hex(dest),delta)
 return i(op,rs,rt,delta)
def w(data,addr):return struct.unpack_from('<I',data,addr-BASE)[0]
def put(data,addr,value):struct.pack_into('<I',data,addr-BASE,value)
def words(*vals):return struct.pack('<'+'I'*len(vals),*vals)

def crc32mpeg(data):
 table=[]
 for n in range(256):
  c=n<<24
  for _ in range(8):c=((c<<1)^POLY if c&0x80000000 else c<<1)&0xffffffff
  table.append(c)
 c=0xffffffff
 for x in data:c=((c<<8)&0xffffffff)^table[((c>>24)^x)&255]
 return c

def emit_patch(data,addr,orig,repl,records,label):
 assert isinstance(repl,bytes)
 off=addr-BASE
 assert data[off:off+len(orig)]==orig,(label,hex(addr),'baseline mismatch')
 assert len(orig)==len(repl)
 data[off:off+len(repl)]=repl
 records.append(dict(label=label,address=f'{addr:#010x}',size=len(repl),before=orig.hex(),after=repl.hex()))

def pix_get(data,x,y):
 off=(y*640+x)*2
 return data[off]|(data[off+1]<<8)
def pix_set(data,x,y,c=0xffff):
 if not (0<=x<640 and 0<=y<480):return
 off=(y*640+x)*2
 data[off]=c&255;data[off+1]=c>>8

def copy_rect(dst,src,sx,sy,width,height,dx,dy):
 for y in range(height):
  do=((dy+y)*640+dx)*2;so=((sy+y)*640+sx)*2
  dst[do:do+width*2]=src[so:so+width*2]

def is_label(v):
 return (v>>11)>=24 and ((v>>5)&63)>=48 and (v&31)>=24

def move_label(dst,src,x0,x1,cx,y):
 pts=[(x,yy,pix_get(src,x,yy)) for yy in range(315,390) for x in range(x0,x1) if is_label(pix_get(src,x,yy))]
 assert pts
 xlo=min(p[0] for p in pts);xhi=max(p[0] for p in pts)+1;ylo=min(p[1] for p in pts)
 dx=round(cx-(xhi-xlo)/2)
 for x,yy,v in pts:pix_set(dst,dx+x-xlo,y+yy-ylo,v)

def draw_text(dst,text,cx,y,scale=3):
 width=len(text)*6*scale-scale
 x=round(cx-width/2)
 for ch in text:
  for dy,line in enumerate(F[ch]):
   for dx,one in enumerate(line):
    if one=='1':
     for yy in range(scale):
      for xx in range(scale):pix_set(dst,x+dx*scale+xx,y+dy*scale+yy)
  x+=6*scale

def fill_rect(dst,x,y,ww,hh,c):
 for yy in range(y,y+hh):
  for xx in range(x,x+ww):pix_set(dst,xx,yy,c)

def circle_outline(dst,cx,cy,r,thick=3):
 for yy in range(cy-r-thick,cy+r+thick+1):
  for xx in range(cx-r-thick,cx+r+thick+1):
   d=math.hypot(xx-cx,yy-cy)
   if r-thick<=d<=r+thick:pix_set(dst,xx,yy)

def draw_refresh(dst,cx,cy):
 for yy in range(cy-43,cy+44):
  for xx in range(cx-43,cx+44):
   dx=xx-cx;dy=yy-cy;dist=math.hypot(dx,dy)
   if 31<=dist<=37:
    a=math.degrees(math.atan2(dy,dx))%360
    if a<195 or a>212:pix_set(dst,xx,yy)
 for yy in range(cy-33,cy-15):
  for xx in range(cx-42,cx-42+(yy-(cy-33))//2+3):pix_set(dst,xx,yy)
 for yy in range(cy+15,cy+33):
  for xx in range(cx+42-((cy+33-yy)//2+3),cx+42):pix_set(dst,xx,yy)

def draw_handle(dst,cx,cy):
 # Stylized gamepad: D-pad, paired face buttons, and grips.
 for yy in range(cy-31,cy+25):
  for xx in range(cx-63,cx+64):
   nx=abs(xx-cx)/63;ny=abs(yy-cy)/32
   if 0.82<max(nx,ny)<0.98 and nx+ny<1.65:pix_set(dst,xx,yy)
 fill_rect(dst,cx-40,cy-9,30,9,0xffff)
 fill_rect(dst,cx-30,cy-19,9,30,0xffff)
 circle_outline(dst,cx+24,cy-8,7,2)
 circle_outline(dst,cx+42,cy+4,7,2)

def screens(stock):
 blank=stock['qasf.bel']
 result={}
 for name in LANGS:
  src=stock[name]
  assert len(src)==len(blank)==614400
  out=bytearray(blank)
  draw_text(out,'SETUP',320,5,2)
  # Copy the three native icons without resampling.
  for sx,dx in zip((54,240,427),(58,250,442)):
   copy_rect(out,src,sx,153,159,159,dx,30)
  for bounds,cx in zip(LABEL_X[name],(138,330,522)):
   move_label(out,src,*bounds,cx,192)
  blue=pix_get(src,54,153)
  fill_rect(out,250,250,159,159,blue)
  fill_rect(out,442,250,159,159,blue)
  draw_refresh(out,330,328)
  draw_handle(out,522,299)
  draw_text(out,'P1',489,342,3)
  draw_text(out,'P2',555,342,3)
  draw_text(out,'REFRESH',330,416,2)
  draw_text(out,'HANDLE',522,416,2)
  result[name]=bytes(out)
 return result

def build():
 with zipfile.ZipFile(BASE_ZIP) as z:original=z.read('bios/bisrv.asd')
 assert sha(original)==BASE_SHA
 assert len(original)==12768452
 with zipfile.ZipFile(RESOURCE_ZIP) as z:stock={name:z.read('Resources/'+name) for name in ('qasf.bel',)+LANGS}
 firmware=bytearray(original);records=[]
 # Current Refresh completion explicitly jumps into 8 no-op words at A38668.
 # Redirect to their natural successor before installing a gate in that padding.
 assert all(w(original,0x80A38660+4*i)==0 for i in range(10))
 emit_patch(firmware,0x80A38FE0,words(j(0x80A38668)),words(j(0x80A38688)),records,'refresh_jump_over_nops')
 # Conditional gate: default 0 => displaced stock merge, mode1 => HW-positive helper.
 # s2 is safe scratch because the displaced original andi always defines it.
 gate=[
  i(15,0,18,0x80A4),               # lui s2,0x80a4
  i(35,18,18,0x9910),              # lw s2,-0x66f0(s2)
  b(5,18,0,GATE+8,FIXED_P1),       # bne s2,zero,HW-positive helper
  0,
  r(6,20,6,0,0x25),               # or a2,a2,s4 (stock)
  i(12,6,18,0x20),                 # andi s2,a2,0x20 (stock)
  j(NORMALIZE_CONT),
  0,
 ]
 assert len(gate)==8
 emit_patch(firmware,GATE,b'\0'*32,words(*gate),records,'conditional_normalizer_gate')
 emit_patch(firmware,0x8035D53C,words(j(FIXED_P1)),words(j(GATE)),records,'normalizer_entry')
 # New row4 native dispatch; existing row0,1,2,3 and Refresh dispatch preserved.
 dispatcher=[
  i(9,0,8,4),                          # li t0,4
  b(5,3,8,DISPATCH+4,DISPATCH+36),     # bne v1,t0,stock
  0,
  i(15,0,8,0x80a4),                   # lui t0,hi(mode)
  i(35,8,9,0x9910),                   # lw t1,lo(mode)(t0)
  i(14,9,9,1),                        # xori t1,t1,1
  i(43,8,9,0x9910),                   # sw t1,lo(mode)(t0)
  i(9,0,30,1),                        # li fp,1
  j(0x80359ABC),                      # redraw native Setup
  i(9,0,18,1),                        # delay: li s2,1
  j(0x80356BFC),                      # stock other rows
  0,
 ]
 # bne must target index10, i.e. DISPATCH+40 (not +36).
 dispatcher[1]=b(5,3,8,DISPATCH+4,DISPATCH+40)
 assert len(dispatcher)==12 and len(words(*dispatcher))==48
 emit_patch(firmware,DISPATCH,b'\0'*48,words(*dispatcher),records,'native_setup_row4_dispatch')
 emit_patch(firmware,0x80A38618,words(j(0x80356BFC)),words(j(DISPATCH)),records,'native_setup_row4_entry')
 # Keep special Refresh pending 0..7 range. Extend ordinary Setup range 0..4.
 emit_patch(firmware,0x80A389D0,words(i(9,0,25,3)),words(i(9,0,25,4)),records,'setup_previous_wrap')
 emit_patch(firmware,0x80A389F4,words(i(9,0,2,3)),words(i(9,0,2,4)),records,'setup_next_wrap')
 # Native highlight grid: first row columns0,1,2; second row columns1,2.
 # x=52+192*(index-2*(index>=3)); y=20+224*(index>=3).
 coords=[
  i(11,5,31,3),                      # sltiu ra,a1,3
  i(14,31,31,1),                     # xori ra,ra,1 (row)
  r(0,31,12,1,0),                    # sll t4,ra,1
  r(5,12,10,0,0x23),                # subu t2,a1,t4
  r(0,10,12,6,0),                   # sll t4,t2,6
  r(0,10,10,7,0),                   # sll t2,t2,7
  r(10,12,10,0,0x21),               # addu t2,t2,t4
  i(9,10,10,52),                    # addiu t2,t2,52
  r(0,31,12,8,0),                   # sll t4,ra,8 (256*row)
  r(0,31,31,5,0),                   # sll ra,ra,5 (32*row)
  r(12,31,31,0,0x23),              # subu ra,t4,ra (224*row)
  i(9,31,31,20),                   # addiu ra,ra,20
  j(CONT),0,
 ]
 assert len(coords)==14
 emit_patch(firmware,COORDS,b'\0'*56,words(*coords),records,'setup_3x2_highlight_math')
 emit_patch(firmware,0x80359B1C,words(w(original,0x80359B1C),w(original,0x80359B20)),words(j(COORDS),0),records,'setup_highlight_entry')
 # Dynamic mode underline rendered after native Setup compositor, only if
 # Refresh overlay is inactive. Restore all saved regs using existing epilogue.
 p2_offset=(369*640+541)*2
 status=[
  i(15,0,8,0x80a4),                # lui t0,0x80a4
  i(35,8,9,0x9910),               # lw t1,mode(t0)
  i(35,28,4,-5136),               # lw a0,framebuffer(gp)
  i(15,0,10,p2_offset>>16),       # lui t2,hi(p2 offset)
  i(13,10,10,p2_offset&65535),    # ori t2,t2,lo(p2 offset)
  b(4,9,0,STATUS+20,STATUS+32),   # beq t1,zero,p2
  0,
  i(9,10,10,-132),                # mode P1 => shift left 66px
  r(4,10,4,0,0x21),              # addu a0,a0,t2
  i(9,0,11,-1),                  # li t3,0xffff
  i(9,0,12,28),                  # li t4,28px
  i(41,4,11,0),                  # sh t3,0(a0)
  i(41,4,11,1280),               # sh t3,1280(a0)
  i(41,4,11,2560),               # sh t3,2560(a0)
  i(9,4,4,2),                    # addiu a0,a0,2
  i(9,12,12,-1),                 # addiu t4,t4,-1
  b(5,12,0,STATUS+64,STATUS+44), # bne t4,zero,loop
  0,
  j(RESTORE),0,
 ]
 assert len(status)==20
 emit_patch(firmware,STATUS,b'\0'*80,words(*status),records,'native_setup_mode_status_underline')
 # Original beq at A38AB4 goes straight to register restore when no Refresh.
 assert w(original,0x80A38AB4)==0x1120012e
 emit_patch(firmware,0x80A38AB4,words(0x1120012e),words(b(4,9,0,0x80A38AB4,STATUS)),records,'native_setup_status_hook')
 assert w(firmware,MODE)==0,'mode must cold boot P2'
 # Exact HW-P1 helper must remain byte-identical.
 assert firmware[FIXED_P1-BASE:FIXED_P1-BASE+44]==original[FIXED_P1-BASE:FIXED_P1-BASE+44]
 # Preserve critical Refresh, CLASSIC and audio hooks.
 for addr in (0x80A385F0,0x80A38628,0x80A38648,0x80A38688,0x80A389C0,0x80A38A58,0x80A39000,0x807DAB98):
  assert w(firmware,addr)==w(original,addr),(hex(addr),'protected word changed')
 assert len(firmware)==len(original)
 crc=crc32mpeg(firmware[0x200:]);struct.pack_into('<I',firmware,0x18c,crc)
 assert crc32mpeg(firmware[0x200:])==struct.unpack_from('<I',firmware,0x18c)[0]
 assert struct.unpack_from('<I',firmware,0x184)[0]==len(firmware)-0x200
 # Independently enumerate byte changes and ensure only allowed patch ranges.
 allowed={(addr-BASE+i) for addr,n in [(int(q['address'],16),q['size']) for q in records] for i in range(n)}|set(range(0x18c,0x190))
 changed={i for i,(x,y) in enumerate(zip(original,firmware)) if x!=y}
 assert changed<=allowed
 ui=screens(stock)
 manifest=dict(project='XGO A10 Handle Interface Native Setup P1/P2 Toggle',classification='OFFLINE-VERIFIED / HARDWARE-UNTESTED',base_sha256=BASE_SHA,firmware_sha256=sha(firmware),payload_crc32_mpeg2=f'{crc:08x}',mode_address=f'{MODE:#010x}',default_mode='P2',mode_persistence='volatile, resets to P2 at boot',caves=[f'{COORDS:#x}..{STATUS+80-1:#x}',f'{DISPATCH:#x}..{DISPATCH+48-1:#x}',f'{GATE:#x}..{GATE+31:#x}'],patches=records,resources={n:sha(data) for n,data in ui.items()},recovery_firmware_sha256=BASE_SHA)
 readme=f'''XGO NATIVE SETUP HANDLE P1/P2 TOGGLE — EXPERIMENTAL HARDWARE TEST

OFFLINE VERIFIED, NOT YET TESTED ON XGO HARDWARE. USE A DISPOSABLE SD CLONE.

BASE: HW-positive fixed-Handle-P1 firmware SHA-256 {BASE_SHA}
TEST: new firmware SHA-256 {sha(firmware)}

SETUP: five choices in a 3x2 layout:
  User Games / Language / TV System
               REFRESH / HANDLE

HANDLE tile shows P1 and P2. A white underline marks the current mode.
Select HANDLE using built-in controls to toggle assignment.
  P2 (default on every cold boot): built-in P1; Handle P2 (stock routing).
  P1 (optional): built-in P1 + Handle P1; Handle P2 suppressed.

INSTALL (TEST CLONE ONLY):
  1. Back up your SD's six existing Resources files before copying this ZIP.
  2. Copy bios/bisrv.asd and the six Resources/* files onto the TEST SD clone.
  3. DO NOT overwrite other firmware, CLASSIC, audio or game files.
  4. Cold boot; confirm Setup five tiles and underline under P2.
  5. Verify Refresh, CLASSIC, audio OSD, game lists, stock controls.
  6. Test Handle P2, toggle to P1, test Handle P1, toggle back to P2.
  7. Power-cycle; confirm mode resets to P2.

RECOVERY:
  RECOVERY/bios/bisrv.asd is the EXACT hardware-positive fixed-P1 image.
  If test fails, restore that image and YOUR backed-up six Resources files.
  Do not copy the RECOVERY folder wholesale to the SD root.

SAFETY/UNCERTAINTY:
  Offline checks cannot prove hardware boot, executable cave lifetime, display
  framebuffer ownership, or peripheral behavior. This is the next physical test,
  not a proven firmware. There is no persistent configuration in this version.
  Refresh no-op jump redirect skips only eight pre-existing zero instructions.
  No RP2040 responder firmware changes are required.

LCFG payload CRC32/MPEG2: 0x{crc:08x}
'''
 def zi(name):
  x=zipfile.ZipInfo(name,(2026,10,22,6,40,0));x.compress_type=zipfile.ZIP_DEFLATED;x.create_system=3;x.external_attr=0o644<<16;return x
 with zipfile.ZipFile(OUTPUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  z.writestr(zi('bios/bisrv.asd'),firmware)
  for name,data in ui.items():z.writestr(zi('Resources/'+name),data)
  z.writestr(zi('RECOVERY/bios/bisrv.asd'),original)
  z.writestr(zi('PATCH-MANIFEST.json'),json.dumps(manifest,indent=2)+'\n')
  z.writestr(zi('README-HARDWARE-TEST.txt'),readme)
  z.writestr(zi('SOURCE/build_xgo_native_handle_toggle.py'),Path(__file__).read_bytes())
  verifier=ROOT/'verify_xgo_native_handle_toggle.py'
  if verifier.exists():z.writestr(zi('SOURCE/verify_xgo_native_handle_toggle.py'),verifier.read_bytes())
 print('FIRMWARE',sha(firmware),'CRC',hex(crc),'PATCHES',len(records),'CHANGED BYTES',len(changed))
 print('ZIP',OUTPUT,'SIZE',OUTPUT.stat().st_size,'SHA',sha(OUTPUT.read_bytes()))
 for n in LANGS:print('RESOURCE',n,sha(ui[n]))
 return manifest

if __name__=='__main__':build()
