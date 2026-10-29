#!/usr/bin/env python3
"""Fail-closed analysis of future C43 telemetry; *not* root or stability certification."""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path
PREFIX='RIMS_C43_NDF_TRACE_V1'
VETO='RIMS_C39_TERMS_V1'
KEYS={
 'BEGIN': {'kind','xini','xfinal'},
 'TRIAL': {'kind','x','accepted','failed','order','iter'},
 'ACCEPT_GATE': {'kind','x','accepted','failed','order'},
 'COMMIT': {'kind','x','accepted','failed','order'},
}

def parse_event(line):
    d={}
    for tok in line.split()[1:]:
        name,sep,value=tok.partition('=')
        if sep!='=' or name in d or not name:raise ValueError('Duplicate/malformed phase key')
        d[name]=value
    kind=d.get('kind')
    if kind not in KEYS or set(d)!=KEYS[kind]:
        raise ValueError('Unknown/partial C43 event: '+repr(d))
    for key,value in list(d.items()):
        if key=='kind':continue
        if key in ('x','xini','xfinal'):
            d[key]=float(value)
            if not math.isfinite(d[key]):raise ValueError('Nonfinite x-coordinate')
        else:
            d[key]=int(value)
            if d[key]<0:raise ValueError('Negative phase counter')
    if kind=='TRIAL' and (d['order']<1 or d['iter']<1):raise ValueError('Invalid trial order/iteration')
    if kind in ('COMMIT','ACCEPT_GATE') and (d['order']<1 or d['accepted']<1):
        raise ValueError('Invalid accepted record')
    return d


def parse(text, *, expected_veto=True):
    events=[];veto=[]
    for line_no,line in enumerate(text.splitlines()):
        if line.startswith(PREFIX+' '):events.append((line_no,parse_event(line)))
        if line.startswith(VETO+' '):
            v={}
            for item in line.split()[1:]:
                k,eq,value=item.partition('=')
                if not eq or k in v:raise ValueError('Malformed C39 source record')
                v[k]=value
            veto.append((line_no,v))
    if expected_veto and len(veto)!=1:
        raise ValueError('Exactly one real original C39 veto record required')
    if not veto:
        return {'status':'NO_NATIVE_VETO_RECORD','certified':False}
    pos,v=veto[0]
    begin=[(i,d) for i,d in events if i<pos and d['kind']=='BEGIN']
    if not begin:raise ValueError('No C43 solver BEGIN before veto')
    start=begin[-1][0]
    scope=[(i,d) for i,d in events if start<=i<pos]
    if not scope or scope[-1][1]['kind']!='TRIAL':
        raise ValueError('Veto must immediately follow the final logged Newton trial phase')
    trial=scope[-1][1]
    v_a=float(v['a']);v_ratio=float(v['ratio']);v_tol=float(v['tolerance'])
    if not (math.isfinite(v_a) and math.isfinite(v_ratio) and math.isfinite(v_tol)
            and 0<v_a<1 and v_ratio < -1e-10 and v_tol==1e-10):
        raise ValueError('Not the original strict RIMS physical veto')
    if not math.isclose(math.exp(trial['x']),v_a,rel_tol=2e-12):
        raise ValueError('Newton candidate loga does not match veto a')
    accepted=[d for _,d in scope if d['kind']=='ACCEPT_GATE']
    committed=[d for _,d in scope if d['kind']=='COMMIT']
    if trial['accepted'] != len(accepted):
        raise ValueError('Final trial accepted counter inconsistent with traced gate events')
    prev=0
    for d in accepted:
        if d['accepted'] != prev+1:raise ValueError('Nonconsecutive ACCEPT_GATE counts')
        prev=d['accepted']
    if len(committed)>len(accepted):raise ValueError('Committed without corresponding accept gate')
    for j,d in enumerate(committed):
        g=accepted[j]
        if d['accepted'] != g['accepted'] or d['x'] != g['x']:
            raise ValueError('COMMIT coordinate/counter differs from accepted gate')
    if any(b['x']>trial['x'] for b in committed):
        raise ValueError('Accepted coordinate beyond failed trial in forward evolution')
    return {
     'schema':'RIMS_C43_NDF15_COMMIT_AWARE_FORENSIC_V1',
     'status':'FAILED_NEWTON_TRIAL_CONFIRMED',
     'veto_ratio':v_ratio,'veto_a':v_a,
     'latest_failed_trial_loga':trial['x'],
     'accepted_gate_count_in_final_evolver':len(accepted),
     'committed_step_count_in_final_evolver':len(committed),
     'accept_gate_without_committed_state_count':len(accepted)-len(committed),
     'last_committed_loga':committed[-1]['x'] if committed else None,
     'last_committed_a':math.exp(committed[-1]['x']) if committed else None,
     'source_lineage_verifiable_only_with_pinned_binary':True,
     'last_committed_background_g_measured':False,
     'same_accepted_trajectory_root_bracket_proved':False,
     'numerical_convergence_proved':False,
     'normalized_background_proved':False,
     'physical_stability_proved':False}


def main():
    p=argparse.ArgumentParser();p.add_argument('--stderr',required=True);p.add_argument('--out',required=True)
    x=p.parse_args();inp=Path(x.stderr);out=Path(x.out)
    if out.exists():raise FileExistsError('Do not overwrite existing audit')
    raw=inp.read_bytes();z=parse(raw.decode('utf-8',errors='strict'))
    z['raw_stderr_sha256']=hashlib.sha256(raw).hexdigest()
    out.write_text(json.dumps(z,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print(z['status'],': no accepted physical stability or convergence claimed')
if __name__=='__main__':main()
