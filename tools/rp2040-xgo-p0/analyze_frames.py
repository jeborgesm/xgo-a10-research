#!/usr/bin/env python3
"""Read-only P0 DATA/CLOCK frame diagnostics. Requires no Pico reflashing.

GPIO P0 10 MHz text: BEGIN XGO_P0 rate=..., 8-hex-character words,
END XGO_P0. YELLOW/GP26=CLOCK bit0; GREEN/GP27=DATA bit1;
earliest of 16 2-bit samples in each word occupies the low bits.

WARNING: The host samples first/R0 BEFORE first CLOCK fall. A two-wire
capture DOES NOT observe that host instruction or its decoded button.
P0 harness != current Frankie; adding a probe may affect fragile bus.
"""
import argparse
import csv
import json
import re
from collections import Counter

START=re.compile(r'^BEGIN XGO_P0\b.*\brate=(\d+)')
HEX=re.compile(r'^[0-9a-fA-F]{8}$')

def load(path):
    rate=None; words=[]; end=False
    with open(path,errors='replace') as inp:
        for line in inp:
            line=line.strip()
            m=START.search(line)
            if m:
                if rate is not None: raise ValueError('Multiple BEGIN markers')
                rate=int(m.group(1))
                if not 100000<=rate<=100000000: raise ValueError('Bad sample rate')
                continue
            if line.startswith('END XGO_P0') and rate:
                end=True
                break
            if rate and HEX.fullmatch(line): words.append(int(line,16))
    if not rate or not words: raise ValueError('No P0 words found')
    clock=[];data=[]
    for word in words:
        for j in range(16):
            pair=(word>>(2*j))&3
            clock.append(pair&1)
            data.append((pair>>1)&1)
    return rate,clock,data,end

def runs(data):
    out=[];s=0;old=data[0]
    for j,v in enumerate(data[1:],1):
        if v!=old:
            out.append((s,j,old))
            s=j;old=v
    out.append((s,len(data),old))
    return out

def analyze(rate,clock,data):
    """Group all CLOCK low phases (including 11/13-pulse anomalies).

    A 150us maximum high gap retains one clock-stretch event but separates
    distinct 16ms host scans. This is an analysis heuristic, not protocol law.
    """
    lows=[(s,e) for s,e,v in runs(clock) if v==0]
    data_runs=runs(data)
    data_low=[(s,e) for s,e,v in data_runs if v==0]
    groups=[];group=[]
    gap=round(.000150*rate)
    for pulse in lows:
        if group and pulse[0]-group[-1][1]>gap:
            groups.append(group);group=[]
        group.append(pulse)
    if group: groups.append(group)
    frames=[]
    for pulses in groups:
        if len(pulses)<3:continue
        start=pulses[0][0];end=pulses[-1][1]
        widths=[(b-a)*1e6/rate for a,b in pulses]
        highs=[(pulses[i+1][0]-pulses[i][1])*1e6/rate
               for i in range(len(pulses)-1)]
        possible=[(a,b) for a,b in data_low if
                  a<=start and b>=max(0,start-round(.000300*rate)) and
                  (b-a)*1e6/rate>=2]
        load_start,load_end=possible[-1] if possible else (None,None)
        data_edges=[a for a,b,v in data_runs if start<=a<end]
        r0_line=data[start]  # ONLY electrical value at first clock
        flags=[]
        if len(pulses)!=12: flags.append('NON_12_CLOCKS')
        if max(widths)>18: flags.append('CLOCK_LOW_GT_18US')
        if highs and max(highs)>18: flags.append('CLOCK_HIGH_GT_18US')
        if highs and min(highs)<.5: flags.append('CLOCK_HIGH_LT_0_5US')
        if load_start is None: flags.append('NO_MATCHED_LOAD')
        elif load_end>start: flags.append('LOAD_LOW_AT_FIRST_CLOCK')
        if data_edges: flags.append('DATA_CHANGED_DURING_BURST')
        fmt=lambda x:round(x,3) if x is not None else None
        # DATA proxy after CLOCK rise; not an actual host read.
        proxy=[]
        for i in range(min(11,len(pulses)-1)):
            rise=pulses[i][1]; nextfall=pulses[i+1][0]
            midpoint=(rise+nextfall)//2
            proxy.append(data[midpoint])
        frames.append(dict(
            frame=len(frames),clock_count=len(pulses),
            first_fall_us=fmt(start*1e6/rate),
            last_rise_us=fmt(end*1e6/rate),
            burst_us=fmt((end-start)*1e6/rate),
            low_min_us=fmt(min(widths)),low_max_us=fmt(max(widths)),
            high_min_us=fmt(min(highs)) if highs else None,
            high_max_us=fmt(max(highs)) if highs else None,
            low_widths_us=[fmt(x) for x in widths],
            high_widths_us=[fmt(x) for x in highs],
            load_low_us=fmt((load_end-load_start)*1e6/rate)
                        if load_start is not None else None,
            load_rise_to_first_fall_us=fmt((start-load_end)*1e6/rate)
                        if load_end is not None else None,
            data_at_first_fall=r0_line,
            data_edges_during_burst=len(data_edges),
            after_rise_data_proxy=proxy,flags=flags))
    return frames

LIMITS=[
    'No XGO R0 sample strobe: DATA at first CLOCK fall is not host decoded R.',
    'Host later-slot read timing is unavailable; DATA proxy is not host decode.',
    'Digital threshold readings cannot determine analog DATA rise or PHY loading.',
    'Current Frankie V2 Jr differs electrically from archived P0 loose-wire probe.',
    'Adding another probe can disturb this bus; do not infer passive means zero load.'
]

def report(path,json_path=None,csv_path=None):
    rate,clk,data,complete=load(path)
    frames=analyze(rate,clk,data)
    flags=Counter(x for f in frames for x in f['flags'])
    info=dict(rate_hz=rate,sample_resolution_us=1e6/rate,
              complete_export=complete,duration_ms=round(len(clk)*1e3/rate,3),
              frames=len(frames),clock_low_runs=sum(v==0 for _,_,v in runs(clk)),
              frame_flags=dict(flags),interpretive_limits=LIMITS)
    output=dict(summary=info,frames=frames)
    print(json.dumps(info,indent=2))
    for f in frames:
        print('frame=%d clock=%d load=%s rise_to_clk=%s high_min=%s flags=%s' %
              (f['frame'],f['clock_count'],f['load_low_us'],
               f['load_rise_to_first_fall_us'],f['high_min_us'],
               ','.join(f['flags']) or 'NONE'))
    if json_path:
        with open(json_path,'w') as out:json.dump(output,out,indent=2)
    if csv_path:
        cols=['frame','clock_count','first_fall_us','burst_us','low_min_us',
              'low_max_us','high_min_us','high_max_us','load_low_us',
              'load_rise_to_first_fall_us','data_at_first_fall',
              'data_edges_during_burst','flags']
        with open(csv_path,'w',newline='') as out:
            w=csv.DictWriter(out,fieldnames=cols);w.writeheader()
            for f in frames:
                w.writerow({k:','.join(f[k]) if k=='flags' else f[k] for k in cols})
    return output

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('capture')
    p.add_argument('--json',dest='json_path')
    p.add_argument('--csv',dest='csv_path')
    a=p.parse_args()
    report(a.capture,a.json_path,a.csv_path)
