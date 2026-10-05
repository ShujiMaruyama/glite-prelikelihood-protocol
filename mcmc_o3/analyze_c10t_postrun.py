#!/usr/bin/env python3
import argparse, json, math, tempfile
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.linalg import eigh
import arviz as az

SLOW = ['q_H','omega_b','omega_dm','logA','n_s','tau_reio','Omega_scf','rims_alpha_U','rims_shell_u_i']
FAST = ['A_planck']
SAMPLED = SLOW + FAST


def load_chain(path):
    header = path.open().readline().lstrip('#').split()
    df = pd.read_csv(path, comment='#', sep=r'\s+', header=None, names=header)
    w = np.rint(df['weight'].to_numpy(float)).astype(int)
    if np.max(np.abs(df['weight'].to_numpy(float)-w)) > 1e-8 or np.any(w < 1):
        raise RuntimeError(f'invalid MCMC weights in {path}')
    return header, df, w


def weighted_step_trim(df, w, burn):
    total = int(w.sum()); cut = int(math.floor(burn*total)); skipped = 0; out = []
    for row, wi in zip(df.to_numpy(float), w):
        wi = int(wi)
        if skipped + wi <= cut:
            skipped += wi; continue
        row = row.copy()
        if skipped < cut:
            row[0] = wi - (cut-skipped); skipped = cut
        out.append(row)
    if not out: raise RuntimeError('burn-in removed entire chain')
    return np.asarray(out), total, cut


def rank_ess(arr):
    rhat = float(np.asarray(az.rhat(arr, method='rank')))
    bulk = float(np.asarray(az.ess(arr, method='bulk')))
    try: tail = float(np.asarray(az.ess(arr, method='tail')))
    except TypeError: tail = float(np.asarray(az.ess(arr, method='tail', prob=(0.05,0.95))))
    return rhat, bulk, tail


def drift_sigma(v):
    h = len(v)//2
    if h < 2: return float('nan')
    sd = float(np.std(v, ddof=1))
    return 0.0 if sd == 0 else float(abs(np.mean(v[:h])-np.mean(v[-h:]))/sd)


def synthesize_getdist_root(src, work, burn):
    root = work/'rims_c10t_trimmed'; first_header = None; meta = {}
    for ci in range(1,5):
        header, df, w = load_chain(src/f'rims_c10t.{ci}.txt')
        if first_header is None: first_header = header
        elif header != first_header: raise RuntimeError('chain headers disagree')
        arr,total,cut = weighted_step_trim(df,w,burn)
        np.savetxt(f'{root}.{ci}.txt',arr,fmt='%.12g')
        meta[str(ci)]={'original_weight_sum':total,'weight_burned':cut,'retained_weight_sum':int(np.rint(arr[:,0]).astype(int).sum()),'retained_rows':int(len(arr))}
    with open(f'{root}.paramnames','w') as f:
        for i,n in enumerate(first_header[2:]):
            safe = n if n in SAMPLED else f'd{i:02d}'
            star = '' if n in SAMPLED else '*'
            f.write(f'{safe}{star} {n}\n')
    return root, meta


def proposal_correlation(src,names):
    lines=(src/'rims_c10_precond.covmat').read_text().splitlines(); labels=lines[0].lstrip('#').split(); cov=np.loadtxt(lines[1:])
    idx=[labels.index(n) for n in names]; cov=cov[np.ix_(idx,idx)]; sd=np.sqrt(np.diag(cov))
    return cov/np.outer(sd,sd)


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--artifact-dir',required=True); ap.add_argument('--output',default='C10U_C10T_POSTRUN_AUDIT.json'); ap.add_argument('--burnin',type=float,default=0.30); ap.add_argument('--skip-getdist',action='store_true'); a=ap.parse_args()
    src=Path(a.artifact_dir); burn=a.burnin
    if not (src/'SHA256SUMS.txt').exists(): raise RuntimeError('source artifact has no SHA256SUMS.txt')
    per_chain={}; expanded=[]; rows=0; weights=0; header0=None
    for ci in range(1,5):
        header,df,w=load_chain(src/f'rims_c10t.{ci}.txt')
        if header0 is None: header0=header
        elif header != header0: raise RuntimeError('chain headers disagree')
        arr=np.repeat(df[SAMPLED].to_numpy(float),w,axis=0); cut=int(math.floor(burn*len(arr))); retained=arr[cut:]
        if len(retained)<20: raise RuntimeError(f'too few retained draws in chain {ci}')
        expanded.append(retained); r=len(df); ws=int(w.sum()); rows+=r; weights+=ws
        per_chain[str(ci)]={'rows':int(r),'weight_sum':ws,'acceptance':float(r/ws),'reconstructed_steps':int(len(arr)),'burned_steps':cut,'retained_steps':int(len(retained))}
    min_draws=min(len(x) for x in expanded); eq=np.stack([x[-min_draws:] for x in expanded])
    diag={}
    for j,n in enumerate(SAMPLED):
        rhat,bulk,tail=rank_ess(eq[:,:,j]); dr=[drift_sigma(x[:,j]) for x in expanded]; means=[float(np.mean(x[:,j])) for x in expanded]
        within=float(np.sqrt(np.mean([np.var(x[:,j],ddof=1) for x in expanded]))); sep=float((max(means)-min(means))/within) if within>0 else 0.0
        diag[n]={'rank_normalized_Rhat':rhat,'bulk_ESS':bulk,'tail_ESS':tail,'max_abs_half_chain_drift_sigma':float(np.nanmax(dr)),'per_chain_half_drift_sigma':dr,'per_chain_mean':means,'chain_mean_range_over_within_sd':sep}
    pooled=eq.reshape(-1,len(SAMPLED)); corr=np.corrcoef(pooled,rowvar=False); prop=proposal_correlation(src,SAMPLED)
    cp=[]; mp=[]; dp=[]
    for i in range(len(SAMPLED)):
        for j in range(i+1,len(SAMPLED)):
            cp.append({'a':SAMPLED[i],'b':SAMPLED[j],'posterior_r':float(corr[i,j]),'abs_r':float(abs(corr[i,j]))})
            mp.append({'a':SAMPLED[i],'b':SAMPLED[j],'posterior_r':float(corr[i,j]),'proposal_r':float(prop[i,j]),'difference':float(corr[i,j]-prop[i,j]),'abs_difference':float(abs(corr[i,j]-prop[i,j]))})
            vals=[float(np.corrcoef(eq[k,:,i],eq[k,:,j])[0,1]) for k in range(4)]; dp.append({'a':SAMPLED[i],'b':SAMPLED[j],'per_chain_r':vals,'range':float(max(vals)-min(vals))})
    cp.sort(key=lambda d:d['abs_r'],reverse=True); mp.sort(key=lambda d:d['abs_difference'],reverse=True); dp.sort(key=lambda d:d['range'],reverse=True)
    sx=eq[:,:,:len(SLOW)]; ps=sx.reshape(-1,len(SLOW)); sd=np.std(ps,axis=0,ddof=1); z=sx/sd; means=np.mean(z,axis=1); W=sum(np.cov(c,rowvar=False,ddof=1) for c in z)/4.; B=np.cov(means,rowvar=False,ddof=1); vals,vecs=eigh(B,W+1e-8*np.eye(len(SLOW)))
    modes=[]
    for k in np.argsort(vals)[::-1][:3]:
        v=vecs[:,k]/np.max(np.abs(vecs[:,k])); terms=sorted([{'parameter':n,'coefficient':float(c)} for n,c in zip(SLOW,v)],key=lambda d:abs(d['coefficient']),reverse=True)
        modes.append({'between_within_eigenvalue':float(vals[k]),'terms':terms[:6]})
    gd={'available':False,'error':None}; trim_meta=None
    if not a.skip_getdist:
        from getdist import loadMCSamples
        with tempfile.TemporaryDirectory() as td:
            root,trim_meta=synthesize_getdist_root(src,Path(td),burn); s=loadMCSamples(str(root),settings={'ignore_rows':0}); ess={}
            for n in SAMPLED:
                if n in s.index: ess[n]=float(s.getEffectiveSamples(s.index[n]))
            gd={'available':True,'GetDist_Rminus1':float(s.getGelmanRubin()),'parameter_ESS':ess,'minimum_all_sampled_ESS':min(ess.values()),'minimum_slow_headline_ESS':min(ess[n] for n in SLOW if n in ess),'burnin_basis':'integer-weight step trim before GetDist loading','error':None}
    def worst(group,field,maximize):
        items=[(n,diag[n][field]) for n in group]; n,v=(max(items,key=lambda x:x[1]) if maximize else min(items,key=lambda x:x[1])); return {'parameter':n,'value':float(v)}
    out={'schema':'rims-phaseii-o3-c10u-c10t-postrun-audit-v1','role':'analysis_only_recovery_of_completed_c10t_transport_pilot','source_run_id':37248887077,'source_artifact_id':11321815241,'source_artifact_zip_digest':'sha256:5ebb566f5f816ece598ee27072dd5b3a341922a52820136069cddc404027650a','burnin_fraction':burn,'rows':rows,'weight_sum':weights,'aggregate_acceptance':float(rows/weights),'chains':per_chain,'equalized_reconstructed_draws_per_chain':int(min_draws),'parameter_groups':{'slow_headline':SLOW,'fast_nuisance':FAST},'GetDist':gd,'getdist_trim_metadata':trim_meta,'rank_normalized':diag,'slow_block_summary':{'worst_rank_Rhat':worst(SLOW,'rank_normalized_Rhat',True),'minimum_bulk_ESS':worst(SLOW,'bulk_ESS',False),'minimum_tail_ESS':worst(SLOW,'tail_ESS',False),'worst_half_chain_drift':worst(SLOW,'max_abs_half_chain_drift_sigma',True),'worst_chain_mean_separation':worst(SLOW,'chain_mean_range_over_within_sd',True)},'all_sampled_summary':{'worst_rank_Rhat':worst(SAMPLED,'rank_normalized_Rhat',True),'minimum_bulk_ESS':worst(SAMPLED,'bulk_ESS',False),'minimum_tail_ESS':worst(SAMPLED,'tail_ESS',False),'worst_half_chain_drift':worst(SAMPLED,'max_abs_half_chain_drift_sigma',True)},'top_absolute_posterior_correlations':cp[:15],'top_posterior_vs_proposal_correlation_mismatches':mp[:15],'top_between_chain_correlation_dispersions':dp[:15],'proposal_posterior_correlation_frobenius_mismatch':float(np.linalg.norm(corr-prop,'fro')),'generalized_between_within_modes_slow_block':modes,'interpretation':{'acceptance_problem_resolved':0.20<=float(rows/weights)<=0.50,'single_global_scale_is_sufficient':False,'dominant_issue':'cross-chain nonstationarity and covariance/ridge orientation mismatch rather than raw acceptance','recommended_next_design':'do not extend runtime blindly; predeclare a geometry redesign using block-aware or transformed coordinates trained only from nonproduction chains, then validate on fresh sentinel chains'},'production_gate':{'GetDist_Rminus1_lt':0.01,'minimum_headline_ESS_ge':1000.0,'unchanged':True},'claim_boundary':{'eligible_for_inference':False,'production_posterior':False,'Bayes_factor':False,'model_preference':False,'LambdaCDM_competitiveness_verified':False,'automatic_follow_on_forbidden':True}}
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)); print(json.dumps(out,indent=2,sort_keys=True))

if __name__=='__main__': main()
