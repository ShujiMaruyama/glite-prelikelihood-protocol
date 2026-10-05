#!/usr/bin/env python3
import argparse, hashlib, json, math
from pathlib import Path
import numpy as np
import pandas as pd
import yaml
from scipy.linalg import eigh

BASELINE = ['q_H','omega_b','omega_dm','logA','n_s','tau_reio','Omega_scf','rims_alpha_U','rims_shell_u_i']
DIRECT_H0 = ['H0','omega_b','omega_dm','logA','n_s','tau_reio','Omega_scf','rims_alpha_U','rims_shell_u_i']
H0_PHI = ['H0','omega_b','omega_dm','logA','n_s','tau_reio','Omega_scf','rims_alpha_U','rims_phi_transition']
FAST = 'A_planck'
SHRINK_GRID = [0.15,0.25,0.35,0.50,0.70,0.85]


def load_chain(path):
    names = path.open().readline().lstrip('#').split()
    df = pd.read_csv(path, comment='#', sep=r'\s+', header=None, names=names)
    w = np.rint(df['weight'].to_numpy(float)).astype(int)
    if np.max(np.abs(df['weight'].to_numpy(float)-w)) > 1e-8 or np.any(w < 1):
        raise RuntimeError(f'invalid integer MCMC weights: {path}')
    return df, w


def reconstruct_after_burn(df, w, burn):
    x = df.loc[df.index.repeat(w)].reset_index(drop=True)
    cut = int(math.floor(burn*len(x)))
    return x.iloc[cut:].reset_index(drop=True), len(x), cut


def generalized_between_within(chains, cols):
    n = min(len(x) for x in chains)
    a = np.stack([x.iloc[-n:][cols].to_numpy(float) for x in chains])
    pool = a.reshape(-1,len(cols))
    sd = np.std(pool,axis=0,ddof=1)
    z = a/sd
    means = np.mean(z,axis=1)
    W = sum(np.cov(c,rowvar=False,ddof=1) for c in z)/len(z)
    B = np.cov(means,rowvar=False,ddof=1)
    vals,vecs = eigh(B,W+1e-8*np.eye(len(cols)))
    order=np.argsort(vals)[::-1]
    modes=[]
    for k in order[:3]:
        v=vecs[:,k]/np.max(np.abs(vecs[:,k]))
        terms=sorted([{'parameter':n,'coefficient':float(c)} for n,c in zip(cols,v)],key=lambda d:abs(d['coefficient']),reverse=True)
        modes.append({'eigenvalue':float(vals[k]),'terms':terms[:6]})
    corr=np.corrcoef(pool,rowvar=False)
    eig=np.linalg.eigvalsh(0.5*(corr+corr.T))
    return {'equalized_draws_per_chain':int(n),'max_between_within_eigenvalue':float(vals[order[0]]),'top_modes':modes,'pooled_correlation_min_eigenvalue':float(eig.min()),'pooled_correlation_condition':float(eig.max()/eig.min())}


def shrink_cov(X,s):
    C=np.cov(X,rowvar=False,ddof=0)
    C=(1-s)*C+s*np.diag(np.diag(C))
    return 0.5*(C+C.T)


def generalized_condition(Cv,Ct):
    eps=1e-12*max(float(np.trace(Ct))/len(Ct),1.0)
    vals=eigh(Cv+eps*np.eye(len(Cv)),Ct+eps*np.eye(len(Ct)),eigvals_only=True)
    vals=np.maximum(vals,1e-14)
    return {'min_generalized_eigenvalue':float(vals.min()),'max_generalized_eigenvalue':float(vals.max()),'generalized_condition':float(vals.max()/vals.min()),'max_abs_log_eigenvalue':float(np.max(np.abs(np.log(vals))))}


def loo_cv(chains,cols):
    out={}
    for s in SHRINK_GRID:
        held=[]
        for h in range(len(chains)):
            train=np.vstack([chains[i][cols].to_numpy(float) for i in range(len(chains)) if i!=h])
            valid=chains[h][cols].to_numpy(float)
            held.append({'held_out_chain':h+1,**generalized_condition(shrink_cov(valid,s),shrink_cov(train,s))})
        worst=max(x['generalized_condition'] for x in held)
        full=shrink_cov(np.vstack([x[cols].to_numpy(float) for x in chains]),s)
        sd=np.sqrt(np.diag(full)); R=full/np.outer(sd,sd); ev=np.linalg.eigvalsh(0.5*(R+R.T))
        out[f'{s:.2f}']={'shrinkage':s,'heldout':held,'worst_heldout_generalized_condition':float(worst),'full_correlation_min_eigenvalue':float(ev.min()),'full_correlation_condition':float(ev.max()/ev.min()),'passes':bool(worst<=25.0 and ev.min()>=0.10 and ev.max()/ev.min()<=25.0)}
    selected=None
    for s in SHRINK_GRID:
        if out[f'{s:.2f}']['passes']:
            selected=s; break
    return out,selected


def equivalence_audit(y):
    p=y['params']; q=p['q_H']; H=p['H0']
    refs=[]
    for name,spec in p.items():
        if name=='H0' or not isinstance(spec,dict): continue
        for key in ('value','derived'):
            v=spec.get(key)
            if isinstance(v,str) and 'q_H' in v: refs.append({'parameter':name,'field':key})
    theory_text=yaml.safe_dump(y.get('theory',{}),sort_keys=True)
    like_text=yaml.safe_dump(y.get('likelihood',{}),sort_keys=True)
    checks={
      'qH_uniform_0_1': q.get('prior')=={'min':0.0,'max':1.0},
      'qH_periodic_true': q.get('periodic') is True,
      'qH_drop_true': q.get('drop') is True,
      'H0_bounds_55_82': H.get('min')==55.0 and H.get('max')==82.0,
      'H0_formula_has_measure_preserving_mod_map': isinstance(H.get('value'),str) and '55.0 + 27.0*np.mod(q_H' in H['value'],
      'no_other_param_value_or_derived_depends_on_qH': len(refs)==0,
      'theory_block_does_not_reference_qH': 'q_H' not in theory_text,
      'likelihood_block_does_not_reference_qH': 'q_H' not in like_text,
    }
    passed=all(checks.values())
    return {'checks':checks,'unexpected_qH_dependencies':refs,'passed':passed,'measure_argument':'For fixed remaining sampled parameters, q_H -> mod(q_H+g,1) is a measure-preserving bijection almost everywhere on the unit circle. H0=55+27*t therefore has uniform density on [55,82] with constant |dH0/dq_H|=27. Replacing sampled q_H~Uniform(0,1) by sampled H0~Uniform(55,82) preserves the target measure if the dependency checks pass.'}


def write_cov(path,C,names):
    with path.open('w') as f:
        f.write('# '+' '.join(names)+'\n'); np.savetxt(f,C,fmt='%.18e')


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--artifact-dir',required=True); ap.add_argument('--contract',required=True); ap.add_argument('--out-dir',required=True); args=ap.parse_args()
    src=Path(args.artifact_dir); out=Path(args.out_dir); out.mkdir(parents=True,exist_ok=True)
    contract=json.loads(Path(args.contract).read_text()); burn=float(contract['covariance_design']['burnin_fraction'])
    y=yaml.safe_load((src/'rims_c10t.updated.yaml').read_text())
    eq=equivalence_audit(y)
    chains=[]; chain_meta=[]
    for i in range(1,5):
        df,w=load_chain(src/f'rims_c10t.{i}.txt'); r,total,cut=reconstruct_after_burn(df,w,burn); chains.append(r); chain_meta.append({'chain':i,'original_reconstructed_steps':total,'burned_steps':cut,'retained_steps':len(r)})
    geometry={
      'baseline_qH_u':generalized_between_within(chains,BASELINE),
      'direct_H0_u':generalized_between_within(chains,DIRECT_H0),
      'direct_H0_phi_transition_diagnostic_only':generalized_between_within(chains,H0_PHI),
    }
    base=geometry['baseline_qH_u']['max_between_within_eigenvalue']; h0=geometry['direct_H0_u']['max_between_within_eigenvalue']; reduction=(base-h0)/base
    cv_base,sel_base=loo_cv(chains,BASELINE); cv_h0,sel_h0=loo_cv(chains,DIRECT_H0)
    direct_h0_eligible=bool(eq['passed'] and reduction>=contract['coordinate_selection_rule']['direct_H0_must_reduce_max_between_within_eigenvalue_by_fraction_ge'] and sel_h0 is not None)
    candidate=None
    if direct_h0_eligible:
        s=float(sel_h0); slowX=np.vstack([x[DIRECT_H0].to_numpy(float) for x in chains]); Cslow=shrink_cov(slowX,s)
        fastX=np.concatenate([x[FAST].to_numpy(float) for x in chains]); vfast=float(np.var(fastX,ddof=0))
        C=np.zeros((10,10)); C[:9,:9]=Cslow; C[9,9]=vfast
        names=DIRECT_H0+[FAST]
        covpath=out/'rims_c10v_H0_blockaware.covmat'; write_cov(covpath,C,names)
        sd=np.sqrt(np.diag(Cslow)); R=Cslow/np.outer(sd,sd); ev=np.linalg.eigvalsh(0.5*(R+R.T))
        candidate={'status':'geometry_candidate_only_not_authorized_for_mcmc','coordinate':'direct_H0_u','selected_shrinkage':s,'slow_fast_block_diagonal':True,'sampled_order':names,'covmat_file':covpath.name,'covmat_sha256':hashlib.sha256(covpath.read_bytes()).hexdigest(),'slow_correlation_min_eigenvalue':float(ev.min()),'slow_correlation_condition':float(ev.max()/ev.min()),'training_means':{n:float(np.mean(slowX[:,j])) for j,n in enumerate(DIRECT_H0)},'training_stds':{n:float(np.std(slowX[:,j],ddof=0)) for j,n in enumerate(DIRECT_H0)},'A_planck_training_mean':float(np.mean(fastX)),'A_planck_training_std':float(np.std(fastX,ddof=0))}
    alpha=y['params']['rims_alpha_U']['prior']; u=y['params']['rims_shell_u_i']['prior']
    phi_audit={'status':'blocked_from_execution_in_c10v','mapping':'phi=4.44-u/(2*alpha_U)','inverse':'u=2*alpha_U*(4.44-phi)','absolute_jacobian_du_dphi':'2*alpha_U','conditional_support':{'phi_min(alpha_U)':f"4.44-{u['max']}/(2*alpha_U)",'phi_max(alpha_U)':f"4.44-{u['min']}/(2*alpha_U)"},'alpha_prior':alpha,'u_prior':u,'reason':'independent flat phi would omit the Jacobian and alpha-dependent support and would change the target distribution'}
    result={'schema':'rims-phaseii-o3-c10v-geometry-redesign-audit-v1','role':contract['role'],'source_c10t_run_id':contract['sources']['c10t_run_id'],'chain_training_metadata':chain_meta,'direct_H0_target_equivalence':eq,'geometry_diagnostics':geometry,'direct_H0_max_between_within_reduction_fraction':float(reduction),'covariance_cross_validation':{'baseline_qH_u':cv_base,'baseline_selected_shrinkage':sel_base,'direct_H0_u':cv_h0,'direct_H0_selected_shrinkage':sel_h0,'rule':contract['covariance_design']['selection_rule']},'phi_transition_target_measure_audit':phi_audit,'selected_candidate':candidate,'decision':{'direct_H0_candidate_eligible_for_future_fresh_sentinel':direct_h0_eligible,'phi_transition_candidate_eligible':False,'new_mcmc_authorized':False,'recommended_next_step':'If direct_H0 is eligible, freeze a separate fresh short sentinel scale sweep using the candidate H0/block-aware covariance. Do not reuse c10t samples for inference and do not start a long run.' if direct_h0_eligible else 'Stop and redesign geometry; no run.'},'production_gate':contract['production_gate'],'claim_boundary':contract['claim_boundary']}
    (out/'C10V_GEOMETRY_REDESIGN_AUDIT.json').write_text(json.dumps(result,indent=2,sort_keys=True))
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=='__main__': main()
