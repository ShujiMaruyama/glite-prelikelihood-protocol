from pathlib import Path
import csv, json, math, subprocess, shutil
import numpy as np
from cobaya.model import get_model

ROOT=Path.cwd(); CLASS=ROOT/'class_public'/'class'; CROOT=ROOT/'class_public'; PACKAGES=ROOT/'cobaya_packages'
WORK=ROOT/'extension_profile_work'; OUT=ROOT/'extension_profile_results'; WORK.mkdir(exist_ok=True); OUT.mkdir(exist_ok=True)
omegas=[0.05,0.06,0.075,0.10,0.125,0.15,0.175,0.20,0.25]
alphas=[0.0,0.0025,0.005,0.01,0.02,0.05]; phi_ts=[20.,100.,200.]

extra={'h':0.67810,'omega_b':0.02238280,'omega_cdm':0.01201075,'omega_idm':0.10809675,
'idm_soundspeed':'no','N_ur':3.044,'N_ncdm':0,'YHe':'BBN','scf_parameters':'5., 0., 0., 0., 4.44, 0.',
'attractor_ic_scf':'no','scf_tuning_index':0,'rims_enabled':'yes','rims_enforce_stability':'yes',
'rims_stability_tolerance':1e-10,'rims_require_normalization':'yes','rims_normalization_tolerance':1e-8,
'rims_subleading_adiabatic_ic':'yes','recombination':'RECFAST','z_reio':7.6711,'reio_parametrization':'reio_camb',
'A_s':2.100549e-9,'n_s':0.9660499,'k_pivot':0.05}
params={'Omega_scf':{'prior':{'min':0.04,'max':0.26}},'rims_alpha_U':{'prior':{'min':0.0,'max':0.06}},
'rims_phi_transition':{'prior':{'min':10.0,'max':250.0}},'rims_phi_ref':{'prior':{'min':0.0,'max':10.0}}}
info={'packages_path':str(PACKAGES),'theory':{'classy':{'path':str(ROOT/'class_public'),'extra_args':extra}},
'likelihood':{'bao.desi_dr2':None,'sn.pantheonplus':None},'params':params,'debug':False,'stop_at_error':False}
model=get_model(info); like_names=list(model.likelihood)

def ini_text(omega,alpha,phi_t,phi_ref,prefix,require_norm=False):
 return f'''output =\ngauge = synchronous\nic = ad\nh = 0.67810\nomega_b = 0.02238280\nomega_cdm = 0.01201075\nomega_idm = 0.10809675\nidm_soundspeed = no\nN_ur = 3.044\nN_ncdm = 0\nYHe = BBN\nOmega_scf = {omega:.12g}\nscf_parameters = 5., 0., 0., 0., 4.44, 0.\nattractor_ic_scf = no\nscf_tuning_index = 0\nrims_enabled = yes\nrims_alpha_U = {alpha:.12g}\nrims_phi_transition = {phi_t:.12g}\nrims_phi_ref = {phi_ref:.16g}\nrims_enforce_stability = yes\nrims_stability_tolerance = 1.e-10\nrims_require_normalization = {'yes' if require_norm else 'no'}\nrims_normalization_tolerance = 1.e-8\nrims_subleading_adiabatic_ic = yes\nrecombination = RECFAST\nz_reio = 7.6711\nreio_parametrization = reio_camb\nA_s = 2.100549e-9\nn_s = 0.9660499\nk_pivot = 0.05\nroot = {prefix}\noverwrite_root = yes\nwrite_background = yes\nwrite_parameters = no\nwrite_warnings = no\ninput_verbose = 0\nbackground_verbose = 0\nthermodynamics_verbose = 0\nperturbations_verbose = 0\ntransfer_verbose = 0\nprimordial_verbose = 0\nharmonic_verbose = 0\nfourier_verbose = 0\nlensing_verbose = 0\noutput_verbose = 0\n'''

def run_bg(omega,alpha,phi_t,phi_ref,label,require_norm=False):
 d=WORK/label
 if d.exists(): shutil.rmtree(d)
 d.mkdir(parents=True); prefix=str((d/'run_').resolve()); ini=d/'run.ini'; ini.write_text(ini_text(omega,alpha,phi_t,phi_ref,prefix,require_norm))
 cp=subprocess.run([str(CLASS),str(ini)],cwd=CROOT,text=True,capture_output=True); bg=d/'run__background.dat'
 if cp.returncode!=0 or not bg.exists():
  shutil.rmtree(d,ignore_errors=True); return None,{'returncode':cp.returncode,'stdout':cp.stdout[-1000:],'stderr':cp.stderr[-1000:]}
 a=np.loadtxt(bg); rec={'phi_today':float(a[-1,18]),'mratio_today':float(a[-1,26]),'min_stability':float(a[:,29].min())}
 shutil.rmtree(d,ignore_errors=True); return rec,None

def normalize(omega,alpha,phi_t):
 phi_ref=4.343497008603
 if alpha==0:
  rec,err=run_bg(omega,alpha,phi_t,phi_ref,'tmp0',False); return (phi_ref,None) if not err else (None,err)
 for it in range(18):
  rec,err=run_bg(omega,alpha,phi_t,phi_ref,f'tmp{it}',False)
  if err:return None,err
  if abs(rec['mratio_today']-1)<2e-9:break
  phi_ref=rec['phi_today']
 rec,err=run_bg(omega,alpha,phi_t,phi_ref,'tmpv',True)
 if err:return None,err
 if abs(rec['mratio_today']-1)>=1e-8:return None,{'error':'normalization_not_closed','mratio_today':rec['mratio_today']}
 return phi_ref,None

anchor=json.loads((ROOT/'realdata_results'/'RIMS_REALDATA_PREFLIGHT.json').read_text())['lcdm_anchor']['minus2logL_total']
rows=[]
for om in omegas:
 for al in alphas:
  pts=[100.] if al==0 else phi_ts
  for pt in pts:
   label=f'o{om:g}_a{al:g}_t{pt:g}'; pref,err=normalize(om,al,pt)
   if err:
    rows.append({'label':label,'Omega_scf':om,'alpha_U':al,'phi_t':pt,'error':repr(err)}); print('NORMERR',label,flush=True); continue
   point={'Omega_scf':om,'rims_alpha_U':al,'rims_phi_transition':pt,'rims_phi_ref':pref}
   try:
    post=model.logposterior(point,cached=False); chi=float(-2*sum(post.loglikes))
    if not math.isfinite(chi): raise ValueError('nonfinite')
    rec={'label':label,'Omega_scf':om,'alpha_U':al,'phi_t':pt,'phi_ref':pref,'minus2logL_total':chi,'Delta_chi2_LCDM':chi-anchor}
    for name,val in zip(like_names,post.loglikes):rec[f'minus2logL__{name}']=float(-2*val)
    rows.append(rec); print('OK',label,chi,chi-anchor,flush=True)
   except Exception as e:
    rows.append({'label':label,'Omega_scf':om,'alpha_U':al,'phi_t':pt,'phi_ref':pref,'error':repr(e)}); print('LIKEERR',label,repr(e),flush=True)

fields=sorted({k for r in rows for k in r});
with open(OUT/'RIMS_EXTENSION_REALDATA_PROFILE.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
succ=[r for r in rows if math.isfinite(r.get('minus2logL_total',math.inf))]; prof=[]
for om in omegas:
 rr=[r for r in succ if r['Omega_scf']==om]
 if rr:
  b=min(rr,key=lambda r:r['minus2logL_total']);prof.append({'Omega_scf':om,'profile_chi2':b['minus2logL_total'],'profile_Delta_chi2_LCDM':b['Delta_chi2_LCDM'],'best_alpha_U':b['alpha_U'],'best_phi_t':b['phi_t'],'best_phi_ref':b['phi_ref']})
summary={'claim_boundary':'Fixed-standard-parameter extension profile; not posterior/evidence.','lcdm_anchor_chi2':anchor,'grid_points':len(rows),'successful_points':len(succ),'failed_points':len(rows)-len(succ),'best_point':min(succ,key=lambda r:r['minus2logL_total']) if succ else None,'profile_omega':prof}
(OUT/'RIMS_EXTENSION_REALDATA_PROFILE.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2),flush=True)
if not succ:raise SystemExit(2)
