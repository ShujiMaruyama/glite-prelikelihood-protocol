from pathlib import Path
import csv, json, math, subprocess, shutil

import numpy as np
from cobaya.model import get_model

ROOT=Path.cwd(); CLASS=ROOT/'class_public'/'class'; CROOT=ROOT/'class_public'
PACKAGES=ROOT/'cobaya_packages'; WORK=ROOT/'dense_profile_work'; OUT=ROOT/'dense_profile_results'
WORK.mkdir(exist_ok=True); OUT.mkdir(exist_ok=True)

omegas=[0.0005,0.001,0.002,0.003,0.005,0.0075,0.01,0.0125,0.015,0.02,0.03,0.05]
alphas=[0.0,0.0025,0.005,0.01,0.02,0.05]
phi_ts=[20.,100.,200.]

# Same fixed standard cosmology as the executed V14 family.
extra={
'h':0.67810,'omega_b':0.02238280,'omega_cdm':0.01201075,'omega_idm':0.10809675,
'idm_soundspeed':'no','N_ur':3.044,'N_ncdm':0,'YHe':'BBN',
'scf_parameters':'5., 0., 0., 0., 4.44, 0.','attractor_ic_scf':'no','scf_tuning_index':0,
'rims_enabled':'yes','rims_enforce_stability':'yes','rims_stability_tolerance':1e-10,
'rims_require_normalization':'yes','rims_normalization_tolerance':1e-8,
'rims_subleading_adiabatic_ic':'yes','recombination':'RECFAST','z_reio':7.6711,
'reio_parametrization':'reio_camb','A_s':2.100549e-9,'n_s':0.9660499,'k_pivot':0.05,
}
params={
'Omega_scf':{'prior':{'min':0.0001,'max':0.06}},
'rims_alpha_U':{'prior':{'min':0.0,'max':0.06}},
'rims_phi_transition':{'prior':{'min':10.0,'max':250.0}},
'rims_phi_ref':{'prior':{'min':0.0,'max':10.0}},
}
info={'packages_path':str(PACKAGES),'theory':{'classy':{'path':str(ROOT/'class_public'),'extra_args':extra}},
      'likelihood':{'bao.desi_dr2':None,'sn.pantheonplus':None},'params':params,
      'debug':False,'stop_at_error':False}
model=get_model(info); like_names=list(model.likelihood)

# Fixed-point normalization used by the validated V14 scan.
def ini_text(omega,alpha,phi_t,phi_ref,prefix,require_norm=False):
    return f'''output =
gauge = synchronous
ic = ad
h = 0.67810
omega_b = 0.02238280
omega_cdm = 0.01201075
omega_idm = 0.10809675
idm_soundspeed = no
N_ur = 3.044
N_ncdm = 0
YHe = BBN
Omega_scf = {omega:.12g}
scf_parameters = 5., 0., 0., 0., 4.44, 0.
attractor_ic_scf = no
scf_tuning_index = 0
rims_enabled = yes
rims_alpha_U = {alpha:.12g}
rims_phi_transition = {phi_t:.12g}
rims_phi_ref = {phi_ref:.16g}
rims_enforce_stability = yes
rims_stability_tolerance = 1.e-10
rims_require_normalization = {'yes' if require_norm else 'no'}
rims_normalization_tolerance = 1.e-8
rims_subleading_adiabatic_ic = yes
recombination = RECFAST
z_reio = 7.6711
reio_parametrization = reio_camb
A_s = 2.100549e-9
n_s = 0.9660499
k_pivot = 0.05
root = {prefix}
overwrite_root = yes
write_background = yes
write_parameters = no
write_warnings = no
input_verbose = 0
background_verbose = 0
thermodynamics_verbose = 0
perturbations_verbose = 0
transfer_verbose = 0
primordial_verbose = 0
harmonic_verbose = 0
fourier_verbose = 0
lensing_verbose = 0
output_verbose = 0
'''

def run_background(omega,alpha,phi_t,phi_ref,label,require_norm=False):
    d=WORK/label
    if d.exists(): shutil.rmtree(d)
    d.mkdir(parents=True)
    prefix=str((d/'run_').resolve()); ini=d/'run.ini'
    ini.write_text(ini_text(omega,alpha,phi_t,phi_ref,prefix,require_norm))
    cp=subprocess.run([str(CLASS),str(ini)],cwd=CROOT,text=True,capture_output=True)
    bg=d/'run__background.dat'
    if cp.returncode!=0 or not bg.exists():
        return None, {'returncode':cp.returncode,'stderr':cp.stderr[-1000:],'stdout':cp.stdout[-1000:]}
    a=np.loadtxt(bg)
    rec={'phi_today':float(a[-1,18]),'mratio_today':float(a[-1,26]),
         's_today':float(a[-1,23]),'min_stability':float(a[:,29].min())}
    shutil.rmtree(d,ignore_errors=True)
    return rec,None

def normalize(omega,alpha,phi_t):
    phi_ref=4.343497008603
    if alpha==0.0:
        # Coupling-off branch has unity mass ratio independent of the transition.
        rec,err=run_background(omega,alpha,phi_t,phi_ref,'tmp_norm',False)
        if err: return None,err
        return phi_ref,None
    for it in range(18):
        rec,err=run_background(omega,alpha,phi_t,phi_ref,f'tmp_norm_{it}',False)
        if err: return None,err
        if abs(rec['mratio_today']-1.0)<2e-9:
            break
        phi_ref=rec['phi_today']
    rec,err=run_background(omega,alpha,phi_t,phi_ref,'tmp_validate',True)
    if err: return None,err
    if abs(rec['mratio_today']-1.0)>=1e-8:
        return None,{'error':'normalization_not_closed','mratio_today':rec['mratio_today']}
    return phi_ref,None

# Anchor chi2 from the preceding finite-baseline preflight in this same job.
preflight=json.loads((ROOT/'realdata_results'/'RIMS_REALDATA_PREFLIGHT.json').read_text())
anchor=preflight['lcdm_anchor']['minus2logL_total']

rows=[]
for omega in omegas:
  for alpha in alphas:
    for phi_t in phi_ts:
      label=f'o{omega:g}_a{alpha:g}_t{phi_t:g}'
      phi_ref,err=normalize(omega,alpha,phi_t)
      if err:
        rows.append({'label':label,'Omega_scf':omega,'alpha_U':alpha,'phi_t':phi_t,'error':repr(err)})
        print('NORMERR',label,repr(err),flush=True); continue
      point={'Omega_scf':omega,'rims_alpha_U':alpha,'rims_phi_transition':phi_t,'rims_phi_ref':phi_ref}
      try:
        post=model.logposterior(point,cached=False)
        chi2=float(-2*sum(post.loglikes))
        if not math.isfinite(chi2): raise ValueError(f'nonfinite chi2 {chi2}')
        rec={'label':label,'Omega_scf':omega,'alpha_U':alpha,'phi_t':phi_t,'phi_ref':phi_ref,
             'minus2logL_total':chi2,'Delta_chi2_LCDM':chi2-anchor}
        for name,val in zip(like_names,post.loglikes): rec[f'minus2logL__{name}']=float(-2*val)
        rows.append(rec); print('OK',label,chi2,chi2-anchor,flush=True)
      except Exception as e:
        rows.append({'label':label,'Omega_scf':omega,'alpha_U':alpha,'phi_t':phi_t,'phi_ref':phi_ref,'error':repr(e)})
        print('LIKEERR',label,repr(e),flush=True)

fields=sorted({k for r in rows for k in r})
with open(OUT/'RIMS_DENSE_REALDATA_PROFILE.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)

success=[r for r in rows if math.isfinite(r.get('minus2logL_total',math.inf))]
profile_omega=[]
for om in omegas:
    rr=[r for r in success if r['Omega_scf']==om]
    if rr:
        b=min(rr,key=lambda r:r['minus2logL_total'])
        profile_omega.append({'Omega_scf':om,'profile_chi2':b['minus2logL_total'],
                              'profile_Delta_chi2_LCDM':b['Delta_chi2_LCDM'],
                              'best_alpha_U':b['alpha_U'],'best_phi_t':b['phi_t'],'best_phi_ref':b['phi_ref']})
summary={'claim_boundary':'Fixed-standard-parameter dense real-data profile; not MCMC/posterior/evidence.',
         'lcdm_anchor_chi2':anchor,'grid_points':len(rows),'successful_points':len(success),
         'failed_points':len(rows)-len(success),'best_point':min(success,key=lambda r:r['minus2logL_total']) if success else None,
         'profile_omega':profile_omega}
(OUT/'RIMS_DENSE_REALDATA_PROFILE.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2),flush=True)
if not success: raise SystemExit(2)
