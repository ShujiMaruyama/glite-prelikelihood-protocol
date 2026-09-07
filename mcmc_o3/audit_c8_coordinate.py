from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np


def read_chain(path: Path):
    names = path.open(encoding='utf-8').readline().strip()[1:].split()
    a = np.loadtxt(path)
    if a.ndim == 1:
        a = a[None, :]
    w = np.rint(a[:, 0]).astype(int)
    if np.any(w < 1) or not np.allclose(w, a[:, 0], atol=1e-8, rtol=0):
        raise ValueError(f'non-integer MCMC multiplicity in {path}')
    x = np.repeat(a[:, 2:], w, axis=0)
    return names[2:], x, a


def tau_geyer(x):
    x = np.asarray(x, float)
    n = len(x)
    if n < 4:
        return 1.0
    y = x - x.mean()
    var = np.dot(y, y) / n
    if not np.isfinite(var) or var <= 0:
        return 1.0
    size = 1 << (2*n - 1).bit_length()
    f = np.fft.rfft(y, n=size)
    acov = np.fft.irfft(f*np.conjugate(f), n=size)[:n] / np.arange(n, 0, -1)
    rho = acov / acov[0]
    pairs = []
    k = 1
    while k + 1 < n:
        g = rho[k] + rho[k+1]
        if not np.isfinite(g) or g <= 0:
            break
        pairs.append(float(g))
        k += 2
    for i in range(1, len(pairs)):
        pairs[i] = min(pairs[i], pairs[i-1])
    return float(max(1.0, min(1.0 + 2.0*sum(pairs), n)))


def stats(x):
    x = np.asarray(x, float)
    n = len(x)
    tau = tau_geyer(x)
    h = n // 2
    sd = float(np.std(x, ddof=1)) if n > 1 else 0.0
    drift = float((np.mean(x[-h:]) - np.mean(x[:h])) / sd) if h and sd > 0 else 0.0
    return {
        'n_markov_steps': n,
        'mean': float(np.mean(x)),
        'std': sd,
        'tau_int': tau,
        'acf_ESS': float(n/tau),
        'half_chain_drift_sigma': drift,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', required=True)
    ap.add_argument('--model', required=True, choices=['scalar', 'rims'])
    ap.add_argument('--out', required=True)
    ap.add_argument('--burnin', type=float, default=0.30)
    args = ap.parse_args()

    out = {'schema': 'rims-phaseii-o3-c8-coordinate-audit-v1', 'model': args.model, 'chains': {}}
    pooled = []
    for i in range(1, 5):
        p = Path(f'{args.root}.{i}.txt')
        names, x, raw = read_chain(p)
        cut = int(math.floor(args.burnin * len(x)))
        x = x[cut:]
        idx = {n:j for j,n in enumerate(names)}
        required = ['q_H', 'H0', 'Omega_scf']
        if args.model == 'rims':
            required += ['rims_alpha_U', 'rims_shell_u_i']
        for name in required:
            if name not in idx:
                raise ValueError(f'{name} missing from {p}; columns={names}')
        c = {'distinct_rows': int(raw.shape[0]), 'postburn_markov_steps': int(len(x)), 'parameters': {}}
        for name in required:
            c['parameters'][name] = stats(x[:, idx[name]])
        c['corr_qH_Omega_scf'] = float(np.corrcoef(x[:,idx['q_H']], x[:,idx['Omega_scf']])[0,1])
        c['corr_H0_Omega_scf'] = float(np.corrcoef(x[:,idx['H0']], x[:,idx['Omega_scf']])[0,1])
        if args.model == 'rims':
            c['corr_qH_alpha_U'] = float(np.corrcoef(x[:,idx['q_H']], x[:,idx['rims_alpha_U']])[0,1])
            c['corr_qH_shell_u_i'] = float(np.corrcoef(x[:,idx['q_H']], x[:,idx['rims_shell_u_i']])[0,1])
        out['chains'][str(i)] = c
        pooled.append((names, x))

    omega_taus = [c['parameters']['Omega_scf']['tau_int'] for c in out['chains'].values()]
    q_taus = [c['parameters']['q_H']['tau_int'] for c in out['chains'].values()]
    omega_drifts = [abs(c['parameters']['Omega_scf']['half_chain_drift_sigma']) for c in out['chains'].values()]
    q_drifts = [abs(c['parameters']['q_H']['half_chain_drift_sigma']) for c in out['chains'].values()]
    baseline = 181.23947942455877 if args.model == 'scalar' else 704.9745074680679
    out['summary'] = {
        'worst_chain_Omega_scf_tau': float(max(omega_taus)),
        'worst_chain_q_H_tau': float(max(q_taus)),
        'max_abs_Omega_scf_half_drift_sigma': float(max(omega_drifts)),
        'max_abs_q_H_half_drift_sigma': float(max(q_drifts)),
        'c7_reference_bottleneck_tau': baseline,
        'Omega_scf_transport_speedup_vs_c7_reference': float(baseline/max(omega_taus)),
    }
    Path(args.out).write_text(json.dumps(out, indent=2))
    print(json.dumps(out['summary'], indent=2))


if __name__ == '__main__':
    main()
