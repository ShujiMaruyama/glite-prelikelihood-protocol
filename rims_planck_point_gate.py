from pathlib import Path
import json, math
from cobaya.model import get_model

ROOT=Path.cwd(); CROOT=ROOT/'class_public'; PACKAGES=ROOT/'cobaya_packages'; OUT=ROOT/'planck_gate_results'; OUT.mkdir(exist_ok=True)

# Linear-theory primary-CMB gate. Planck lensing is deliberately excluded here
# because the Cobaya lensing stack requests HMcode, which is not implemented for
# CLASS scalar-field scf and would violate the declared nonlinear claim boundary.
LIKES={
 'planck_2018_lowl.TT':None,
 'planck_2018_lowl.EE':None,
 'planck_2018_highl_plik.TTTEEE_lite_native':None,
 'bao.desi_dr2':None,
 'sn.pantheonplus':None,
}

common_fixed={'N_ur':3.044,'N_ncdm':0,'z_reio':7.6711,'A_s':2.100549e-9,'n_s':0.9660499}
common_extra={'YHe':'BBN','recombination':'RECFAST','reio_parametrization':'reio_camb','k_pivot':0.05,'non_linear':'none'}

def fixed_params(d):
    q={k:{'value':v} for k,v in d.items()}
    q['A_planck']={'value':1.0}
    return q

def evaluate(label,numeric,extra):
    info={'packages_path':str(PACKAGES),'theory':{'classy':{'path':str(CROOT),'extra_args':extra}},
          'likelihood':LIKES,'params':fixed_params(numeric),'debug':False,'stop_at_error':True}
    try:
        model=get_model(info)
        sampled=list(model.parameterization.sampled_params())
        if sampled:
            raise RuntimeError(f'Unexpected sampled/nuisance parameters in point gate: {sampled}')
        p=model.logposterior({},cached=False)
        likes={n:float(-2*v) for n,v in zip(list(model.likelihood),p.loglikes)}
        total=float(sum(likes.values()))
        if not math.isfinite(total):raise ValueError(f'nonfinite total {total}')
        rec={'label':label,'chi2_total':total,'components':likes,'success':True}
    except Exception as e:
        rec={'label':label,'success':False,'error':repr(e)}
    print(json.dumps(rec,indent=2),flush=True);return rec

lcdm={**common_fixed,'h':0.6956517430542902,'omega_b':0.023179611134742532,'omega_cdm':0.1239037531859017}
scalar={**common_fixed,'h':0.6705312864048076,'omega_b':0.022699960375065765,
        'omega_cdm':0.011217828828946792,'omega_idm':0.10096045946052112,
        'Omega_scf':0.11786610164595292,
        'rims_alpha_U':0.0,'rims_phi_transition':100.0,'rims_phi_ref':4.343497008603}
scalar_extra={**common_extra,'idm_soundspeed':'no','scf_parameters':'5., 0., 0., 0., 4.44, 0.',
              'attractor_ic_scf':'no','scf_tuning_index':0,'rims_enabled':'yes',
              'rims_enforce_stability':'yes','rims_stability_tolerance':1e-10,
              'rims_require_normalization':'yes','rims_normalization_tolerance':1e-8,
              'rims_subleading_adiabatic_ic':'yes'}
rims={**common_fixed,'h':0.680223995600956,'omega_b':0.022461166106852372,
      'omega_cdm':0.0118520399358053,'omega_idm':0.10666835942224769,
      'Omega_scf':0.10172480941417969,'rims_alpha_U':0.061318108871045524,
      'rims_phi_transition':20.091077972314686,'rims_phi_ref':4.11730971054}

results=[
 evaluate('LambdaCDM_BAO_SN_best',lcdm,common_extra),
 evaluate('scalar_only_BAO_SN_best',scalar,scalar_extra),
 evaluate('RIMS_BAO_SN_best',rims,scalar_extra),
]
success=[r for r in results if r.get('success')]
if success:
    ref=next((r for r in success if r['label'].startswith('LambdaCDM')),None)
    if ref:
        for r in success:r['Delta_chi2_vs_LCDM_point']=r['chi2_total']-ref['chi2_total']
summary={'claim_boundary':'Pointwise linear-theory Planck 2018 primary CMB + DESI DR2 BAO + Pantheon+ compatibility gate at BAO+SN optimized coordinates; no Planck lensing, no reoptimization, no MCMC/evidence.',
         'nonlinear_boundary':'Planck lensing excluded because Cobaya requests HMcode and CLASS scf does not implement HMcode for scalar fields.',
         'likelihoods':list(LIKES),'results':results}
(OUT/'PLANCK_POINT_GATE.json').write_text(json.dumps(summary,indent=2))
if len(success)!=3:raise SystemExit('One or more Planck point evaluations failed')
