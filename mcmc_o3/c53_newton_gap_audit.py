#!/usr/bin/env python3
"""C53: report NDF15 final-Newton-evaluation -> accepted-COMMIT state gap.

Source-informed forensic diagnostic, never a surrogate accepted-state g.
Does not call CLASS, update state, or weaken the original stability veto.
"""
from __future__ import annotations
import argparse, hashlib, json, math, struct
from pathlib import Path

C45='RIMS_C45_COMMITTED_STATE_V1'
C46='RIMS_C46_DERIV_EVAL_V1'


def _keyvals(line, prefix, keys):
    if not line.startswith(prefix+' '):
        raise ValueError('wrong marker')
    d={}
    for part in line[len(prefix)+1:].split():
        k,e,v=part.partition('=')
        if not e or not k or not v or k in d:
            raise ValueError('malformed or duplicate telemetry key')
        d[k]=v
    if set(d)!=keys:raise ValueError('missing or extra telemetry keys')
    return d


def _hex64(s):
    if not s.lower().startswith(('0x','-0x','+0x')) or 'p' not in s.lower():
        raise ValueError('must be C hexadecimal binary64')
    try:v=float.fromhex(s)
    except (ValueError,OverflowError) as err:raise ValueError('invalid binary64') from err
    if not math.isfinite(v):raise ValueError('nonfinite state')
    return struct.pack('>d',v)


def _decode(line,kind):
    if kind=='commit':
        d=_keyvals(line,C45,{'kind','seq','x','n','yhex'})
        if d['kind']!='COMMIT_STATE':raise ValueError('wrong COMMIT state kind')
        seq=int(d['seq'])
        if seq<=0:raise ValueError('invalid sequence')
    else:
        d=_keyvals(line,C46,{'kind','x','n','yhex','H','Vpp','rho_idm','phi','ratio'})
        if d['kind']!='DERIV':raise ValueError('wrong DERIV kind')
        seq=None
        for key in ('H','Vpp','rho_idm','phi','ratio'):_hex64(d[key])
    n=int(d['n']); ys=d['yhex'].split(',')
    if not 1<=n<=1024 or len(ys)!=n:raise ValueError('bad vector dimension')
    return dict(seq=seq,n=n,x=_hex64(d['x']),ys=tuple(_hex64(y) for y in ys))


def _float(bits):return struct.unpack('>d',bits)[0]


def classify(stderr: str):
    lines=stderr.splitlines(); commits=[]; der=[]
    for i,line in enumerate(lines):
        if line.startswith(C45+' '):commits.append((i,_decode(line,'commit')))
        if line.startswith(C46+' '):der.append((i,_decode(line,'deriv')))
    if not commits:
        return {'schema':'RIMS_C53_NEWTON_COMMIT_GAP_V1',
            'status':'NO_ACCEPTED_VECTOR_TELEMETRY',
            'accepted_states':0,'last_derivative_input_exact':0,
            'accepted_g_measured_by_this_program':False,
            'certifies_physical_stability':False}
    data=[]; prev=-1
    for i,(line_no,state) in enumerate(commits,1):
        if state['seq']!=i:raise ValueError('nonconsecutive COMMIT sequence')
        cand=[(j,d) for j,d in der if prev<j<line_no and d['x']==state['x'] and d['n']==state['n']]
        if cand:
            input_state=cand[-1][1]
            mismatches=sum(a!=b for a,b in zip(input_state['ys'],state['ys']))
            absmax=max(abs(_float(a)-_float(b)) for a,b in zip(input_state['ys'],state['ys']))
            scaled=max(abs(_float(a)-_float(b))/max(abs(_float(a)),abs(_float(b)),1e-300)
                      for a,b in zip(input_state['ys'],state['ys']))
            result=dict(seq=i,has_precommit_successful_derivative_at_same_x=True,
                last_derivative_input_equal_commit=(mismatches==0),
                mismatching_components=mismatches,max_abs_state_change=absmax,
                max_relative_state_change=scaled)
        else:
            result=dict(seq=i,has_precommit_successful_derivative_at_same_x=False,
                last_derivative_input_equal_commit=None,mismatching_components=None,
                max_abs_state_change=None,max_relative_state_change=None)
        data.append(result);prev=line_no
    unequal=sum(x['last_derivative_input_equal_commit'] is False for x in data)
    equal=sum(x['last_derivative_input_equal_commit'] is True for x in data)
    missing=sum(x['last_derivative_input_equal_commit'] is None for x in data)
    return dict(schema='RIMS_C53_NEWTON_COMMIT_GAP_V1',
        status='SOURCE_GAP_AUDITED_NO_ACCEPTED_G_PROMOTION',
        accepted_states=len(data),last_derivative_input_exact=equal,
        last_derivative_input_unequal=unequal,missing_last_derivative=missing,
        per_step=data,
        accepted_g_measured_by_this_program=False,
        accepted_state_direct_g_requires_separate_replay=True,
        trial_or_derivative_values_are_not_accepted_values=True,
        certified_trajectory_noninterference=False,
        certifies_physical_stability=False)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--stderr',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():raise FileExistsError('No overwriting evidence')
    raw=a.stderr.read_bytes()
    result=classify(raw.decode('utf-8','strict'))
    result['original_stderr_sha256']=hashlib.sha256(raw).hexdigest()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print('C53',result['status'], 'commits',result['accepted_states'])
if __name__=='__main__':main()
