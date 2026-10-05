#!/usr/bin/env python3
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import yaml

ORDER=['H0','omega_b','omega_dm','logA','n_s','tau_reio','Omega_scf','rims_alpha_U','rims_shell_u_i','A_planck']


def load_cov(path):
    lines=Path(path).read_text().splitlines(); names=lines[0].lstrip('#').split(); C=np.loadtxt(lines[1:]); return names,C

def write_cov(path,names,C):
    with Path(path).open('w') as f:
        f.write('# '+' '.join(names)+'\n'); np.savetxt(f,C,fmt='%.18e')

def replace_qH(x):
    if isinstance(x,list): return [replace_qH(v) for v in x]
    if isinstance(x,dict): return {k:replace_qH(v) for k,v in x.items()}
    return 'H0' if x=='q_H' else x

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--c10t-dir',required=True); ap.add_argument('--c10v-dir',required=True); ap.add_argument('--out-dir',required=True); ap.add_argument('--scale',type=float,required=True); ap.add_argument('--tag',required=True); args=ap.parse_args()
    t=Path(args.c10t_dir); v=Path(args.c10v_dir); out=Path(args.out_dir); out.mkdir(parents=True,exist_ok=True)
    audit=json.loads((v/'C10V_GEOMETRY_REDESIGN_AUDIT.json').read_text())
    cand=audit['selected_candidate']; assert cand['coordinate']=='direct_H0_u'; assert cand['selected_shrinkage']==0.7; assert audit['direct_H0_target_equivalence']['passed'] is True
    vn,VC=load_cov(v/cand['covmat_file']); assert vn==ORDER
    on,OC=load_cov(t/'rims_c10_precond.covmat'); assert 'A_planck' in on
    ia=on.index('A_planck'); old_fast_var=float(OC[ia,ia])
    C=VC.copy(); C[:-1,-1]=0.; C[-1,:-1]=0.; C[-1,-1]=old_fast_var
    cov=out/'rims_c10w_H0_blockaware.covmat'; write_cov(cov,ORDER,C)
    d=yaml.safe_load((t/'rims_c10t.updated.yaml').read_text())
    oldH=d['params']['H0']; oldq=d['params']['q_H']; oldfun=eval(oldH['value'],{'np':np})
    assert oldq['prior']=={'min':0.0,'max':1.0} and oldq.get('periodic') is True and oldq.get('drop') is True
    # q_H must not enter any other parameter definition.
    deps=[]
    for n,spec in d['params'].items():
        if n=='H0' or not isinstance(spec,dict): continue
        for k in ('value','derived'):
            if isinstance(spec.get(k),str) and 'q_H' in spec[k]: deps.append((n,k))
    assert not deps,deps
    # Numerical inverse-map audit over deterministic grid. This checks the exact frozen lambda.
    rng=np.random.default_rng(101005)
    maxerr=0.
    for _ in range(200):
        Om=rng.uniform(0.001,0.18); al=rng.uniform(0.0001,0.12); u=rng.uniform(-2.44234703537,1.09861228867); H=rng.uniform(55.,82.)
        phase0=(oldfun(0.0,Om,al,u)-55.)/27.
        q=np.mod((H-55.)/27.-phase0,1.)
        maxerr=max(maxerr,abs(oldfun(q,Om,al,u)-H))
    assert maxerr<1e-10,maxerr
    del d['params']['q_H']
    mean=float(cand['training_means']['H0']); std=float(cand['training_stds']['H0'])
    d['params']['H0']={'prior':{'min':55.0,'max':82.0},'ref':{'dist':'norm','loc':mean,'scale':std},'proposal':std,'latex':'H_0'}
    m=d['sampler']['mcmc']; m['blocking']=replace_qH(m['blocking']); m['covmat']=str(cov); m['learn_proposal']=False; m['proposal_scale']=float(args.scale)
    d['output']=f"sentinel_c10w/rims_c10w_{args.tag}"
    yp=out/f'rims_c10w_{args.tag}.yaml'; yp.write_text(yaml.safe_dump(d,sort_keys=False,allow_unicode=True,width=140))
    meta={'schema':'rims-phaseii-o3-c10w-h0-builder-v1','tag':args.tag,'proposal_scale':float(args.scale),'target_distribution_changed':False,'coordinate_change':'q_H_to_direct_H0','measure_equivalence':'exact_almost_everywhere','numerical_inverse_max_abs_H0_error':maxerr,'slow_shrinkage':0.7,'A_planck_variance_source':'exact c10t-used c10 preconditioner diagonal','A_planck_variance':old_fast_var,'slow_fast_cross_covariance_zero':True,'covmat_sha256':hashlib.sha256(cov.read_bytes()).hexdigest(),'yaml_sha256':hashlib.sha256(yp.read_bytes()).hexdigest(),'fresh_chains_required':True,'previous_samples_concatenated':False,'eligible_for_inference':False}
    (out/f'C10W_BUILD_{args.tag}.json').write_text(json.dumps(meta,indent=2,sort_keys=True)); print(json.dumps(meta,indent=2,sort_keys=True))
if __name__=='__main__': main()
