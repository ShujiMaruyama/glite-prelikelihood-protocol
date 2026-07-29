from pathlib import Path
import csv, json

from cobaya.model import get_model

ROOT = Path.cwd()
CLASS = ROOT / 'class_public'
PACKAGES = ROOT / 'cobaya_packages'
SCAN = ROOT / 'scan_artifact'
OUT = ROOT / 'realdata_results'
OUT.mkdir(exist_ok=True)
CSV = SCAN / 'validated_shell_scan.csv'

# Keep all fixed CLASS inputs in extra_args. Strings such as "no"/"yes" must
# not be placed in Cobaya's params[value] block, where they are interpreted as
# expressions.
extra_args = {
    'h': 0.67810,
    'omega_b': 0.02238280,
    'omega_cdm': 0.01201075,
    'omega_idm': 0.10809675,
    'idm_soundspeed': 'no',
    'N_ur': 3.044,
    'N_ncdm': 0,
    'YHe': 'BBN',
    'scf_parameters': '5., 0., 0., 0., 4.44, 0.',
    'attractor_ic_scf': 'no',
    'scf_tuning_index': 0,
    'rims_enabled': 'yes',
    'rims_enforce_stability': 'yes',
    'rims_stability_tolerance': 1e-10,
    'rims_require_normalization': 'yes',
    'rims_normalization_tolerance': 1e-8,
    'rims_subleading_adiabatic_ic': 'yes',
    'recombination': 'RECFAST',
    'z_reio': 7.6711,
    'reio_parametrization': 'reio_camb',
    'A_s': 2.100549e-9,
    'n_s': 0.9660499,
    'k_pivot': 0.05,
}

params = {
    'Omega_scf': {'prior': {'min': 0.0, 'max': 0.70}},
    'rims_alpha_U': {'prior': {'min': 0.0, 'max': 0.06}},
    'rims_phi_transition': {'prior': {'min': 10.0, 'max': 250.0}},
    'rims_phi_ref': {'prior': {'min': 0.0, 'max': 10.0}},
}

info = {
    'packages_path': str(PACKAGES),
    'theory': {
        'classy': {
            'path': str(CLASS),
            'extra_args': extra_args,
        }
    },
    'likelihood': {
        'bao.desi_dr2': None,
        'sn.pantheonplus': None,
    },
    'params': params,
    'debug': False,
    'stop_at_error': False,
}

model = get_model(info)
like_names = list(model.likelihood)
rows = []

with open(CSV, newline='') as f:
    for r in csv.DictReader(f):
        point = {
            'Omega_scf': float(r['Omega_scf']),
            'rims_alpha_U': float(r['alpha_U']),
            'rims_phi_transition': float(r['phi_t']),
            'rims_phi_ref': float(r['phi_ref']),
        }
        try:
            post = model.logposterior(point, cached=False)
            rec = {
                'label': r['label'],
                **point,
                'logpost': float(post.logpost),
                'minus2logL_total': float(-2.0 * sum(post.loglikes)),
            }
            for name, val in zip(like_names, post.loglikes):
                rec[f'minus2logL__{name}'] = float(-2.0 * val)
            rows.append(rec)
            print('OK', rec['label'], rec['minus2logL_total'], flush=True)
        except Exception as e:
            rows.append({'label': r['label'], **point, 'error': repr(e)})
            print('ERR', r['label'], repr(e), flush=True)

# An almost-LambdaCDM anchor in the same patched executable: scalar fraction
# and coupling set to zero, with the same standard cosmological parameters.
anchor = {
    'Omega_scf': 0.0,
    'rims_alpha_U': 0.0,
    'rims_phi_transition': 100.0,
    'rims_phi_ref': 4.44,
}
try:
    post = model.logposterior(anchor, cached=False)
    anchor_rec = {
        'label': 'patched_LCDM_anchor',
        **anchor,
        'logpost': float(post.logpost),
        'minus2logL_total': float(-2.0 * sum(post.loglikes)),
    }
    for name, val in zip(like_names, post.loglikes):
        anchor_rec[f'minus2logL__{name}'] = float(-2.0 * val)
except Exception as e:
    anchor_rec = {'label': 'patched_LCDM_anchor', **anchor, 'error': repr(e)}
rows.append(anchor_rec)

success = [r for r in rows if 'minus2logL_total' in r]
if success:
    best = min(r['minus2logL_total'] for r in success)
    for r in success:
        r['Delta_chi2_to_best'] = r['minus2logL_total'] - best
    if 'minus2logL_total' in anchor_rec:
        for r in success:
            r['Delta_chi2_to_LCDM_anchor'] = r['minus2logL_total'] - anchor_rec['minus2logL_total']

fieldnames = sorted({k for r in rows for k in r.keys()})
with open(OUT / 'RIMS_REALDATA_PREFLIGHT.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader(); w.writerows(rows)

summary = {
    'claim_boundary': 'Real-data fixed-standard-parameter profile-grid preflight; not production MCMC and not evidence.',
    'datasets': [
        'DESI DR2 BAO: Cobaya bao.desi_dr2',
        'Pantheon+ SN without SH0ES: Cobaya sn.pantheonplus',
    ],
    'evaluated_validated_branches': len(rows)-1,
    'successful_points': len(success),
    'failed_points': len(rows)-len(success),
    'lcdm_anchor': anchor_rec,
}
if success:
    summary['best_point'] = min(success, key=lambda r: r['minus2logL_total'])
    summary['top10'] = sorted(success, key=lambda r: r['minus2logL_total'])[:10]

(OUT / 'RIMS_REALDATA_PREFLIGHT.json').write_text(json.dumps(summary, indent=2))
print(json.dumps(summary, indent=2), flush=True)

if not success:
    raise SystemExit('No successful real-data likelihood evaluations')
