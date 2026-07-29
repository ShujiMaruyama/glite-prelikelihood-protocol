from pathlib import Path
import json, math, subprocess, shutil
import numpy as np
from scipy.optimize import minimize
from cobaya.model import get_model

ROOT=Path.cwd(); CROOT=ROOT/'class_public'; CLASS=CROOT/'class'; PACKAGES=ROOT/'cobaya_packages'; WORK=ROOT/'joint_work'; OUT=ROOT/'joint_results'; WORK.mkdir(exist_ok=True); OUT.mkdir(exist_ok=True)
LIKES={'planck_2018_lowl.TT':None,'planck_2018_lowl.EE':None,'planck_2018_highl_plik.TTTEEE_lite_native':None,'bao.desi_dr2':None,'sn.pantheonplus':None}

# x = h, omega_b, omega_dm, ln(1e10 As), n_s, z_reio
bounds=[(0.62,0.74),(0.021,0.0245),(0.105,0.135),(2.8,3.3),(0.93,1.00),(6.0,10.0)]

def As(logA): return 1e-10*np.exp(logA)

# ---------------- LCDM ----------------
lcdm_extra={'YHe':'BBN','recombination':'RECFAST','reio_parametrization':'reio_camb','k_pivot':0.05,'N_ur':3.044,'N_ncdm':0,'non_linear':'none'}
lcdm_params={
'h':{'prior':{'min':0.62,'max':0.74}},'omega_b':{'prior':{'min':0.021,'max':0.0245}},'omega_cdm':{'prior':{'min':0.105,'max':0.135}},
'A_s':{'prior':{'min':1.6e-9,'max':2.8e-9}},'n_s':{'prior':{'min':0.93,'max':1.0}},'z_reio':{'prior':{'min':6.0,'max':10.0}},'A_planck':{'value':1.0}}
lcdm_model=get_model({'packages_path':str(PACKAGES),'theory':{'classy':{'path':str(CROOT),'extra_args':lcdm_extra}},'likelihood':LIKES,'params':lcdm_params,'debug':False,'stop_at_error':False})
lcdm_names=list(lcdm_model.likelihood); lcdm_trace=[]
def lcdm_obj(x):
 h,ob,odm,la,ns,zr=map(float,x); point={'h':h,'omega_b':ob,'omega_cdm':odm,'A_s':As(la),'n_s':ns,'z_reio':zr}
 try:
  p=lcdm_model.logposterior(point,cached=False); chi=float(-2*sum(p.loglikes));
  if not math.isfinite(chi): raise ValueError('nonfinite')
 except Exception: chi=1e10
 lcdm_trace.append([*x,chi]); print('LCDM',list(x),chi,flush=True); return chi

x0L=np.array([0.67810,0.0223828,0.1201075,np.log(1e10*2.100549e-9),0.9660499,7.6711])
optL=minimize(lcdm_obj,x0L,method='Powell',bounds=bounds,options={'maxiter':10,'maxfev':130,'xtol':2e-4,'ftol':5e-5})
xbL=np.array(optL.x,float); pL=lcdm_model.logposterior({'h':xbL[0],'omega_b':xbL[1],'omega_cdm':xbL[2],'A_s':As(xbL[3]),'n_s':xbL[4],'z_reio':xbL[5]},cached=False)
compL={n:float(-2*v) for n,v in zip(lcdm_names,pL.loglikes)}

# ---------------- RIMS sector fixed, standard coordinates optimized ----------------
OSC=0.10172480941417969; ALPHA=0.061318108871045524; PT=20.091077972314686
rims_extra={'idm_soundspeed':'no','N_ur':3.044,'N_ncdm':0,'YHe':'BBN','scf_parameters':'5., 0., 0., 0., 4.44, 0.','attractor_ic_scf':'no','scf_tuning_index':0,'rims_enabled':'yes','rims_enforce_stability':'yes','rims_stability_tolerance':1e-10,'rims_require_normalization':'yes','rims_normalization_tolerance':1e-8,'rims_subleading_adiabatic_ic':'yes','recombination':'RECFAST','reio_parametrization':'reio_camb','k_pivot':0.05,'non_linear':'none'}
rims_params={'h':{'prior':{'min':0.62,'max':0.74}},'omega_b':{'prior':{'min':0.021,'max':0.0245}},'omega_cdm':{'prior':{'min':0.0105,'max':0.0135}},'omega_idm':{'prior':{'min':0.0945,'max':0.1215}},'Omega_scf':{'value':OSC},'rims_alpha_U':{'value':ALPHA},'rims_phi_transition':{'value':PT},'rims_phi_ref':{'prior':{'min':0.0,'max':10.0}},'A_s':{'prior':{'min':1.6e-9,'max':2.8e-9}},'n_s':{'prior':{'min':0.93,'max':1.0}},'z_reio':{'prior':{'min':6.0,'max':10.0}},'A_planck':{'value':1.0}}
rims_model=get_model({'packages_path':str(PACKAGES),'theory':{'classy':{'path':str(CROOT),'extra_args':rims_extra}},'likelihood':LIKES,'params':rims_params,'debug':False,'stop_at_error':False})
rims_names=list(rims_model.likelihood); cache={}; rims_trace=[]

def run_bg(vals,pref,tag,require_norm=False):
 h,ob,odm,la,ns,zr=vals; d=WORK/tag
 if d.exists(): shutil.rmtree(d)
 d.mkdir(parents=True); prefix=str((d/'run_').resolve()); ini=d/'run.ini'
 ini.write_text(f'''output =\ngauge = synchronous\nic = ad\nh = {h:.14g}\nomega_b = {ob:.14g}\nomega_cdm = {0.1*odm:.14g}\nomega_idm = {0.9*odm:.14g}\nidm_soundspeed = no\nN_ur = 3.044\nN_ncdm = 0\nYHe = BBN\nOmega_scf = {OSC:.16g}\nscf_parameters = 5., 0., 0., 0., 4.44, 0.\nattractor_ic_scf = no\nscf_tuning_index = 0\nrims_enabled = yes\nrims_alpha_U = {ALPHA:.16g}\nrims_phi_transition = {PT:.16g}\nrims_phi_ref = {pref:.16g}\nrims_enforce_stability = yes\nrims_stability_tolerance = 1.e-10\nrims_require_normalization = {'yes' if require_norm else 'no'}\nrims_normalization_tolerance = 1.e-8\nrims_subleading_adiabatic_ic = yes\nrecombination = RECFAST\nz_reio = {zr:.14g}\nreio_parametrization = reio_camb\nA_s = {As(la):.16g}\nn_s = {ns:.14g}\nk_pivot = 0.05\nroot = {prefix}\noverwrite_root = yes\nwrite_background = yes\nwrite_parameters = no\nwrite_warnings = no\ninput_verbose = 0\nbackground_verbose = 0\nthermodynamics_verbose = 0\nperturbations_verbose = 0\ntransfer_verbose = 0\nprimordial_verbose = 0\nharmonic_verbose = 0\nfourier_verbose = 0\nlensing_verbose = 0\noutput_verbose = 0\n''')
 cp=subprocess.run([str(CLASS),str(ini)],cwd=CROOT,text=True,capture_output=True); bg=d/'run__background.dat'
 if cp.returncode!=0 or not bg.exists(): shutil.rmtree(d,ignore_errors=True); return None
 a=np.loadtxt(bg); rec={'phi_today':float(a[-1,18]),'mratio_today':float(a[-1,26])}; shutil.rmtree(d,ignore_errors=True); return rec

def normalize(vals):
 key=tuple(round(float(v),8) for v in vals[:3]) # As/ns/reio do not affect mass normalization materially, but retain standard background coords
 if key in cache:return cache[key]
 pref=4.11730971054
 for it in range(12):
  rec=run_bg(vals,pref,f'n{it}',False)
  if rec is None:cache[key]=None;return None
  if abs(rec['mratio_today']-1)<3e-9:break
  pref=rec['phi_today']
 rec=run_bg(vals,pref,'nv',True)
 if rec is None or abs(rec['mratio_today']-1)>=1e-8: cache[key]=None;return None
 cache[key]=pref;return pref

def rims_obj(x):
 vals=np.array(x,float); pref=normalize(vals)
 if pref is None: chi=1e10; rims_trace.append([*vals,np.nan,chi]); return chi
 h,ob,odm,la,ns,zr=vals
 point={'h':h,'omega_b':ob,'omega_cdm':0.1*odm,'omega_idm':0.9*odm,'rims_phi_ref':pref,'A_s':As(la),'n_s':ns,'z_reio':zr}
 try:
  p=rims_model.logposterior(point,cached=False); chi=float(-2*sum(p.loglikes));
  if not math.isfinite(chi):raise ValueError('nonfinite')
 except Exception:chi=1e10
 rims_trace.append([*vals,pref,chi]); print('RIMS',list(vals),pref,chi,flush=True);return chi

x0R=np.array([0.680223995600956,0.022461166106852372,0.11852039935805299,np.log(1e10*2.100549e-9),0.9660499,7.6711])
optR=minimize(rims_obj,x0R,method='Powell',bounds=bounds,options={'maxiter':10,'maxfev':150,'xtol':3e-4,'ftol':8e-5})
xbR=np.array(optR.x,float); prefR=normalize(xbR); pR=rims_model.logposterior({'h':xbR[0],'omega_b':xbR[1],'omega_cdm':0.1*xbR[2],'omega_idm':0.9*xbR[2],'rims_phi_ref':prefR,'A_s':As(xbR[3]),'n_s':xbR[4],'z_reio':xbR[5]},cached=False); compR={n:float(-2*v) for n,v in zip(rims_names,pR.loglikes)}

result={'claim_boundary':'Joint Planck-primary+DESI-DR2-BAO+Pantheon+ standard-coordinate best-fit pilot; RIMS sector fixed at low-z optimum; no lensing/MCMC/evidence.',
'lcdm':{'h':float(xbL[0]),'omega_b':float(xbL[1]),'omega_cdm':float(xbL[2]),'A_s':float(As(xbL[3])),'n_s':float(xbL[4]),'z_reio':float(xbL[5]),'chi2':float(optL.fun),'components':compL,'calls':len(lcdm_trace)},
'rims_fixed_sector':{'Omega_scf':OSC,'alpha_U':ALPHA,'phi_t':PT,'h':float(xbR[0]),'omega_b':float(xbR[1]),'omega_dm_total':float(xbR[2]),'omega_cdm':float(0.1*xbR[2]),'omega_idm':float(0.9*xbR[2]),'phi_ref':float(prefR),'A_s':float(As(xbR[3])),'n_s':float(xbR[4]),'z_reio':float(xbR[5]),'chi2':float(optR.fun),'components':compR,'calls':len(rims_trace)},
'Delta_chi2_RIMS_minus_LCDM':float(optR.fun-optL.fun)}
(OUT/'JOINT_STANDARD_OPTIMIZATION.json').write_text(json.dumps(result,indent=2));np.savetxt(OUT/'LCDM_JOINT_TRACE.csv',np.array(lcdm_trace),delimiter=',',header='h,omega_b,omega_dm,logA,ns,zreio,chi2',comments='');np.savetxt(OUT/'RIMS_JOINT_TRACE.csv',np.array(rims_trace),delimiter=',',header='h,omega_b,omega_dm,logA,ns,zreio,phi_ref,chi2',comments='');print(json.dumps(result,indent=2),flush=True)
