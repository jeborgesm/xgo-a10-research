#!/usr/bin/env python3
import argparse, re

def load(path):
    words=[]; rate=None; inside=False
    with open(path, "r", errors="ignore") as f:
        for line in f:
            if line.startswith("BEGIN XGO_P0"):
                m=re.search(r"rate=(\d+)", line); rate=int(m.group(1)); inside=True; continue
            if line.startswith("END XGO_P0"): break
            if inside and re.fullmatch(r"[0-9a-fA-F]{8}\s*", line):
                words.append(int(line,16))
    if not words or not rate: raise SystemExit("No XGO_P0 capture found")
    samples=[]
    # PIO shift-right/autopush: earliest 2-bit sample reaches low bits first.
    for w in words:
        for n in range(16):
            v=(w>>(2*n))&3
            samples.append((v&1,(v>>1)&1))
    return rate,samples

def runs(samples, chan):
    out=[]; start=0; last=samples[0][chan]
    for i,s in enumerate(samples[1:],1):
        if s[chan]!=last:
            out.append((start,i,last)); start=i; last=s[chan]
    out.append((start,len(samples),last))
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("capture")
    args=ap.parse_args()
    rate,s=load(args.capture)
    print(f"samples={len(s)} rate={rate}Hz duration={len(s)/rate*1000:.3f}ms")
    for chan,name in [(0,"YELLOW/GP26"),(1,"GREEN/GP27")]:
        r=runs(s,chan)
        edges=max(0,len(r)-1)
        lows=[(b-a)*1e6/rate for a,b,v in r if v==0]
        highs=[(b-a)*1e6/rate for a,b,v in r if v==1]
        print(f"{name}: edges={edges} low_runs={len(lows)} high_runs={len(highs)}")
        if lows: print("  low us first20:", " ".join(f"{x:.1f}" for x in lows[:20]))
        if highs: print("  high us first20:", " ".join(f"{x:.1f}" for x in highs[:20]))
    print("\nFirst transitions (time_us yellow green):")
    prev=s[0]
    print(f"{0:10.1f} {prev[0]} {prev[1]}")
    shown=0
    for i,v in enumerate(s[1:],1):
        if v!=prev:
            print(f"{i*1e6/rate:10.1f} {v[0]} {v[1]}")
            prev=v; shown+=1
            if shown>=120: break

if __name__=="__main__": main()
