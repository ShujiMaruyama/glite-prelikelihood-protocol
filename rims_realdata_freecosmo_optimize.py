from pathlib import Path
import json, math, subprocess, shutil, hashlib

import numpy as np
from scipy.optimize import minimize, differential_evolution
from cobaya.model import get_model

ROOT=Path.cwd(); CROOT=ROOT/'class_public'; CLASS=CROOT/'class'; PACKAGES=ROOT/'cobaya_packages'
WORK=ROOT/'freecosmo_work'; OUT=ROOT/'freecosmo_results'; WORK.mkdir(exist_ok=True); OUT.mkdir(exist_ok=True)

LIKES={'bao.desi_dr2':None,'sn.pantheonplus':None}

# ---------- LambdaCDM model ----------
lcdm_extra={'YHe':'BBN','recombination':'RECFAST','reio_parametrization':'reio_camb','k_pivot':0.05,
            'N_ur':3.044,'N_ncdm':0,'z_reio':7.6711,'A_s':2.100549e-9,'n_s':0.9660499}
lcdm_params={'h':{'prior':{'min':0.55,'max':0.85}},'omega_b':{'prior':{'min':0.019,'max':0.026}},
             'omega_cdm':{'prior':{'min':0.08,'max':0.16}}}
lcdm_info={'packages_path':str(PACKAGES),'theory':{'classy':{'path':str(CROOT),'extra_args':lcdm_extra}},
           'likelihood':LIKES,'params':lcdm_params,'debug':False,'stop_at_error':False}
lcdm_model=get_model(lcdm_info); lcdm_like_names=list(lcdm_model.likelihood)

lcdm_trace=[]
def lcdm_obj(x):
    h,ob,odm=map(float,x)
    point={'h':h,'omega_b':ob,'omega_cdm':odm}
    try:
        p=lcdm_model.logposterior(point,cached=False); chi=float(-2*sum(p.loglikes))
        if not math.isfinite(chi): raise ValueError('nonfinite')
    except Exception:
        chi=1e12
    lcdm_trace.append([h,ob,odm,chi]); return chi

# Global-low-cost seed then local polish.
lcdm_de=differential_evolution(lcdm_obj,[(0.55,0.85),(0.019,0.026),(0.08,0.16)],
                               seed=20260729,popsize=6,maxiter=10,tol=2e-4,polish=False,workers=1,updating='immediate')
lcdm_opt=minimize(lcdm_obj,lcdm_de.x,method='Powell',bounds=[(0.55,0.85),(0.019,0.026),(0.08,0.16)],
                  options={'maxiter':20,'maxfev':160,'xtol':2e-5,'ftol':2e-5})

lcdm_best_x=np.array(lcdm_opt.x,float); lcdm_best_chi=float(lcdm_opt.fun)
lcdm_post=lcdm_model.logposterior({'h':lcdm_best_x[0],'omega_b':lcdm_best_x[1],'omega_cdm':lcdm_best_x[2]},cached=False)
lcdm_parts={n:float(-2*v) for n,v in zip(lcdm_like_names,lcdm_post.loglikes)}

# ---------- RIMS model ----------
rims_extra={'idm_soundspeed':'no','N_ur':3.044,'N_ncdm':0,'YHe':'BBN',
            'scf_parameters':'5., 0., 0., 0., 4.44, 0.','attractor_ic_scf':'no','scf_tuning_index':0,
            'rims_enabled':'yes','rims_enforce_stability':'yes','rims_stability_tolerance':1e-10,
            'rims_require_normalization':'yes','rims_normalization_tolerance':1e-8,
            'rims_subleading_adiabatic_ic':'yes','recombination':'RECFAST','z_reio':7.6711,
            'reio_parametrization':'reio_camb','A_s':2.100549e-9,'n_s':0.9660499,'k_pivot':0.05}
rims_params={'h':{'prior':{'min':0.55,'max':0.85}},'omega_b':{'prior':{'min':0.019,'max':0.026}},
             'omega_cdm':{'prior':{'min':0.008,'max':0.016}},'omega_idm':{'prior':{'min':0.072,'max':0.144}},
             'Omega_scf':{'prior':{'min':0.04,'max':0.16}},'rims_alpha_U':{'prior':{'min':0.0,'max':0.10}},
             'rims_phi_transition':{'prior':{'min':10.0,'max':220.0}},'rims_phi_ref':{'prior':{'min':0.0,'max':10.0}}}
rims_info={'packages_path':str(PACKAGES),'theory':{'classy':{'path':str(CROOT),'extra_args':rims_extra}},
           'likelihood':LIKES,'params':rims_params,'debug':False,'stop_at_error':False}
rims_model=get_model(rims_info); rims_like_names=list(rims_model.likelihood)

cache={}; rims_trace=[]

def key6(x): return tuple(round(float(v),9) for v in x)

def ini_text(h,ob,odm,oscf,alpha,pt,pref,prefix,require_norm=False):
    ocdm=0.1*odm; oidm=0.9*odm
    return f'''output =\ngauge = synchronous\nic = ad\nh = {h:.14g}\nomega_b = {ob:.14g}\nomega_cdm = {ocdm:.14g}\nomega_idm = {oidm:.14g}\nidm_soundspeed = no\nN_ur = 3.044\nN_ncdm = 0\nYHe = BBN\nOmega_scf = {oscf:.14g}\nscf_parameters = 5., 0., 0., 0., 4.44, 0.\nattractor_ic_scf = no\nscf_tuning_index = 0\nrims_enabled = yes\nrims_alpha_U = {alpha:.14g}\nrims_phi_transition = {pt:.14g}\nrims_phi_ref = {pref:.16g}\nrims_enforce_stability = yes\nrims_stability_tolerance = 1.e-10\nrims_require_normalization = {'yes' if require_norm else 'no'}\nrims_normalization_tolerance = 1.e-8\nrims_subleading_adiabatic_ic = yes\nrecombination = RECFAST\nz_reio = 7.6711\nreio_parametrization = reio_camb\nA_s = 2.100549e-9\nn_s = 0.9660499\nk_pivot = 0.05\nroot = {prefix}\noverwrite_root = yes\nwrite_background = yes\nwrite_parameters = no\nwrite_warnings = no\ninput_verbose = 0\nbackground_verbose = 0\nthermodynamics_verbose = 0\nperturbations_verbose = 0\ntransfer_verbose = 0\nprimordial_verbose = 0\nharmonic_verbose = 0\nfourier_verbose = 0\nlensing_verbose = 0\noutput_verbose = 0\n'''

def run_bg(vals,pref,tag,require_norm=False):
    h,ob,odm,oscf,alpha,pt=vals; d=WORK/tag
    if d.exists(): shutil.rmtree(d)
    d.mkdir(parents=True); prefix=str((d/'run_').resolve()); ini=d/'run.ini'
    ini.write_text(ini_text(h,ob,odm,oscf,alpha,pt,pref,prefix,require_norm))
    cp=subprocess.run([str(CLASS),str(ini)],cwd=CROOT,text=True,capture_output=True); bg=d/'run__background.dat'
    if cp.returncode!=0 or not bg.exists():
        shutil.rmtree(d,ignore_errors=True); return None
    a=np.loadtxt(bg); rec={'phi_today':float(a[-1,18]),'mratio_today':float(a[-1,26]),
                          'min_stability':float(a[:,29].min())}
    shutil.rmtree(d,ignore_errors=True); return rec

def normalize(vals):
    k=key6(vals)
    if k in cache: return cache[k]
    h,ob,odm,oscf,alpha,pt=vals
    if not (0.55<=h<=0.85 and 0.019<=ob<=0.026 and 0.08<=odm<=0.16 and 0.04<=oscf<=0.16 and 0<=alpha<=0.10 and 10<=pt<=220):
        cache[k]=None; return None
    pref=4.343497008603
    if alpha==0:
        rec=run_bg(vals,pref,'norm_zero',False)
        if rec is None: cache[k]=None; return None
    else:
        for it in range(14):
            rec=run_bg(vals,pref,f'norm_{it}',False)
            if rec is None: cache[k]=None; return None
            if abs(rec['mratio_today']-1)<3e-9: break
            pref=rec['phi_today']
    rec=run_bg(vals,pref,'norm_final',True)
    if rec is None or abs(rec['mratio_today']-1)>=1e-8:
        cache[k]=None; return None
    cache[k]=pref; return pref

def rims_obj(x):
    vals=np.array(x,float); pref=normalize(vals)
    if pref is None:
        chi=1e10; rims_trace.append([*vals,np.nan,chi]); return chi
    h,ob,odm,oscf,alpha,pt=vals
    point={'h':h,'omega_b':ob,'omega_cdm':0.1*odm,'omega_idm':0.9*odm,
           'Omega_scf':oscf,'rims_alpha_U':alpha,'rims_phi_transition':pt,'rims_phi_ref':pref}
    try:
        p=rims_model.logposterior(point,cached=False); chi=float(-2*sum(p.loglikes))
        if not math.isfinite(chi): raise ValueError('nonfinite')
    except Exception:
        chi=1e10
    rims_trace.append([*vals,pref,chi]); print('RIMS',vals.tolist(),'pref',pref,'chi2',chi,flush=True); return chi

bounds=[(0.55,0.85),(0.019,0.026),(0.08,0.16),(0.04,0.16),(0.0,0.10),(10.,220.)]
# Two physically distinct starts: interacting fixed-slice minimum and decoupled-scalar neighborhood.
starts=[np.array([0.67810,0.0223828,0.1201075,0.10,0.05,20.0]),
        np.array([0.67810,0.0223828,0.1201075,0.10,0.0,100.0])]
opts=[]
for i,x0 in enumerate(starts):
    res=minimize(rims_obj,x0,method='Powell',bounds=bounds,
                 options={'maxiter':12,'maxfev':180,'xtol':5e-4,'ftol':2e-4})
    opts.append(res)
    print('STARTDONE',i,res.fun,res.x,flush=True)

best_res=min(opts,key=lambda r:r.fun); bx=np.array(best_res.x,float); bpref=normalize(bx)
point={'h':bx[0],'omega_b':bx[1],'omega_cdm':0.1*bx[2],'omega_idm':0.9*bx[2],
       'Omega_scf':bx[3],'rims_alpha_U':bx[4],'rims_phi_transition':bx[5],'rims_phi_ref':bpref}
bpost=rims_model.logposterior(point,cached=False); bparts={n:float(-2*v) for n,v in zip(rims_like_names,bpost.loglikes)}

result={'claim_boundary':'Pilot real-data best-fit optimization with BAO+SN; not MCMC/posterior/evidence.',
        'datasets':['DESI DR2 BAO','Pantheon+ without SH0ES'],
        'lcdm':{'h':float(lcdm_best_x[0]),'omega_b':float(lcdm_best_x[1]),'omega_cdm':float(lcdm_best_x[2]),
                'chi2':lcdm_best_chi,'components':lcdm_parts,'n_objective_calls':len(lcdm_trace)},
        'rims':{'h':float(bx[0]),'omega_b':float(bx[1]),'omega_dm_total':float(bx[2]),
                'omega_cdm':float(0.1*bx[2]),'omega_idm':float(0.9*bx[2]),'Omega_scf':float(bx[3]),
                'alpha_U':float(bx[4]),'phi_t':float(bx[5]),'phi_ref':float(bpref),'chi2':float(best_res.fun),
                'components':bparts,'n_objective_calls':len(rims_trace)},
        'Delta_chi2_RIMS_minus_LCDM':float(best_res.fun-lcdm_best_chi)}
(OUT/'FREECOSMO_BESTFIT.json').write_text(json.dumps(result,indent=2))
np.savetxt(OUT/'LCDM_OPT_TRACE.csv',np.array(lcdm_trace),delimiter=',',header='h,omega_b,omega_cdm,chi2',comments='')
np.savetxt(OUT/'RIMS_OPT_TRACE.csv',np.array(rims_trace),delimiter=',',header='h,omega_b,omega_dm,Omega_scf,alpha_U,phi_t,phi_ref,chi2',comments='')
print(json.dumps(result,indent=2),flush=True)
