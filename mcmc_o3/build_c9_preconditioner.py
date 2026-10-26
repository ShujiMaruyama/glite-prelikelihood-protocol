#!/usr/bin/env python3
import argparse, hashlib, json, platform, sys
from pathlib import Path
import numpy as np, yaml

EXPECTED={
 'scalar':{
   'canonical_cov_sha256':'ad7d9a05b587535d98cbe3b343ea8caade89cc278b62c9b06f6bc88833645689',
   'prefix':'scalar','c8_yaml':'scalar_exp_c8_transport.yaml',
   'sampled':['q_H','omega_b','omega_cdm','logA','n_s','tau_reio','Omega_scf','A_planck'],
 },
 'rims':{
   'canonical_cov_sha256':'95fe973cd854528e61f1ebf74ee9674e1d33d97b2703da8eff4d5c9d0082e8f0',
   'prefix':'rims_exp_shell','c8_yaml':'rims_exp_shell_c8_transport.yaml',
   'sampled':['q_H','omega_b','omega_dm','logA','n_s','tau_reio','Omega_scf','rims_alpha_U','rims_shell_u_i','A_planck'],
 },
}
CANONICAL_DIGITS=8
BURNIN_FRACTION=0.30
DIAGONAL_SHRINKAGE=0.15
CORR_EIGEN_FLOOR=1e-3
MIN_CORR_EIG_GATE=0.10
MAX_CORR_CONDITION_GATE=25.0
SOURCE_RUN=34074123144

def pred_scalar(Om):
    return 68.00781035064747 - 0.48114439376854024*((Om-0.06988961182249204)/0.030640502057554492) - 0.11363064315320584*((Om-0.06988961182249204)/0.030640502057554492)**2

def pred_rims(Om,a,u):
    x=(Om-0.08768051)/0.02541329; y=(a-0.04626285)/0.02051664; z=(u+1.53784825)/0.48203115
    return 68.1447995 -0.678001096*x +0.273304965*y -0.0397724341*z -0.152357637*x*x -0.00426803887*x*y

def qmap(model,H0,Om,a=None,u=None):
    pred=pred_scalar(Om) if model=='scalar' else pred_rims(Om,a,u)
    return np.mod((H0-55.0)/27.0 - (pred-68.0)/27.0,1.0)

def read_chain(path):
    with path.open() as f: names=f.readline().strip()[1:].split()
    a=np.loadtxt(path); a=a[None,:] if a.ndim==1 else a
    return names,a

def wcov(X,w):
    sw=float(w.sum()); assert np.isfinite(sw) and sw>0
    mu=(X*w[:,None]).sum(0)/sw; Y=X-mu
    return mu,(Y*w[:,None]).T@Y/sw

def canonical_digest(C,params,digits=CANONICAL_DIGITS):
    rows=[[format(float(x),f'.{digits}e') for x in row] for row in C]
    payload=json.dumps({'params':list(params),'matrix':rows},sort_keys=True,separators=(',',':')).encode()
    return hashlib.sha256(payload).hexdigest()

def numeric_contract(C,params):
    assert C.shape==(len(params),len(params))
    assert np.all(np.isfinite(C))
    C=0.5*(C+C.T)
    diag=np.diag(C)
    assert np.all(diag>0)
    sd=np.sqrt(diag); Corr=C/np.outer(sd,sd); Corr=0.5*(Corr+Corr.T)
    eig=np.linalg.eigvalsh(Corr)
    mn=float(eig.min()); mx=float(eig.max()); cond=float(mx/mn)
    sym=float(np.max(np.abs(C-C.T)))
    assert mn>=MIN_CORR_EIG_GATE,(mn,MIN_CORR_EIG_GATE)
    assert cond<=MAX_CORR_CONDITION_GATE,(cond,MAX_CORR_CONDITION_GATE)
    return C,{'symmetry_max_abs':sym,'min_corr_eig':mn,'max_corr_eig':mx,'corr_condition':cond,'diag':diag.tolist(),'std':sd.tolist()}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--model',choices=['scalar','rims'],required=True); ap.add_argument('--c7-dir',required=True); ap.add_argument('--repo-mcmc-dir',default='mcmc_o3'); ap.add_argument('--out-dir',required=True); args=ap.parse_args()
    model=args.model; spec=EXPECTED[model]; c7=Path(args.c7_dir); out=Path(args.out_dir); out.mkdir(parents=True,exist_ok=True); repo=Path(args.repo_mcmc_dir)
    lineage=json.loads((c7/'RUN_LINEAGE.json').read_text()); assert int(lineage['continuation_index'])==7; assert lineage['target_distribution_changed'] is False
    sampled=spec['sampled']; covs=[]; ws=[]; pooled=[]; per_chain=[]
    for i in range(1,5):
        names,a=read_chain(c7/'chains'/f"{spec['prefix']}.{i}.txt"); start=int(BURNIN_FRACTION*len(a)); a=a[start:]; w=a[:,0]
        d={n:a[:,names.index(n)] for n in names}
        q=qmap(model,d['H0'],d['Omega_scf'],d.get('rims_alpha_U'),d.get('rims_shell_u_i'))
        X=np.column_stack([q if p=='q_H' else d[p] for p in sampled]); mu,C=wcov(X,w)
        covs.append(C); ws.append(float(w.sum())); pooled.append((X,w)); per_chain.append({'chain':i,'rows_used':int(len(a)),'weight_sum':float(w.sum())})
    W=np.array(ws); C=sum(c*w for c,w in zip(covs,W))/W.sum(); C=(1-DIAGONAL_SHRINKAGE)*C+DIAGONAL_SHRINKAGE*np.diag(np.diag(C)); C=0.5*(C+C.T)
    sd=np.sqrt(np.diag(C)); Corr=C/np.outer(sd,sd); Corr=0.5*(Corr+Corr.T); eig=np.linalg.eigvalsh(Corr)
    floor_applied=bool(float(eig.min())<CORR_EIGEN_FLOOR)
    if floor_applied:
        vals,vecs=np.linalg.eigh(Corr); vals=np.maximum(vals,CORR_EIGEN_FLOOR); Corr=(vecs*vals)@vecs.T; Corr=0.5*(Corr+Corr.T); C=Corr*np.outer(sd,sd); C=0.5*(C+C.T)
    C,contract=numeric_contract(C,sampled)
    canonical=canonical_digest(C,sampled); assert canonical==spec['canonical_cov_sha256'],(canonical,spec['canonical_cov_sha256'])
    covpath=out/f'{model}_c9_precond.covmat'
    with covpath.open('w') as f: f.write('# '+' '.join(sampled)+'\n'); np.savetxt(f,C,fmt='%.18e')
    raw_digest=hashlib.sha256(covpath.read_bytes()).hexdigest()
    X=np.vstack([x for x,w in pooled]); w=np.concatenate([w for x,w in pooled]); pmu,PC=wcov(X,w); psd=np.sqrt(np.diag(PC))
    c8=yaml.safe_load((repo/spec['c8_yaml']).read_text()); c8['output']=f"chains_c9/{'scalar_c9' if model=='scalar' else 'rims_c9'}"
    for p,par in c8['params'].items():
        if isinstance(par,dict) and 'prior' in par and p in sampled:
            scale=float(psd[sampled.index(p)]*(1.5 if p=='q_H' else 1.0)); par['ref']={'dist':'norm','loc':float(pmu[sampled.index(p)]),'scale':scale}
    m=c8['sampler']['mcmc']; m['covmat']=str(covpath); m['learn_proposal']=False; m['proposal_scale']=2.4
    ypath=out/(f'{model}_exp_c9_preconditioned.yaml' if model=='scalar' else 'rims_exp_shell_c9_preconditioned.yaml'); ypath.write_text(yaml.safe_dump(c8,sort_keys=False,allow_unicode=True,width=140))
    meta={'schema':'rims-phaseii-o3-c9-preconditioner-v2','model':model,'source_run':SOURCE_RUN,'source_continuation_index':7,'burnin_fraction':BURNIN_FRACTION,'within_chain_only':True,'diagonal_shrinkage':DIAGONAL_SHRINKAGE,'corr_eigen_floor':CORR_EIGEN_FLOOR,'eigen_floor_applied':floor_applied,'sampled_parameters':sampled,'canonical_digits':CANONICAL_DIGITS,'canonical_cov_sha256':canonical,'raw_cov_sha256_provenance_only':raw_digest,'numeric_contract':contract,'per_chain':per_chain,'pooled_ref_mean':dict(zip(sampled,pmu.tolist())),'pooled_ref_std':dict(zip(sampled,psd.tolist())),'yaml_sha256':hashlib.sha256(ypath.read_bytes()).hexdigest(),'runtime':{'python':sys.version.split()[0],'platform':platform.platform(),'numpy':np.__version__,'pyyaml':getattr(yaml,'__version__','unknown')}}
    (out/f'{model}_c9_precond_meta.json').write_text(json.dumps(meta,indent=2,sort_keys=True)); print(json.dumps(meta,indent=2,sort_keys=True))
if __name__=='__main__': main()
