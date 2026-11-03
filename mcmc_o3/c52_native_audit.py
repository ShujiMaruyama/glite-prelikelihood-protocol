#!/usr/bin/env python3
"""C52 source/binary-attested exact-state physical-g auditor.

No CLASS compute or derivative reevaluation. A logged mass on a rejected Newton
candidate is NEVER an accepted-state physical observation. Fail closed.
"""
from __future__ import annotations
import argparse,hashlib,json,math,re,struct,subprocess
from pathlib import Path
import c43_phase_audit as c43

HEAD='RIMS_C43_NDF_TRACE_V1'
COMMIT='RIMS_C45_COMMITTED_STATE_V1'
DERIV='RIMS_C46_DERIV_EVAL_V1'
FROZEN='ed66e920d52e9f7f63c0778c3d1681e732007c99afd5b4ac816160056909f340'
CASE_SHA='9bc753d2dd2843160e43ca9c37e4480d78513ef372ee9618831cc4447da6a284'
FREEZE='0893eb71e09208c2579652d405f54277647f92ce1de33ee8a0e492ce2547cda0'
PIN_BG='08f6bad70c6c479bc5d6946d2a6332263bca47f8a8d7f7dcc87d9c93df681027'
PIN_ND='0d293723510171ae9a732c80da32adb9ee52701f'
UPSTREAM='e85808324f51fc694d12e3ed7439552a3c3f9540'
HEX=re.compile(r'^[+-]?0x[0-9a-f]+(?:\.[0-9a-f]*)?p[+-]?\d+$',re.I)

def sha(raw):return hashlib.sha256(raw).hexdigest()
def fields(line,marker,keys,kind):
    if not line.startswith(marker+' '):raise ValueError('Wrong trace marker')
    out={}
    for part in line[len(marker)+1:].split():
        k,sep,val=part.partition('=')
        if not sep or not k or not val or k in out:raise ValueError('Malformed/duplicate trace field')
        out[k]=val
    if set(out)!=keys or out['kind']!=kind:raise ValueError('Incomplete/mislabelled trace event')
    return out
def double(tok):
    if not HEX.fullmatch(tok):raise ValueError('Nonhex/ambiguous/nonfinite binary64 data')
    f=float.fromhex(tok)
    if not math.isfinite(f):raise ValueError('Nonfinite binary64 data')
    return f
def bits(tok):return struct.pack('>d',double(tok))
def parsed(line,kind):
    if kind=='commit':
        d=fields(line,COMMIT,{'kind','seq','x','n','yhex'},'COMMIT_STATE')
        seq=int(d['seq'])
        if seq<=0:raise ValueError('Invalid accepted sequence')
    else:
        d=fields(line,DERIV,{'kind','x','n','yhex','H','Vpp','rho_idm','phi','ratio'},'DERIV')
        seq=None
    n=int(d['n'])
    ys=d['yhex'].split(',')
    if not 0<n<=1024 or len(ys)!=n:raise ValueError('Incomplete state vector')
    values={k:double(d[k]) for k in ('H','Vpp','rho_idm','phi','ratio')} if kind=='deriv' else {}
    if kind=='deriv' and (values['H']<=0 or values['rho_idm']<0):
        raise ValueError('Unphysical derivative physical field')
    return {'seq':seq,'x':bits(d['x']),'y':tuple(bits(v) for v in ys),
            'n':n,'phys':values,
            'physbits':tuple(bits(d[k]) for k in ('H','Vpp','rho_idm','phi','ratio')) if kind=='deriv' else None}

def audit(stderr,*,alpha=.01,phi_t=-26.51196042031118):
    if alpha!=.01 or phi_t!=-26.51196042031118:
        raise ValueError('Frozen original mass-law input changed')
    parent=c43.parse(stderr)
    lines=stderr.splitlines()
    veto=[i for i,l in enumerate(lines) if l.startswith('RIMS_C39_TERMS_V1 ')]
    if len(veto)!=1:raise ValueError('Missing/duplicated original stability veto')
    begin=[i for i,l in enumerate(lines[:veto[0]]) if l.startswith(HEAD+' kind=BEGIN ')]
    if not begin:raise ValueError('No NDF15 BEGIN before physical veto')
    scope=lines[begin[-1]:veto[0]]
    commits=[(i,parsed(line,'commit')) for i,line in enumerate(scope) if line.startswith(COMMIT+' ')]
    derivs=[(i,parsed(line,'deriv')) for i,line in enumerate(scope) if line.startswith(DERIV+' ')]
    expected=parent['committed_step_count_in_final_evolver']
    if expected!=len(commits):raise ValueError('Missing or extra C45 state snapshot for COMMIT')
    obs=[];unmatched=[];prev=-1
    for count,(ix,commit) in enumerate(commits,1):
        if commit['seq']!=count:raise ValueError('COMMIT sequence missing/out of order')
        candidates=[(i,x) for i,x in derivs if prev<i<ix and
                    x['x']==commit['x'] and x['y']==commit['y'] and x['n']==commit['n']]
        if not candidates:
            unmatched.append(count);prev=ix;continue
        if len({x['physbits'] for _,x in candidates})!=1:
            raise ValueError('Identical state produced inconsistent physical fields')
        d=candidates[-1][1]['phys']
        s=1/(1+math.exp(-2*alpha*(d['phi']-phi_t))) if 2*alpha*(d['phi']-phi_t)>=0 else (
            lambda t: t/(1+t))(math.exp(2*alpha*(d['phi']-phi_t)))
        k=alpha*alpha*(1-s)*(1-3*s)
        computed=(d['Vpp']+3*d['rho_idm']*k)/(d['H']**2)
        if not math.isclose(computed,d['ratio'],rel_tol=8e-11,abs_tol=2e-24):
            raise ValueError('Original source effective-mass decomposition discrepancy')
        g=computed+1e-10
        obs.append({'seq':count,'a':math.exp(struct.unpack('>d',commit['x'])[0]),
           'ratio':d['ratio'],'recomputed_ratio':computed,'g':g,'s':s,
           'beta':alpha*(1-s),'kappa':k,'rho_idm':d['rho_idm'],'H':d['H'],
           'Vpp':d['Vpp']})
        prev=ix
    signs=[[p['seq'],q['seq']] for p,q in zip(obs,obs[1:])
           if q['seq']==p['seq']+1 and p['g']*q['g']<0]
    status=('ACCEPTED_G_NOT_OBSERVED' if not obs else
       'ACCEPTED_SIGN_CHANGE_BRACKET_WITH_SOURCE_ATTESTATION' if signs else
       'ACCEPTED_G_OBSERVED_NO_ROOT_BRACKET')
    return {'schema':'RIMS_C52_EXACT_BINARY64_TERMINAL_DERIV_COMMIT_JOIN_V1',
        'status':status,'accepted_steps':len(commits),'successful_deriv_records':len(derivs),
        'exact_matched_accepted_g':len(obs),'unmeasured_commits':unmatched,
        'accepted_observations':obs,'adjacent_measured_sign_pairs':signs,
        'original_veto_trial_a':parent['veto_a'],
        'last_accepted_coordinate_a':parent['last_committed_a'],
        'C44_baseline_coarse_parity':len(commits)==618 and
           math.isclose(parent['veto_a'],3.945904558535526e-10,rel_tol=1e-8),
        'full_trajectory_noninterference_proven':False,
        'accepted_state_stability_proven':False,'normalized_background_proven':False,
        'numerical_convergence_proven':False,'observational_detection':False,
        'native_CLASS_executed_by_this_auditor':False}

def verify_provenance(p,lock,native,raw,root,binary):
    if not (p.get('rims_enabled')=='yes' and p.get('rims_enforce_stability')=='yes'
        and p.get('rims_stability_tolerance')==1e-10
        and p.get('rims_alpha_U')==.01
        and p.get('rims_phi_transition')==-26.51196042031118
        and p.get('rims_phi_ref')==4.11730971054
        and p.get('rims_require_normalization')=='no'
        and p.get('output')=='' and 'tol_background_integration' not in p):
        raise ValueError('Original frozen RIMS physical parameters were altered')
    input_bytes=(json.dumps(p,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
    if sha(input_bytes)!=FROZEN:raise ValueError('Canonical original input digest mismatch')
    if not(lock.get('original_c39_background_sha256')==PIN_BG and
       lock.get('original_ndf_git_blob_sha1')==PIN_ND and
       lock.get('upstream_commit')==UPSTREAM and
       lock.get('insertion_only') is True and
       lock.get('original_veto_unchanged') is True and
       lock.get('additional_physical_evaluations')==0 and
       lock.get('applied_to_temporary_CLASS_checkout') is True):
        raise ValueError('Required pinned CLASS source chain is unverified')
    if not(native.get('compute_attempts')==1 and native.get('case')=='rims_002'
        and native.get('case_sha256')==CASE_SHA and native.get('freeze_sha256')==FREEZE
        and native.get('native_status')=='ORIGINAL_SHOOTING_VETO'
        and native.get('phase_status')=='FAILED_NEWTON_TRIAL_CONFIRMED'
        and native.get('input_sha256')==FROZEN and native.get('stderr_sha256')==sha(raw)):
        raise ValueError('Not an authentic one-case C44 native-veto receipt')
    root=Path(root).resolve(strict=True);binary=Path(binary).resolve(strict=True)
    if root not in binary.parents:raise ValueError('Binary outside the compiled source tree')
    head=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()
    if head!=UPSTREAM:raise ValueError('Wrong upstream source commit')
    for filename,key in [('source/background.c','background_output_sha256'),
                         ('tools/evolver_ndf15.c','ndf_output_sha256')]:
        if sha((root/filename).read_bytes())!=lock.get(key):
            raise ValueError('Compiled source hash mismatch: '+filename)
    if sha(binary.read_bytes())!=native.get('binary_sha256'):
        raise ValueError('Compiled extension binary hash mismatch')
    return True

def main():
    p=argparse.ArgumentParser()
    for name in ('stderr','input','source-lock','native-receipt','class-source','binary','output'):
        p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():raise FileExistsError('Do not overwrite original native audit')
    raw=a.stderr.read_bytes()
    params=json.loads(a.input.read_text())
    lock=json.loads(a.source_lock.read_text())
    native=json.loads(a.native_receipt.read_text())
    verify_provenance(params,lock,native,raw,a.class_source,a.binary)
    result=audit(raw.decode('utf8','strict'),
                 alpha=params['rims_alpha_U'],phi_t=params['rims_phi_transition'])
    result['input_sha256']=FROZEN
    result['stderr_sha256']=sha(raw)
    result['native_binary_sha256']=native['binary_sha256']
    result['source_attestation_complete']=True
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print('C52',result['status'],result['exact_matched_accepted_g'],'/',result['accepted_steps'])
    if result['exact_matched_accepted_g']==0:raise SystemExit(4)
if __name__=='__main__':main()
