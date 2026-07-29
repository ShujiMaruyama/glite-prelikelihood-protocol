from pathlib import Path
import csv, json, math

from cobaya.model import get_model

ROOT = Path.cwd()
CLASS = ROOT / 'class_public'
PACKAGES = ROOT / 'cobaya_packages'
SCAN = ROOT / 'scan_artifact'
OUT = ROOT / 'realdata_results'
OUT.mkdir(exist_ok=True)
CSV = SCAN / 'validated_shell_scan.csv'

# Fixed inputs shared by the validated RIMS scan.
rims_extra = {
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

rims_params = {
    'Omega_scf': {'prior': {'min': 0.0, 'max': 0.70}},
    'rims_alpha_U': {'prior': {'min': 0.0, 'max': 0.06}},
    'rims_phi_transition': {'prior': {'min': 10.0, 'max': 250.0}},
    'rims_phi_ref': {'prior': {'min': 0.0, 'max': 10.0}},
}

likelihoods = {
    'bao.desi_dr2': None,
    'sn.pantheonplus': None,
}

rims_info = {
    'packages_path': str(PACKAGES),
    'theory': {'classy': {'path': str(CLASS), 'extra_args': rims_extra}},
    'likelihood': likelihoods,
    'params': rims_params,
    'debug': False,
    'stop_at_error': False,
}

rims_model = get_model(rims_info)
like_names = list(rims_model.likelihood)
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
            post = rims_model.logposterior(point, cached=False)
            total = float(-2.0 * sum(post.loglikes))
            if not math.isfinite(total):
                raise ValueError(f'non-finite RIMS likelihood: {total}')
            rec = {
                'label': r['label'],
                **point,
                'logpost': float(post.logpost),
                'minus2logL_total': total,
            }
            for name, val in zip(like_names, post.loglikes):
                rec[f'minus2logL__{name}'] = float(-2.0 * val)
            rows.append(rec)
            print('OK', rec['label'], rec['minus2logL_total'], flush=True)
        except Exception as e:
            rows.append({'label': r['label'], **point, 'error': repr(e)})
            print('ERR', r['label'], repr(e), flush=True)

# True standard-LambdaCDM baseline. RIMS/scalar/IDM are absent and the same
# total physical dark-matter density is assigned to ordinary CDM. Numeric
# cosmological quantities are explicit fixed Cobaya parameters; only CLASS
# string/configuration options remain in extra_args.
lcdm_extra = {
    'YHe': 'BBN',
    'recombination': 'RECFAST',
    'reio_parametrization': 'reio_camb',
    'k_pivot': 0.05,
}
lcdm_params = {
    'h': {'value': 0.67810},
    'omega_b': {'value': 0.02238280},
    'omega_cdm': {'value': 0.12010750},
    'N_ur': {'value': 3.044},
    'N_ncdm': {'value': 0},
    'z_reio': {'value': 7.6711},
    'A_s': {'value': 2.100549e-9},
    'n_s': {'value': 0.9660499},
}
lcdm_info = {
    'packages_path': str(PACKAGES),
    'theory': {'classy': {'path': str(CLASS), 'extra_args': lcdm_extra}},
    'likelihood': likelihoods,
    'params': lcdm_params,
    'debug': False,
    'stop_at_error': True,
}

try:
    lcdm_model = get_model(lcdm_info)
    lcdm_like_names = list(lcdm_model.likelihood)
    post = lcdm_model.logposterior({}, cached=False)
    total = float(-2.0 * sum(post.loglikes))
    if not math.isfinite(total):
        raise ValueError(f'non-finite LCDM likelihood: {total}')
    anchor_rec = {
        'label': 'standard_LCDM_anchor',
        'minus2logL_total': total,
        'logpost': float(post.logpost),
    }
    for name, val in zip(lcdm_like_names, post.loglikes):
        anchor_rec[f'minus2logL__{name}'] = float(-2.0 * val)
except Exception as e:
    anchor_rec = {'label': 'standard_LCDM_anchor', 'error': repr(e)}

rows.append(anchor_rec)

success = [r for r in rows if math.isfinite(r.get('minus2logL_total', math.inf))]
if success:
    best = min(r['minus2logL_total'] for r in success)
    for r in success:
        r['Delta_chi2_to_best'] = r['minus2logL_total'] - best
    if math.isfinite(anchor_rec.get('minus2logL_total', math.inf)):
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
    'successful_rims_points': sum(1 for r in rows if r.get('label','').startswith('validated_') and math.isfinite(r.get('minus2logL_total', math.inf))),
    'failed_rims_points': sum(1 for r in rows if r.get('label','').startswith('validated_') and not math.isfinite(r.get('minus2logL_total', math.inf))),
    'lcdm_anchor': anchor_rec,
}
rims_success = [r for r in success if r.get('label','').startswith('validated_')]
if rims_success:
    summary['best_rims_point'] = min(rims_success, key=lambda r: r['minus2logL_total'])
    summary['top10_rims'] = sorted(rims_success, key=lambda r: r['minus2logL_total'])[:10]

(OUT / 'RIMS_REALDATA_PREFLIGHT.json').write_text(json.dumps(summary, indent=2))
print(json.dumps(summary, indent=2), flush=True)

if not rims_success:
    raise SystemExit('No successful RIMS real-data likelihood evaluations')
if not math.isfinite(anchor_rec.get('minus2logL_total', math.inf)):
    raise SystemExit('Standard LCDM anchor failed')
