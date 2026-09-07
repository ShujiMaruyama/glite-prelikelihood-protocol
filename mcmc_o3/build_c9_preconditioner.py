#!/usr/bin/env python3
import argparse, hashlib, json
from pathlib import Path
import numpy as np, yaml

EXPECTED={
 'scalar':{'cov_sha256':'9b43e765071b134c72e3006013ce252a9e4c2cfd32f6c3b48fbbd04fd1b632c1','prefix':'scalar','c8_yaml':'scalar_exp_c8_transport.yaml'},
 'rims':{'cov_sha256':'939209723b01a1fb3d42d98e66d637b102c4798a0a8755198283956ccccb6613','prefix':'rims_exp_shell','c8_yaml':'rims_exp_shell_c8_transport.yaml'},
}

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
    sw=w.sum(); mu=(X*w[:,None]).sum(0)/sw; Y=X-mu
    return mu,(Y*w[:,None]).T@Y/sw

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--model',choices=['scalar','rims'],required=True); ap.add_argument('--c7-dir',required=True); ap.add_argument('--repo-mcmc-dir',default='mcmc_o3'); ap.add_argument('--out-dir',required=True); args=ap.parse_args()
    model=args.model; spec=EXPECTED[model]; c7=Path(args.c7_dir); out=Path(args.out_dir); out.mkdir(parents=True,exist_ok=True); repo=Path(args.repo_mcmc_dir)
    lineage=json.loads((c7/'RUN_LINEAGE.json').read_text()); assert int(lineage['continuation_index'])==7; assert lineage['target_distribution_changed'] is False
    sampled=['q_H','omega_b','omega_cdm','logA','n_s','tau_reio','Omega_scf','A_planck'] if model=='scalar' else ['q_H','omega_b','omega_dm','logA','n_s','tau_reio','Omega_scf','rims_alpha_U','rims_shell_u_i','A_planck']
    covs=[]; ws=[]; pooled=[]
    for i in range(1,5):
        names,a=read_chain(c7/'chains'/f"{spec['prefix']}.{i}.txt"); a=a[int(0.3*len(a)):]; w=a[:,0]; d={n:a[:,names.index(n)] for n in names}
        q=qmap(model,d['H0'],d['Omega_scf'],d.get('rims_alpha_U'),d.get('rims_shell_u_i'))
        X=np.column_stack([q if p=='q_H' else d[p] for p in sampled]); mu,C=wcov(X,w); covs.append(C); ws.append(w.sum()); pooled.append((X,w))
    W=np.array(ws); C=sum(c*w for c,w in zip(covs,W))/W.sum(); lam=0.15; C=(1-lam)*C+lam*np.diag(np.diag(C))
    sd=np.sqrt(np.diag(C)); Corr=C/np.outer(sd,sd); vals,vecs=np.linalg.eigh(Corr); vals=np.maximum(vals,1e-3); Corr=(vecs*vals)@vecs.T; C=Corr*np.outer(sd,sd)
    covpath=out/f'{model}_c9_precond.covmat'
    with covpath.open('w') as f: f.write('# '+' '.join(sampled)+'\n'); np.savetxt(f,C,fmt='%.18e')
    digest=hashlib.sha256(covpath.read_bytes()).hexdigest(); assert digest==spec['cov_sha256'],(digest,spec['cov_sha256'])
    X=np.vstack([x for x,w in pooled]); w=np.concatenate([w for x,w in pooled]); pmu,PC=wcov(X,w); psd=np.sqrt(np.diag(PC))
    c8=yaml.safe_load((repo/spec['c8_yaml']).read_text()); c8['output']=f"chains_c9/{'scalar_c9' if model=='scalar' else 'rims_c9'}"
    for p,par in c8['params'].items():
        if isinstance(par,dict) and 'prior' in par and p in sampled:
            scale=float(psd[sampled.index(p)]*(1.5 if p=='q_H' else 1.0)); par['ref']={'dist':'norm','loc':float(pmu[sampled.index(p)]),'scale':scale}
    m=c8['sampler']['mcmc']; m['covmat']=str(covpath); m['learn_proposal']=False; m['proposal_scale']=2.4
    ypath=out/(f'{model}_exp_c9_preconditioned.yaml' if model=='scalar' else 'rims_exp_shell_c9_preconditioned.yaml'); ypath.write_text(yaml.safe_dump(c8,sort_keys=False,allow_unicode=True,width=140))
    eig=np.linalg.eigvalsh(C/np.outer(np.sqrt(np.diag(C)),np.sqrt(np.diag(C))))
    meta={'model':model,'source_run':34074123144,'source_continuation_index':7,'burnin_fraction':0.3,'within_chain_only':True,'diagonal_shrinkage':0.15,'corr_eigen_floor':1e-3,'sampled_parameters':sampled,'cov_sha256':digest,'min_corr_eig':float(eig.min()),'pooled_ref_mean':dict(zip(sampled,pmu.tolist())),'pooled_ref_std':dict(zip(sampled,psd.tolist())),'yaml_sha256':hashlib.sha256(ypath.read_bytes()).hexdigest()}
    (out/f'{model}_c9_precond_meta.json').write_text(json.dumps(meta,indent=2)); print(json.dumps(meta,indent=2))
if __name__=='__main__': main()
