#!/usr/bin/env python3
"""C55: read-only C44-frozen-source accepted-state algebraic g reconstruction.

Requires successful terminal derivative+runtime-scalar AUX and accepted COMMIT
telemetry from a future native run. Does not run CLASS, change physics, or
certify stability. Correct CLASS indices tau=0,phi=1,phi_prime=2, n=7.
"""
from __future__ import annotations
import argparse, json, math, hashlib, re, struct
from pathlib import Path
D='RIMS_C46_DERIV_EVAL_V1'
A='RIMS_C54_DERIV_AUX_V1'
C='RIMS_C45_COMMITTED_STATE_V1'
HEX=re.compile(r'^[+-]?0[xX][0-9a-fA-F]+(?:\.[0-9a-fA-F]*)?[pP][+-]?[0-9]+$')
EPS=1e-10
ALPHA=.01
PHI_T=-26.51196042031118
EXPECTED_SHAPE=(0.,0.,0.)
DKEY={'kind','x','n','yhex','H','Vpp','rho_idm','phi','ratio'}
AKEY={'kind','x','V','phi_prime','rho_scf','iphi','iphip','lam','palpha','pA','pB','alpha_U','phi_t','has_dcdm','has_dr','has_fld'}
CKEY={'kind','seq','x','n','yhex'}

def pairs(line,prefix,keys):
    if not line.startswith(prefix+' '):raise ValueError('incorrect record type')
    out={}
    for v in line[len(prefix)+1:].split():
        a,sep,b=v.partition('=')
        if not sep or not a or not b or a in out:raise ValueError('duplicate/malformed trace key')
        out[a]=b
    if set(out)!=keys:raise ValueError('incomplete/extra record fields')
    return out

def fp(x):
    if not HEX.fullmatch(x):raise ValueError('only %a hexadecimal doubles accepted')
    try:v=float.fromhex(x)
    except (ValueError,OverflowError) as err:raise ValueError('out-of-range binary64') from err
    if not math.isfinite(v):raise ValueError('non-finite value')
    return v

def bits(x):return struct.pack('>d',fp(x) if isinstance(x,str) else float(x))

def parse(line,kind):
    if kind=='deriv':
        d=pairs(line,D,DKEY)
        if d['kind']!='DERIV':raise ValueError('DERIV marker mismatch')
        out={k:fp(d[k]) for k in ('H','Vpp','rho_idm','phi','ratio')}
    elif kind=='aux':
        d=pairs(line,A,AKEY)
        if d['kind']!='DERIV_AUX':raise ValueError('AUX marker mismatch')
        out={k:fp(d[k]) for k in ('V','phi_prime','rho_scf','lam','palpha','pA','pB','alpha_U','phi_t')}
        for k in ('iphi','iphip','has_dcdm','has_dr','has_fld'):
            out[k]=int(d[k])
        if any(out[k]!=0 for k in ('has_dcdm','has_dr','has_fld')):
            raise ValueError('Frozen original background is not the two-dynamical-density branch')
        if (out['palpha'],out['pA'],out['pB'])!=EXPECTED_SHAPE:
            raise ValueError('Runtime SCF polynomial shape drifted from frozen original')
        if not 0<out['lam']<1e3:raise ValueError('Invalid runtime shooting-selected SCF lambda')
        if out['alpha_U']!=ALPHA or out['phi_t']!=PHI_T:
            raise ValueError('Runtime RIMS parameters drifted')
    elif kind=='commit':
        d=pairs(line,C,CKEY)
        if d['kind']!='COMMIT_STATE':raise ValueError('COMMIT marker mismatch')
        out={'seq':int(d['seq'])}
        if out['seq']<=0:raise ValueError('bad accepted sequence')
    else:raise ValueError('kind')
    out['x_bits']=bits(d['x'])
    if kind!='aux':
        out['n']=int(d['n']); y=d['yhex'].split(',')
        if not 1<=out['n']<=1024 or len(y)!=out['n']:raise ValueError('vector length')
        out['y_bits']=tuple(bits(e) for e in y)
        out['y']=tuple(fp(e) for e in y)
    return out

def sig(phi,alpha=ALPHA,phi_t=PHI_T):
    z=2*alpha*(phi-phi_t)
    if z>=0:return 1/(1+math.exp(-z))
    e=math.exp(z);return e/(1+e)

def potential(phi,lam=5.):
    return math.exp(-lam*phi)

def recon(der,aux,commit):
    if not (der['x_bits']==aux['x_bits']==commit['x_bits']):
        raise ValueError('same-time exact-bit match required')
    if der['n']!=commit['n'] or len(der['y'])!=len(commit['y']):
        raise ValueError('dimensional mismatch')
    # CLASS original pinned e858083... tau index 0; frozen has_dcdm=has_dr=has_fld=0
    # implies scalar index 1 and scalar derivative index 2; total state length 7.
    # The prior C54 consumer erroneously expected scalar indices 0,1.
    if not (der['n']==7 and aux['iphi']==1 and aux['iphip']==2):
        raise ValueError('unexpected native CLASS C44 integration indices (expected phi=1, phi_prime=2)')
    if der['y_bits'][1]!=bits(der['phi']) or der['y_bits'][2]!=bits(aux['phi_prime']):
        raise ValueError('Derivative y vector does not support physical field log')
    a=math.exp(struct.unpack('>d',der['x_bits'])[0])
    if not (math.isfinite(a) and a>0 and der['H']>0 and der['rho_idm']>=0):
        raise ValueError('invalid physical source')
    phi_e,pp_e=der['y'][1:3]; phi_c,pp_c=commit['y'][1:3]
    lam=aux['lam']
    Ve,Vc=potential(phi_e,lam),potential(phi_c,lam)
    if not math.isclose(aux['V'],Ve,rel_tol=2e-12,abs_tol=0):
        raise ValueError('Potential source mismatch')
    if not math.isclose(der['Vpp'],lam*lam*Ve,rel_tol=2e-12,abs_tol=0):
        raise ValueError('Potential second derivative mismatch')
    rho_scf_e=((pp_e*pp_e/(2*a*a))+Ve)/3
    if not math.isclose(aux['rho_scf'],rho_scf_e,rel_tol=5e-12,abs_tol=0):
        raise ValueError('Scalar density source mismatch')
    se,sc=sig(phi_e),sig(phi_c)
    if not (se>0 and sc>0):raise ValueError('invalid logistic mass')
    idmc=der['rho_idm']*math.sqrt(sc/se)
    drho_scf=((pp_c*pp_c-pp_e*pp_e)/(2*a*a)+(Vc-Ve))/3
    h2c=der['H']**2+(idmc-der['rho_idm'])+drho_scf
    if not (math.isfinite(h2c) and h2c>0):
        raise ValueError('invalid reconstructed Friedmann H^2')
    kc=ALPHA*ALPHA*(1-sc)*(1-3*sc)
    ke=ALPHA*ALPHA*(1-se)*(1-3*se)
    g_eval=(der['Vpp']+3*der['rho_idm']*ke)/(der['H']**2)+EPS
    if not math.isclose(g_eval,der['ratio']+EPS,rel_tol=2e-8,abs_tol=5e-22):
        raise ValueError('Original native source effective mass ratio mismatch')
    g_c=(lam*lam*Vc+3*idmc*kc)/h2c+EPS
    if not math.isfinite(g_c):raise ValueError('non-finite reconstructed accepted g')
    return dict(seq=commit['seq'],a=a,
        last_deriv_exact_state=(der['y_bits']==commit['y_bits']),
        state_difference_components=sum(x!=y for x,y in zip(der['y_bits'],commit['y_bits'])),
        phi_accepted=phi_c,phi_prime_accepted=pp_c,
        H2_accepted_reconstruction=h2c,
        rho_idm_accepted_reconstruction=idmc,
        kappa_accepted=kc,runtime_scf_lambda=lam,
        g_last_successful_derivative=g_eval,
        g_accepted_algebraic_reconstruction=g_c,
        native_scalar_phi_index=1,native_scalar_phi_prime_index=2,native_index_tau=0,
        original_background_functions_called_by_auditor=False,
        direct_native_accepted_g_measured=False,
        rigorous_roundoff_error_enclosure_available=False,
        full_coupled_stability_certified=False)

def audit(stderr: str):
    data=stderr.splitlines(); records=[];der=None;aux=None;prev=-1;miss=[]
    for i,line in enumerate(data):
        if line.startswith(D+' '):der=parse(line,'deriv');aux=None;prev=i
        elif line.startswith(A+' '):
            if der is None or prev!=i-1:raise ValueError('orphan/nonadjacent auxiliary source record')
            aux=parse(line,'aux')
            if der['x_bits']!=aux['x_bits']:raise ValueError('derivative/aux coordinate mismatch')
        elif line.startswith(C+' '):
            c=parse(line,'commit')
            if c['seq']!=len(records)+len(miss)+1:raise ValueError('commit sequence drift')
            if der is None or aux is None or der['x_bits']!=c['x_bits']:
                miss.append(c['seq'])
            else:records.append(recon(der,aux,c))
            der=None;aux=None
    status=('NO_ACCEPTED_STATE_VECTORS' if len(records)+len(miss)==0 else
            'ACCEPTED_ALGEBRAIC_G_RECONSTRUCTED_NOT_NATIVE_VERIFIED' if records else
            'NO_SAME_EPOCH_DERIVATIVE_WITH_AUX')
    return dict(schema='RIMS_C55_CORRECTED_NATIVE_LAYOUT_ALGEBRAIC_G_V1',
        status=status,total_commits=len(records)+len(miss),
        accepted_algebraic_reconstructions=len(records),
        missing_unmatched=miss,records=records,
        native_accepted_g_directly_measured=False,
        solver_trajectory_noninterference_validated=False,
        rigorous_roundoff_sign_certification=False,
        production_observational_detection=False)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--stderr',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    o=p.parse_args()
    if o.output.exists():raise FileExistsError('Refuse overwrite')
    raw=o.stderr.read_bytes()
    result=audit(raw.decode('utf8','strict'))
    result['original_stderr_sha256']=hashlib.sha256(raw).hexdigest()
    o.output.parent.mkdir(parents=True,exist_ok=True)
    o.output.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print(result['status'],'reconstructions',result['accepted_algebraic_reconstructions'],'/',result['total_commits'])
if __name__=='__main__':main()
