from pathlib import Path
import csv, json, math, shutil, subprocess, sys
import numpy as np

ROOT=Path.cwd(); CLASS=ROOT/'class_public'/'class'; WORK=ROOT/'scan_work'; OUT=ROOT/'scan_results'
WORK.mkdir(exist_ok=True); OUT.mkdir(exist_ok=True)
omegas=[0.01,0.30,0.69]
alphas=[0.005,0.01,0.02,0.05]
phi_ts=[20.,50.,100.,200.]
ztargets=[0.,0.5,1.,2.,3.]

def tag(x): return f'{x:.7g}'.replace('-','m').replace('.','p').replace('+','')

def ini_text(omega,alpha_u,phi_t,phi_ref,prefix,require_norm=False):
    return f'''output = mPk
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
rims_alpha_U = {alpha_u:.12g}
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
P_k_max_h/Mpc = 0.02
z_pk = 0.
root = {prefix}
overwrite_root = yes
write_background = yes
write_parameters = yes
write_warnings = yes
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

def run_one(omega,alpha_u,phi_t,phi_ref,label,require_norm=False):
    d=WORK/label; d.mkdir(parents=True,exist_ok=True)
    ini=d/'run.ini'; prefix=str((d/'run_').resolve()); ini.write_text(ini_text(omega,alpha_u,phi_t,phi_ref,prefix,require_norm))
    cp=subprocess.run([str(CLASS),str(ini)],cwd=ROOT/'class_public',text=True,capture_output=True)
    (d/'stdout.txt').write_text(cp.stdout); (d/'stderr.txt').write_text(cp.stderr)
    bg=d/'run__background.dat'
    if cp.returncode!=0 or not bg.exists():
        return {'success':False,'Omega_scf':omega,'alpha_U':alpha_u,'phi_t':phi_t,'label':label,'returncode':cp.returncode,
                'stdout_tail':cp.stdout[-1600:],'stderr_tail':cp.stderr[-1600:]}
    a=np.loadtxt(bg); z=a[:,0]; H=a[:,3]; phi=a[:,18]; V=a[:,20]; Vpp=a[:,22]; s=a[:,23]
    mratio=a[:,26]; meff2=a[:,28]; stab=a[:,29]; rho_lambda=a[:,12]; rho_tot=a[:,31]
    mask=(z>=0)&(z<=3); xi=np.sqrt(np.maximum(meff2[mask],0))/H[mask]; ss=s[mask]; W=abs(alpha_u)*(1-ss)
    rec={'success':True,'Omega_scf':omega,'alpha_U':alpha_u,'phi_t':phi_t,'phi_ref':phi_ref,'phi_today':float(phi[-1]),
         'mratio_today':float(mratio[-1]),'s_today':float(s[-1]),'min_stab_all':float(stab.min()),
         'Omega_lambda_today':float(rho_lambda[-1]/rho_tot[-1]),'Xi_min_z0_3':float(xi.min()),'Xi_max_z0_3':float(xi.max()),
         's_min_z0_3':float(ss.min()),'s_max_z0_3':float(ss.max()),
         'W_fractional_excursion_z0_3':float((W.max()-W.min())/max(abs(W.mean()),1e-300)),
         'cross_s_1over3':bool(ss.min()<=1/3<=ss.max()),'cross_s_1over2':bool(ss.min()<=0.5<=ss.max()),
         'cross_s_2over3':bool(ss.min()<=2/3<=ss.max()),'label':label}
    for zz in ztargets:
        i=int(np.argmin(np.abs(z-zz))); rec[f'Xi_z{zz:g}']=float(math.sqrt(max(meff2[i],0))/H[i]); rec[f's_z{zz:g}']=float(s[i])
        rec[f'lambda_eff_z{zz:g}']=float(math.sqrt(max(Vpp[i]/V[i],0))) if V[i]>0 else float('nan')
        rec[f'Vpp_over_H2_z{zz:g}']=float(Vpp[i]/H[i]**2)
        rec[f'mattercorr_over_H2_z{zz:g}']=float((meff2[i]-Vpp[i])/H[i]**2)
    return rec

rows=[]; failures=[]
for omega in omegas:
  for alpha_u in alphas:
    for phi_t in phi_ts:
      phi_ref=4.343497008603; final=None
      prefix=f'o{tag(omega)}_a{tag(alpha_u)}_t{tag(phi_t)}'
      for it in range(20):
        rec=run_one(omega,alpha_u,phi_t,phi_ref,f'{prefix}_it{it}',False)
        if not rec.get('success'):
            failures.append(rec); final=None; break
        final=rec
        if abs(rec['mratio_today']-1)<2e-9: break
        phi_ref=rec['phi_today']
      if final and abs(final['mratio_today']-1)<1e-8:
        label=f'validated_{prefix}'; val=run_one(omega,alpha_u,phi_t,phi_ref,label,True)
        if val.get('success'):
            rows.append(val)
            shutil.copy2(WORK/label/'run__background.dat',OUT/f'{label}_background.dat')
            shutil.copy2(WORK/label/'run.ini',OUT/f'{label}.ini')
            print('PASS',omega,alpha_u,phi_t,'XiMax',val['Xi_max_z0_3'],'dW/W',val['W_fractional_excursion_z0_3'],'s',val['s_min_z0_3'],val['s_max_z0_3'],flush=True)
        else:
            failures.append(val); print('FAIL validation',omega,alpha_u,phi_t,flush=True)
      else:
        print('FAIL normalization',omega,alpha_u,phi_t,flush=True)

keys=['success','Omega_scf','alpha_U','phi_t','Omega_lambda_today','phi_ref','phi_today','mratio_today','s_today','min_stab_all',
      'Xi_min_z0_3','Xi_max_z0_3','s_min_z0_3','s_max_z0_3','W_fractional_excursion_z0_3','cross_s_1over3','cross_s_1over2','cross_s_2over3',
      'Xi_z0','Xi_z0.5','Xi_z1','Xi_z2','Xi_z3','s_z0','s_z0.5','s_z1','s_z2','s_z3',
      'lambda_eff_z0','lambda_eff_z0.5','lambda_eff_z1','lambda_eff_z2','lambda_eff_z3',
      'Vpp_over_H2_z0','Vpp_over_H2_z0.5','Vpp_over_H2_z1','Vpp_over_H2_z2','Vpp_over_H2_z3',
      'mattercorr_over_H2_z0','mattercorr_over_H2_z0.5','mattercorr_over_H2_z1','mattercorr_over_H2_z2','mattercorr_over_H2_z3','label']
with open(OUT/'validated_shell_scan.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=keys,extrasaction='ignore'); w.writeheader(); [w.writerow(r) for r in rows]
(OUT/'failed_shell_scan.json').write_text(json.dumps(failures,indent=2))
summary={
 'validated_count':len(rows),'failed_count':len(failures),
 'max_Xi_any_z0_3':max([r['Xi_max_z0_3'] for r in rows],default=None),
 'max_W_fractional_excursion_z0_3':max([r['W_fractional_excursion_z0_3'] for r in rows],default=None),
 'max_s_z0_3':max([r['s_max_z0_3'] for r in rows],default=None),
 'min_s_z0_3':min([r['s_min_z0_3'] for r in rows],default=None),
 'landmark_crossings': [r['label'] for r in rows if r['cross_s_1over3'] or r['cross_s_1over2'] or r['cross_s_2over3']],
 'qs_resolvable': [r['label'] for r in rows if r['Xi_max_z0_3']>=10],
 'top_Xi': sorted(rows,key=lambda r:r['Xi_max_z0_3'],reverse=True)[:10],
 'top_W_excursion': sorted(rows,key=lambda r:r['W_fractional_excursion_z0_3'],reverse=True)[:10]
}
(OUT/'shell_scan_summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps({k:v for k,v in summary.items() if k not in ['top_Xi','top_W_excursion']},indent=2),flush=True)
if not rows: sys.exit(2)
