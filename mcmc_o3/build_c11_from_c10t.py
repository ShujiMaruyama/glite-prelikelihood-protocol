#!/usr/bin/env python3
import argparse, hashlib, json, math
from pathlib import Path
import numpy as np
import yaml

SAMPLED = ['q_H','omega_b','omega_dm','logA','n_s','tau_reio','Omega_scf','rims_alpha_U','rims_shell_u_i','A_planck']
HEADLINE = list(SAMPLED)
BURN = 0.30
SHRINK_CANDIDATES = [0.15,0.20,0.25,0.30,0.35,0.40]
MIN_CORR_EIG = 0.10
MAX_CORR_COND = 25.0
SOURCE_RUN_ID = 37248887077
SOURCE_ARTIFACT_ID = 11321815241
SOURCE_ARTIFACT_DIGEST = 'sha256:5ebb566f5f816ece598ee27072dd5b3a341922a52820136069cddc404027650a'
SOURCE_HEAD_SHA = 'ddf304a61f84fec9a32be82aab1d430897a41018'
OLD_SCALE = 3.4


def target_view(d):
    keep = ['prior','value','min','max','derived']
    return {
        'likelihood': d['likelihood'],
        'theory': d['theory'],
        'params': {
            k: ({x: v[x] for x in keep if x in v} if isinstance(v, dict) else v)
            for k, v in d['params'].items()
        },
    }


def read_chain(path):
    first = path.read_text().splitlines()[0]
    assert first.startswith('#')
    names = first[1:].split()
    a = np.loadtxt(path)
    if a.ndim == 1:
        a = a[None, :]
    assert a.shape[1] == len(names), (path, a.shape, len(names))
    return names, a


def reconstruct_postburn(a, names, burn=BURN):
    wi = names.index('weight')
    w = np.rint(a[:, wi]).astype(int)
    assert np.all(w >= 1)
    assert np.max(np.abs(a[:, wi] - w)) < 1e-8
    full = np.repeat(a, w, axis=0)
    cut = int(math.floor(burn * len(full)))
    return full[cut:], int(cut), int(len(full))


def corr_stats(C):
    C = 0.5*(C+C.T)
    sd = np.sqrt(np.diag(C))
    Corr = C / np.outer(sd, sd)
    Corr = 0.5*(Corr+Corr.T)
    eig = np.linalg.eigvalsh(Corr)
    mn, mx = float(eig.min()), float(eig.max())
    return sd, Corr, mn, mx, float(mx/mn)


def write_cov(path, params, C):
    with path.open('w') as f:
        f.write('# ' + ' '.join(params) + '\n')
        np.savetxt(f, C, fmt='%.18e')


def generalized_eigs(A, B):
    eb, vb = np.linalg.eigh(0.5*(B+B.T))
    if np.any(eb <= 0):
        raise RuntimeError('reference covariance is not positive definite')
    Binvhalf = vb @ np.diag(1.0/np.sqrt(eb)) @ vb.T
    W = Binvhalf @ (0.5*(A+A.T)) @ Binvhalf
    return np.linalg.eigvalsh(0.5*(W+W.T))


def getdist_repaired(src, reconstructed, names):
    try:
        from getdist import loadMCSamples
        gd = src / '_getdist_reconstructed'
        gd.mkdir(exist_ok=True)
        root = gd / 'rims_c10t_reconstructed'
        for ci, full in enumerate(reconstructed, start=1):
            np.savetxt(str(root)+f'.{ci}.txt', full, fmt='%.12g')
        param_names = names[2:]
        derived = set(param_names) - set(SAMPLED)
        with Path(str(root)+'.paramnames').open('w') as f:
            for n in param_names:
                key = n + ('*' if n in derived else '')
                f.write(f'{key} {n}\n')
        s = loadMCSamples(str(root), settings={'ignore_rows': 0.0})
        gd_r = float(s.getGelmanRubin())
        ess = {}
        for n in HEADLINE:
            if n in s.index:
                ess[n] = float(s.getEffectiveSamples(s.index[n]))
        return {
            'GetDist_Rminus1': gd_r,
            'parameter_ESS': ess,
            'minimum_parameter_ESS': min(ess.values()) if ess else None,
            'error': None,
            'burnin_convention': '30 percent reconstructed-step burn-in applied before GetDist; ignore_rows=0 thereafter'
        }
    except Exception as e:
        return {'error': repr(e)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--c10t-dir', required=True)
    ap.add_argument('--out-dir', required=True)
    args = ap.parse_args()
    src = Path(args.c10t_dir)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    manifest = src / 'SHA256SUMS.txt'
    assert manifest.exists()
    for line in manifest.read_text().splitlines():
        if not line.strip():
            continue
        h, rel = line.split(None, 1)
        rel = rel.strip().lstrip('*').lstrip('./')
        p = src / rel
        assert p.exists(), p
        got = hashlib.sha256(p.read_bytes()).hexdigest()
        assert got == h, (rel, got, h)

    base_yaml = yaml.safe_load((src/'rims_c10t.yaml').read_text())
    original_target = target_view(base_yaml)
    old_cov = np.loadtxt(src/'rims_c10_precond.covmat')

    chain_info = {}
    postburn_param = []
    reconstructed_full_after_burn = []
    rows_total = 0
    weights_total = 0
    names0 = None

    for ci in range(1,5):
        names, a = read_chain(src/f'rims_c10t.{ci}.txt')
        if names0 is None:
            names0 = names
        assert names == names0
        assert all(p in names for p in SAMPLED)
        full_after, cut, nfull = reconstruct_postburn(a, names)
        wi = names.index('weight')
        rows = len(a)
        wsum = int(np.rint(a[:,wi]).sum())
        acc = float(rows/wsum)
        chain_info[str(ci)] = {
            'distinct_rows': int(rows),
            'weight_sum': int(wsum),
            'acceptance': acc,
            'reconstructed_steps_before_burnin': nfull,
            'reconstructed_steps_burned': cut,
            'reconstructed_steps_retained': int(len(full_after)),
        }
        rows_total += rows
        weights_total += wsum
        full_for_gd = full_after.copy()
        full_for_gd[:, wi] = 1.0
        reconstructed_full_after_burn.append(full_for_gd)
        X = np.column_stack([full_after[:, names.index(p)] for p in SAMPLED])
        postburn_param.append(X)

    aggregate_acceptance = float(rows_total/weights_total)

    import arviz as az
    min_draws = min(len(x) for x in postburn_param)
    eq = [x[-min_draws:] for x in postburn_param]
    rank = {}
    for j,p in enumerate(SAMPLED):
        arr = np.stack([x[:,j] for x in eq], axis=0)
        rhat = float(np.asarray(az.rhat(arr, method='rank')))
        bulk = float(np.asarray(az.ess(arr, method='bulk')))
        tail = float(np.asarray(az.ess(arr, method='tail', prob=(0.05,0.95))))
        drifts = []
        for x in postburn_param:
            v = x[:,j]
            h = len(v)//2
            sd = float(np.std(v, ddof=1))
            drift = float(abs(np.mean(v[-h:])-np.mean(v[:h]))/sd) if sd > 0 else 0.0
            drifts.append(drift)
        rank[p] = {
            'rank_normalized_Rhat': rhat,
            'bulk_ESS': bulk,
            'tail_ESS': tail,
            'max_abs_half_chain_drift_sigma': max(drifts),
        }

    getdist = getdist_repaired(src, reconstructed_full_after_burn, names0)

    centered = []
    for X in postburn_param:
        centered.append(X - X.mean(axis=0, keepdims=True))
    Z = np.vstack(centered)
    raw_cov = (Z.T @ Z) / float(len(Z))
    raw_cov = 0.5*(raw_cov+raw_cov.T)

    shrink_table = []
    selected = None
    for s in SHRINK_CANDIDATES:
        C = (1.0-s)*raw_cov + s*np.diag(np.diag(raw_cov))
        C = 0.5*(C+C.T)
        sd, corr, mn, mx, cond = corr_stats(C)
        row = {'diagonal_shrinkage': s, 'min_corr_eig': mn, 'max_corr_eig': mx, 'corr_condition': cond}
        shrink_table.append(row)
        if selected is None and mn >= MIN_CORR_EIG and cond <= MAX_CORR_COND:
            selected = (s,C,sd,corr,mn,mx,cond)
    if selected is None:
        raise RuntimeError('no predeclared shrinkage candidate satisfies geometry gate')
    shrink, C11, sd11, corr11, mn11, mx11, cond11 = selected

    old_sd, old_corr, old_mn, old_mx, old_cond = corr_stats(old_cov)
    raw_sd, raw_corr, raw_mn, raw_mx, raw_cond = corr_stats(raw_cov)
    gev_raw_old = generalized_eigs(raw_cov, old_cov)
    gev_c11_old = generalized_eigs(C11, old_cov)
    gev_raw_c11 = generalized_eigs(raw_cov, C11)

    mismatches = []
    for i in range(len(SAMPLED)):
        for j in range(i+1,len(SAMPLED)):
            mismatches.append({
                'pair':[SAMPLED[i],SAMPLED[j]],
                'empirical':float(raw_corr[i,j]),
                'old_proposal':float(old_corr[i,j]),
                'delta':float(raw_corr[i,j]-old_corr[i,j]),
            })
    mismatches.sort(key=lambda d: abs(d['delta']), reverse=True)

    sign_old, logdet_old = np.linalg.slogdet(old_cov)
    sign_new, logdet_new = np.linalg.slogdet(C11)
    assert sign_old > 0 and sign_new > 0
    d = len(SAMPLED)
    matched_scale = float(OLD_SCALE * math.exp((logdet_old-logdet_new)/(2*d)))
    sentinel_scales = sorted(set(round(x,1) for x in [0.85*matched_scale, matched_scale, 1.15*matched_scale]))
    if len(sentinel_scales) != 3:
        raise RuntimeError(sentinel_scales)

    covpath = out/'rims_c11_precond.covmat'
    write_cov(covpath, SAMPLED, C11)

    c11_yaml = json.loads(json.dumps(base_yaml))
    c11_yaml['output'] = 'chains_c11s/rims_c11s'
    m = c11_yaml['sampler']['mcmc']
    m['covmat'] = str(covpath)
    m['learn_proposal'] = False
    m['proposal_scale'] = float(round(matched_scale,1))
    assert target_view(c11_yaml) == original_target
    ypath = out/'rims_exp_shell_c11_preconditioned.yaml'
    ypath.write_text(yaml.safe_dump(c11_yaml, sort_keys=False, allow_unicode=True, width=140))

    worst_rhat = max(rank.items(), key=lambda kv: kv[1]['rank_normalized_Rhat'])
    min_bulk = min(rank.items(), key=lambda kv: kv[1]['bulk_ESS'])
    min_tail = min(rank.items(), key=lambda kv: kv[1]['tail_ESS'])
    worst_drift = max(rank.items(), key=lambda kv: kv[1]['max_abs_half_chain_drift_sigma'])

    meta = {
        'schema':'rims-phaseii-o3-c11-preconditioner-v1',
        'source_run_id':SOURCE_RUN_ID,
        'source_artifact_id':SOURCE_ARTIFACT_ID,
        'source_role':'bounded_nonproduction_rims_transport_pilot',
        'source_use':'proposal-training-only',
        'source_eligible_for_inference':False,
        'target_distribution_changed':False,
        'coordinate_map_changed':False,
        'fresh_chains_required':True,
        'posterior_samples_concatenated_for_inference':False,
        'burnin_fraction':BURN,
        'burnin_definition':'integer-weight reconstructed Markov steps',
        'within_chain_only':True,
        'chain_means_removed_before_pooling':True,
        'selected_diagonal_shrinkage':float(shrink),
        'sampled_parameters':SAMPLED,
        'numeric_contract':{
            'min_corr_eig':mn11,
            'max_corr_eig':mx11,
            'corr_condition':cond11,
            'std':dict(zip(SAMPLED,map(float,sd11))),
        },
        'matched_scale_unrounded':matched_scale,
        'sentinel_scales':sentinel_scales,
        'learn_proposal':False,
        'covmat_sha256':hashlib.sha256(covpath.read_bytes()).hexdigest(),
        'yaml_sha256':hashlib.sha256(ypath.read_bytes()).hexdigest(),
    }
    (out/'rims_c11_precond_meta.json').write_text(json.dumps(meta,indent=2,sort_keys=True))

    audit = {
        'schema':'rims-phaseii-o3-c10u-repaired-audit-and-c11-geometry-v1',
        'source_run_id':SOURCE_RUN_ID,
        'source_artifact_id':SOURCE_ARTIFACT_ID,
        'source_artifact_digest':SOURCE_ARTIFACT_DIGEST,
        'source_head_sha':SOURCE_HEAD_SHA,
        'artifact_internal_manifest_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest(),
        'source_role':'bounded_nonproduction_rims_transport_pilot',
        'source_eligible_for_inference':False,
        'acceptance':{'aggregate':aggregate_acceptance,'chains':chain_info},
        'burnin':{'fraction':BURN,'definition':'integer-weight reconstructed Markov steps','equalized_tail_draws_per_chain':int(min_draws)},
        'GetDist_repaired':getdist,
        'rank_normalized':rank,
        'worst_rank_Rhat':{'parameter':worst_rhat[0],**worst_rhat[1]},
        'minimum_bulk_ESS':{'parameter':min_bulk[0],**min_bulk[1]},
        'minimum_tail_ESS':{'parameter':min_tail[0],**min_tail[1]},
        'worst_half_chain_drift':{'parameter':worst_drift[0],**worst_drift[1]},
        'geometry_mismatch':{
            'old_cov_min_corr_eig':old_mn,
            'old_cov_corr_condition':old_cond,
            'empirical_within_chain_min_corr_eig':raw_mn,
            'empirical_within_chain_corr_condition':raw_cond,
            'empirical_over_old_generalized_eigenvalues':list(map(float,gev_raw_old)),
            'empirical_over_old_anisotropy_ratio':float(gev_raw_old.max()/gev_raw_old.min()),
            'old_to_empirical_std_ratio':dict(zip(SAMPLED,map(float,raw_sd/old_sd))),
            'largest_abs_correlation_mismatches':mismatches[:12],
        },
        'c11_geometry':{
            'target_distribution_changed':False,
            'coordinate_map_changed':False,
            'within_chain_only':True,
            'chain_means_removed_before_pooling':True,
            'shrinkage_candidates':shrink_table,
            'selected_diagonal_shrinkage':float(shrink),
            'min_corr_eig':mn11,
            'max_corr_eig':mx11,
            'corr_condition':cond11,
            'std':dict(zip(SAMPLED,map(float,sd11))),
            'new_over_old_generalized_eigenvalues':list(map(float,gev_c11_old)),
            'empirical_over_new_generalized_eigenvalues':list(map(float,gev_raw_c11)),
            'covmat_sha256':hashlib.sha256(covpath.read_bytes()).hexdigest(),
            'yaml_sha256':hashlib.sha256(ypath.read_bytes()).hexdigest(),
        },
        'c11s_predeclared_sentinel':{
            'matched_scale_unrounded':matched_scale,
            'tested_scales':sentinel_scales,
            'minutes_per_scale':12,
            'four_fresh_MPI_chains_per_scale':True,
            'selection_rule':'choose the lowest tested scale with aggregate acceptance in [0.20,0.50], all four chains in [0.10,0.70], and >=10 distinct accepted rows per chain; otherwise stop',
            'samples_eligible_for_inference':False,
            'automatic_long_run':False,
            'automatic_follow_on':False,
        },
        'production_gate':{'GetDist_Rminus1_lt':0.01,'minimum_headline_ESS_ge':1000.0},
        'claim_boundary':{'production_posterior':False,'Bayes_factor':False,'model_preference':False,'LambdaCDM_competitiveness_verified':False},
    }
    (out/'C10U_REPAIRED_AUDIT_AND_C11_GEOMETRY.json').write_text(json.dumps(audit,indent=2,sort_keys=True))
    print(json.dumps(audit,indent=2,sort_keys=True))

if __name__ == '__main__':
    main()
