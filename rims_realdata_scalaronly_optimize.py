from pathlib import Path
import json, math
import numpy as np
from scipy.optimize import differential_evolution, minimize
from cobaya.model import get_model

ROOT=Path.cwd(); CROOT=ROOT/'class_public'; PACKAGES=ROOT/'cobaya_packages'; OUT=ROOT/'scalaronly_results'; OUT.mkdir(exist_ok=True)

extra={'idm_soundspeed':'no','N_ur':3.044,'N_ncdm':0,'YHe':'BBN',
       'scf_parameters':'5., 0., 0., 0., 4.44, 0.','attractor_ic_scf':'no','scf_tuning_index':0,
       'rims_enabled':'yes','rims_alpha_U':0.0,'rims_phi_transition':100.0,'rims_phi_ref':4.343497008603,
       'rims_enforce_stability':'yes','rims_stability_tolerance':1e-10,'rims_require_normalization':'yes',
       'rims_normalization_tolerance':1e-8,'rims_subleading_adiabatic_ic':'yes','recombination':'RECFAST',
       'z_reio':7.6711,'reio_parametrization':'reio_camb','A_s':2.100549e-9,'n_s':0.9660499,'k_pivot':0.05}
params={'h':{'prior':{'min':0.55,'max':0.85}},'omega_b':{'prior':{'min':0.019,'max':0.026}},
        'omega_cdm':{'prior':{'min':0.008,'max':0.016}},'omega_idm':{'prior':{'min':0.072,'max':0.144}},
        'Omega_scf':{'prior':{'min':0.02,'max':0.18}}}
info={'packages_path':str(PACKAGES),'theory':{'classy':{'path':str(CROOT),'extra_args':extra}},
      'likelihood':{'bao.desi_dr2':None,'sn.pantheonplus':None},'params':params,'debug':False,'stop_at_error':False}
model=get_model(info); names=list(model.likelihood); trace=[]

def obj(x):
    h,ob,odm,oscf=map(float,x)
    point={'h':h,'omega_b':ob,'omega_cdm':0.1*odm,'omega_idm':0.9*odm,'Omega_scf':oscf}
    try:
        p=model.logposterior(point,cached=False); chi=float(-2*sum(p.loglikes))
        if not math.isfinite(chi):raise ValueError('nonfinite')
    except Exception:chi=1e12
    trace.append([h,ob,odm,oscf,chi]);return chi

bounds=[(0.55,0.85),(0.019,0.026),(0.08,0.16),(0.02,0.18)]
de=differential_evolution(obj,bounds,seed=20260729,popsize=6,maxiter=9,tol=2e-4,polish=False,workers=1)
opt=minimize(obj,de.x,method='Powell',bounds=bounds,options={'maxiter':20,'maxfev':180,'xtol':2e-5,'ftol':2e-5})
x=np.array(opt.x,float); point={'h':x[0],'omega_b':x[1],'omega_cdm':0.1*x[2],'omega_idm':0.9*x[2],'Omega_scf':x[3]}
p=model.logposterior(point,cached=False); comps={n:float(-2*v) for n,v in zip(names,p.loglikes)}
res={'claim_boundary':'Decoupled-scalar best-fit pilot; alpha_U=0; not posterior/evidence.',
     'h':float(x[0]),'omega_b':float(x[1]),'omega_dm_total':float(x[2]),
     'omega_cdm':float(0.1*x[2]),'omega_idm':float(0.9*x[2]),'Omega_scf':float(x[3]),
     'chi2':float(opt.fun),'components':comps,'objective_calls':len(trace)}
(OUT/'SCALARONLY_BESTFIT.json').write_text(json.dumps(res,indent=2))
np.savetxt(OUT/'SCALARONLY_OPT_TRACE.csv',np.array(trace),delimiter=',',header='h,omega_b,omega_dm,Omega_scf,chi2',comments='')
print(json.dumps(res,indent=2),flush=True)
