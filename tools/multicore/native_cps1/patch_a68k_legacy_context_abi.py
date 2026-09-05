#!/usr/bin/env python3
from pathlib import Path

h=Path("/tmp/cps1/src/cpu/m68000_intf.h")
s=h.read_text()
old=""" struct A68KContext {
	UINT32 d[8], a[8];
	UINT32 isp, srh, ccr, xc, pc, irq, sr;
	INT32 (*IrqCallback) (INT32 nIrq);
	UINT32 ppc;
	INT32 (*ResetCallback)();
	INT32 (*RTECallback)();
	INT32 (*CmpCallback)(UINT32 val, INT32 reg);
	UINT32 sfc, dfc, usp, vbr;
	UINT32 nAsmBank, nCpuVersion;
 };
"""
new=""" struct A68KContext {
	/* Exact register-block ABI used by src/cpu/a68k/mips/a68k.s. */
	UINT32 d[8], a[8];
	UINT32 isp, srh, flags, pc, irq;
	INT32 (*IrqCallback) (INT32 nIrq);
	UINT32 ppc;
	INT32 (*ResetCallback)();
	UINT32 sfc, dfc, usp, vbr;
	UINT32 nCpuVersion, fullpc;
 };
"""
if old not in s: raise SystemExit("A68KContext block not found")
h.write_text(s.replace(old,new,1))

cpp=Path("/tmp/cps1/src/cpu/m68000_intf.cpp")
c=cpp.read_text()

start=c.index("static void UpdateA68KContext()")
end=c.index("#endif", start)
block=c[start:end]
replacement="""static void UpdateA68KContext()
{
	if (M68000_regs.srh & 0x20) {
		M68000_regs.isp = M68000_regs.a[7];
	} else {
		M68000_regs.usp = M68000_regs.a[7];
	}
}

static UINT32 GetA68KSR()
{
	UpdateA68KContext();
	return ((M68000_regs.srh << 8) & 0xFF00) | (M68000_regs.flags & 0x1F);
}

static UINT32 GetA68KISP()
{
	UpdateA68KContext();
	return M68000_regs.isp;
}

static UINT32 GetA68KUSP()
{
	UpdateA68KContext();
	return M68000_regs.usp;
}
"""
c=c[:start]+replacement+c[end:]

c=c.replace("\n\tM68000_regs.nAsmBank = pc >> SEK_BITS;\n","\n")
c=c.replace("\tpsr->RTECallback = A68KRTECallback;\n","")
c=c.replace("\tpsr->CmpCallback = A68KCmpCallback;\n","")
c=c.replace("\t\t\t\tSekRegs[i]->RTECallback = NULL;\n","")
c=c.replace("\t\t\t\tSekRegs[i]->CmpCallback = NULL;\n","")

cpp.write_text(c)

print("patched current FBA wrapper to exact legacy MIPS A68K context ABI")
