#!/usr/bin/env python3
"""Rebuild HW-test TV bottom-left placement from exact native-toggle ZIP.
No speculative PAL submenu fix; original P1/P2 underline hook retained.
"""
import hashlib, json, struct, zipfile
from pathlib import Path

FILES = ("dxkgi.ctp","itiss.ers","esent.bvs","awusa.tax","vssvc.nec","vidca.bvs")
EXPECTED_SOURCE = "aa45f549eca9c58aad93b5804aa44b40857c87418cf0d80ccc81e169b5f058a2"
EXPECTED_OUTPUT = "b1d185686ebe2585113944e7fa2fc11e808fd04d1e04a9e1c86447d0bd9bd00e"

def rect(dst,src,sx,sy,w,h,dx,dy):
    for y in range(h):
        dst[((dy+y)*640+dx)*2:((dy+y)*640+dx+w)*2] = src[((sy+y)*640+sx)*2:((sy+y)*640+sx+w)*2]

def rgb(buf,x,y):
    p=(y*640+x)*2
    return buf[p]|(buf[p+1]<<8)

def bright(p):
    return (p>>11)>=24 and ((p>>5)&63)>=48 and (p&31)>=24

def crc32_mpeg2(data):
    table=[]
    for n in range(256):
        c=n<<24
        for _ in range(8):
            c=((c<<1)^0x04C11DB7 if c&0x80000000 else c<<1)&0xffffffff
        table.append(c)
    crc=0xffffffff
    for x in data:
        crc=((crc<<8)&0xffffffff)^table[((crc>>24)^x)&255]
    return crc

def main(native_zip,stock_zip,out_zip):
    native_zip=Path(native_zip);stock_zip=Path(stock_zip);out_zip=Path(out_zip)
    assert hashlib.sha256(native_zip.read_bytes()).hexdigest()==EXPECTED_SOURCE
    with zipfile.ZipFile(native_zip) as z:
        entries={name:z.read(name) for name in z.namelist()}
    with zipfile.ZipFile(stock_zip) as z:
        blank=z.read("Resources/qasf.bel")
    resources={}
    for name in FILES:
        before=entries["Resources/"+name]
        assert len(before)==len(blank)==614400
        buf=bytearray(before)
        rect(buf,blank,442,30,159,159,442,30)
        rect(buf,blank,420,190,200,31,420,190)
        rect(buf,before,442,30,159,159,58,250)
        text=[(x,y,rgb(before,x,y)) for y in range(189,225) for x in range(420,620) if bright(rgb(before,x,y))]
        assert text,name
        lowx=min(p[0] for p in text);width=max(p[0] for p in text)-lowx+1
        lowy=min(p[1] for p in text);newx=round(138-width/2)
        for x,y,pixel in text:
            dx=newx+x-lowx;dy=416+y-lowy
            if 0<=dx<640 and 0<=dy<480:
                pos=(dy*640+dx)*2
                buf[pos:pos+2]=pixel.to_bytes(2,"little")
        resources[name]=bytes(buf)
        entries["Resources/"+name]=resources[name]
    fw=bytearray(entries["bios/bisrv.asd"])
    assert struct.unpack_from("<I",fw,0xA38AB4)[0]==0x1120FD3B
    assert struct.unpack_from("<I",fw,0xA37F68)[0]==0x2CBF0003
    struct.pack_into("<I",fw,0xA37F68,0x2CBF0002) # index2 now second-row col0
    crc=crc32_mpeg2(fw[0x200:])
    struct.pack_into("<I",fw,0x18C,crc)
    entries["bios/bisrv.asd"]=bytes(fw)
    metadata={
      "build":"TV bottom-left placement / native underline restored / PAL diagnostic",
      "source_zip_sha256":EXPECTED_SOURCE,
      "firmware_sha256":hashlib.sha256(fw).hexdigest(),
      "bios_unchanged_from_native_toggle":False,
      "bios_differences_from_native_toggle":[
        "0xA37F68 sltiu ra,a1,2 (was 3): TV selection highlighted on bottom-left",
        "0x18C LCFG CRC32/MPEG2 updated"],
      "crc32_mpeg2":f"{crc:08x}",
      "tv_mode_text":"runtime-drawn at original lower-left position; TV icon moved to that position",
      "underline":"native toggle hook 0x1120FD3B retained",
      "pal_submenu_rendering":"KNOWN HARDWARE FAILURE - NOT FIXED BY THIS TEST",
      "resources":{name:hashlib.sha256(resources[name]).hexdigest() for name in FILES},
    }
    entries["TV-PLACEMENT-DIAGNOSTIC-MANIFEST.json"]=json.dumps(metadata,indent=2).encode()
    entries["README-TV-PLACEMENT-TEST.txt"]=(
      "EXPERIMENTAL TEST: TV icon moved to lower-left where NTSC/PAL status renders.\n"
      "Native underline restored and P1/P2 routing unchanged.\n"
      "PAL Refresh/Handle submenu rendering remains BROKEN; not claimed fixed.\n"
      "Install bios/ and Resources/ on test SD. Keep RECOVERY/ off SD root.\n").encode()
    with zipfile.ZipFile(out_zip,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for name,data in entries.items():z.writestr(name,data)
    with zipfile.ZipFile(out_zip) as z:assert z.testzip() is None
    print("ZIP",hashlib.sha256(out_zip.read_bytes()).hexdigest())
    print("Firmware",metadata["firmware_sha256"])
    print("CRC",metadata["crc32_mpeg2"])

if __name__=="__main__":
    import sys
    if len(sys.argv)!=4:
        raise SystemExit("usage: python build_tv_bottom_left.py native-toggle.zip XGoAnalisis.zip out.zip")
    main(*sys.argv[1:])
