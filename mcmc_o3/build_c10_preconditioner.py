#!/usr/bin/env python3
import argparse, hashlib, json, platform, sys
from pathlib import Path
import numpy as np, yaml

EXPECTED = {
    'scalar': {
        'prefix': 'scalar_c9',
        'yaml': 'scalar_exp_c9_preconditioned.yaml',
        'analysis': 'analysis_scalar_c9p3/mcmc_summary.json',
        'sampled': ['q_H','omega_b','omega_cdm','logA','n_s','tau_reio','Omega_scf','A_planck'],
        'source_rminus1': 0.26682826381933755,
        'source_miness': 30.730743592031278,
        'canonical_cov_sha256': '9ce8b41da3c267d030c20e1d087cfccef976e74911b56bf0e17da2a8d51fba80',
        'internal_manifest_sha256': 'f9a0d8c3dae2682deab7075e5ec65da334c1ade62c373926a44e7c5f93dc4b16',
    },
    'rims': {
        'prefix': 'rims_c9',
        'yaml': 'rims_exp_shell_c9_preconditioned.yaml',
        'analysis': 'analysis_rims_c9p3/mcmc_summary.json',
        'sampled': ['q_H','omega_b','omega_dm','logA','n_s','tau_reio','Omega_scf','rims_alpha_U','rims_shell_u_i','A_planck'],
        'source_rminus1': 0.9534180298700122,
        'source_miness': 14.815454604046044,
        'canonical_cov_sha256': '9a9c9e1a83c4e4c35191ef8ca7a50d5f0ad56ae74695b9937ab26040458559f6',
        'internal_manifest_sha256': 'e703e5b588486e401732f162a1c4112baf44e08d034abadeb7397574cb213388',
    },
}
SOURCE_RUN = 34292919619
BURNIN_FRACTION = 0.30
DIAGONAL_SHRINKAGE = 0.15
CORR_EIGEN_FLOOR = 1e-3
MIN_CORR_EIG_GATE = 0.10
MAX_CORR_CONDITION_GATE = 25.0
CANONICAL_DIGITS = 8


def read_chain(path):
    with path.open() as f:
        names = f.readline().strip()[1:].split()
    a = np.loadtxt(path)
    if a.ndim == 1:
        a = a[None, :]
    return names, a


def wcov(X, w):
    sw = float(w.sum())
    assert np.isfinite(sw) and sw > 0
    mu = (X * w[:, None]).sum(0) / sw
    Y = X - mu
    return mu, (Y * w[:, None]).T @ Y / sw


def canonical_digest(C, params, digits=CANONICAL_DIGITS):
    rows = [[format(float(x), f'.{digits}e') for x in row] for row in C]
    payload = json.dumps({'params': list(params), 'matrix': rows}, sort_keys=True, separators=(',', ':')).encode()
    return hashlib.sha256(payload).hexdigest()


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', choices=['scalar','rims'], required=True)
    ap.add_argument('--c9p3-dir', required=True)
    ap.add_argument('--out-dir', required=True)
    args = ap.parse_args()

    model = args.model
    spec = EXPECTED[model]
    src = Path(args.c9p3_dir)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    manifest = src / 'SHA256SUMS.txt'
    assert manifest.exists()
    assert hashlib.sha256(manifest.read_bytes()).hexdigest() == spec['internal_manifest_sha256']
    summary = json.loads((src / spec['analysis']).read_text())
    assert abs(float(summary['getdist_Rminus1']) - spec['source_rminus1']) < 1e-12
    assert abs(float(summary['minimum_parameter_ESS']) - spec['source_miness']) < 1e-10
    assert summary['production_acceptance'] is False

    sampled = spec['sampled']
    covs, weights, pooled, per_chain = [], [], [], []
    for i in range(1, 5):
        p = src / 'chains_c9' / f"{spec['prefix']}.{i}.txt"
        names, a = read_chain(p)
        assert all(x in names for x in sampled)
        start = int(BURNIN_FRACTION * len(a))
        a = a[start:]
        w = a[:, names.index('weight')]
        X = np.column_stack([a[:, names.index(x)] for x in sampled])
        mu, C = wcov(X, w)
        covs.append(C)
        weights.append(float(w.sum()))
        pooled.append((X, w))
        per_chain.append({'chain': i, 'rows_used': int(len(a)), 'weight_sum': float(w.sum())})

    W = np.asarray(weights)
    C = sum(c * w for c, w in zip(covs, W)) / W.sum()
    C = (1.0 - DIAGONAL_SHRINKAGE) * C + DIAGONAL_SHRINKAGE * np.diag(np.diag(C))
    C = 0.5 * (C + C.T)
    sd = np.sqrt(np.diag(C))
    Corr = C / np.outer(sd, sd)
    Corr = 0.5 * (Corr + Corr.T)
    vals = np.linalg.eigvalsh(Corr)
    floor_applied = bool(float(vals.min()) < CORR_EIGEN_FLOOR)
    if floor_applied:
        vals, vecs = np.linalg.eigh(Corr)
        vals = np.maximum(vals, CORR_EIGEN_FLOOR)
        Corr = (vecs * vals) @ vecs.T
        Corr = 0.5 * (Corr + Corr.T)
        C = Corr * np.outer(sd, sd)
        C = 0.5 * (C + C.T)

    sd = np.sqrt(np.diag(C))
    Corr = C / np.outer(sd, sd)
    eig = np.linalg.eigvalsh(0.5 * (Corr + Corr.T))
    mn, mx = float(eig.min()), float(eig.max())
    cond = float(mx / mn)
    assert mn >= MIN_CORR_EIG_GATE, (mn, MIN_CORR_EIG_GATE)
    assert cond <= MAX_CORR_CONDITION_GATE, (cond, MAX_CORR_CONDITION_GATE)
    canonical = canonical_digest(C, sampled)
    assert canonical == spec['canonical_cov_sha256'], (canonical, spec['canonical_cov_sha256'])

    covpath = out / f'{model}_c10_precond.covmat'
    with covpath.open('w') as f:
        f.write('# ' + ' '.join(sampled) + '\n')
        np.savetxt(f, C, fmt='%.18e')

    X = np.vstack([x for x, _ in pooled])
    w = np.concatenate([w for _, w in pooled])
    pmu, PC = wcov(X, w)
    psd = np.sqrt(np.diag(PC))

    base = yaml.safe_load((src / spec['yaml']).read_text())
    original_target = target_view(base)
    base['output'] = f"chains_c10p0/{'scalar_c10p0' if model == 'scalar' else 'rims_c10p0'}"
    for p, par in base['params'].items():
        if isinstance(par, dict) and 'prior' in par and p in sampled:
            j = sampled.index(p)
            par['ref'] = {'dist': 'norm', 'loc': float(pmu[j]), 'scale': float(psd[j] * (1.5 if p == 'q_H' else 1.0))}
    m = base['sampler']['mcmc']
    m['covmat'] = str(covpath)
    m['learn_proposal'] = False
    m['proposal_scale'] = 2.4
    assert target_view(base) == original_target

    ypath = out / (f'{model}_exp_c10p0_preconditioned.yaml' if model == 'scalar' else 'rims_exp_shell_c10p0_preconditioned.yaml')
    ypath.write_text(yaml.safe_dump(base, sort_keys=False, allow_unicode=True, width=140))

    meta = {
        'schema': 'rims-phaseii-o3-c10-preconditioner-v1',
        'model': model,
        'source_run': SOURCE_RUN,
        'source_role': 'c9p3-training-only',
        'source_production_acceptance': False,
        'target_distribution_changed': False,
        'coordinate_map_changed_from_c9': False,
        'fresh_chains_required': True,
        'c9_samples_concatenated_with_c10': False,
        'burnin_fraction': BURNIN_FRACTION,
        'within_chain_only': True,
        'diagonal_shrinkage': DIAGONAL_SHRINKAGE,
        'corr_eigen_floor': CORR_EIGEN_FLOOR,
        'eigen_floor_applied': floor_applied,
        'sampled_parameters': sampled,
        'proposal_scale': 2.4,
        'learn_proposal': False,
        'canonical_digits': CANONICAL_DIGITS,
        'canonical_cov_sha256': canonical,
        'raw_cov_sha256_provenance_only': hashlib.sha256(covpath.read_bytes()).hexdigest(),
        'numeric_contract': {
            'min_corr_eig': mn,
            'max_corr_eig': mx,
            'corr_condition': cond,
            'std': dict(zip(sampled, map(float, sd))),
        },
        'per_chain': per_chain,
        'pooled_ref_mean': dict(zip(sampled, map(float, pmu))),
        'pooled_ref_std': dict(zip(sampled, map(float, psd))),
        'yaml_sha256': hashlib.sha256(ypath.read_bytes()).hexdigest(),
        'runtime': {'python': sys.version.split()[0], 'platform': platform.platform(), 'numpy': np.__version__, 'pyyaml': getattr(yaml, '__version__', 'unknown')},
    }
    (out / f'{model}_c10_precond_meta.json').write_text(json.dumps(meta, indent=2, sort_keys=True))
    print(json.dumps(meta, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
