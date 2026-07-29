from pathlib import Path
import csv, json, math, shutil, subprocess, sys
import numpy as np

ROOT=Path.cwd(); CLASS=ROOT/'class_public'/'class'; WORK=ROOT/'scan_work'; OUT=ROOT/'scan_results'
WORK.mkdir(exist_ok=True); OUT.mkdir(exist_ok=True)
omegas=[0.30,0.40,0.50,0.60,0.64,0.66,0.67,0.68]
ztargets=[0.,0.5,1.,2.,3.]

def tag(x): return f'{x:.6g}'.replace('-','m').replace('.','p').replace('+','')

def ini_text(omega,phi_ref,prefix,require_norm=False):
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
rims_alpha_U = 0.01
rims_phi_transition = 100.
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

def run_one(omega,phi_ref,label,require_norm=False):
    d=WORK/label; d.mkdir(parents=True,exist_ok=True)
    ini=d/'run.ini'; prefix=str((d/'run_').resolve()); ini.write_text(ini_text(omega,phi_ref,prefix,require_norm))
    cp=subprocess.run([str(CLASS),str(ini)],cwd=ROOT/'class_public',text=True,capture_output=True)
    (d/'stdout.txt').write_text(cp.stdout); (d/'stderr.txt').write_text(cp.stderr)
    bg=d/'run__background.dat'
    if cp.returncode!=0 or not bg.exists():
        return {'success':False,'Omega_scf':omega,'label':label,'returncode':cp.returncode,
                'stdout_tail':cp.stdout[-2000:],'stderr_tail':cp.stderr[-2000:]}
    a=np.loadtxt(bg); z=a[:,0]; H=a[:,3]; phi=a[:,18]; V=a[:,20]; Vpp=a[:,22]; s=a[:,23]
    mratio=a[:,26]; meff2=a[:,28]; stab=a[:,29]
    mask=(z>=0)&(z<=3); xi=np.sqrt(np.maximum(meff2[mask],0))/H[mask]
    rec={'success':True,'Omega_scf':omega,'phi_ref':phi_ref,'phi_today':float(phi[-1]),
         'mratio_today':float(mratio[-1]),'s_today':float(s[-1]),'min_stab_all':float(stab.min()),
         'Xi_min_z0_3':float(xi.min()),'Xi_max_z0_3':float(xi.max()),'label':label}
    for zz in ztargets:
        i=int(np.argmin(np.abs(z-zz))); rec[f'Xi_z{zz:g}']=float(math.sqrt(max(meff2[i],0))/H[i]); rec[f's_z{zz:g}']=float(s[i])
        rec[f'lambda_eff_z{zz:g}']=float(math.sqrt(max(Vpp[i]/V[i],0))) if V[i]>0 else float('nan')
    return rec

rows=[]; initial_ref=4.343497008603
for omega in omegas:
    phi_ref=initial_ref; hist=[]; final=None
    for it in range(16):
        rec=run_one(omega,phi_ref,f'edge_o{tag(omega)}_it{it}',False); hist.append(rec)
        if not rec.get('success'): break
        final=rec
        if abs(rec['mratio_today']-1)<2e-9: break
        phi_ref=rec['phi_today']
    validated=None
    if final and abs(final['mratio_today']-1)<1e-8:
        label=f'validated_edge_o{tag(omega)}'; validated=run_one(omega,phi_ref,label,True)
        if validated.get('success'):
            shutil.copy2(WORK/label/'run__background.dat',OUT/f'edge_o{tag(omega)}_background.dat')
            shutil.copy2(WORK/label/'run.ini',OUT/f'edge_o{tag(omega)}.ini')
            rows.append(validated)
    print('EDGE',omega,'valid',bool(validated and validated.get('success')),'Xi1',None if not validated else validated.get('Xi_z1'),flush=True)

keys=['success','Omega_scf','phi_ref','phi_today','mratio_today','s_today','min_stab_all','Xi_min_z0_3','Xi_max_z0_3',
      'Xi_z0','Xi_z0.5','Xi_z1','Xi_z2','Xi_z3','lambda_eff_z0','lambda_eff_z0.5','lambda_eff_z1','lambda_eff_z2','lambda_eff_z3','label']
with open(OUT/'validated_edge_scan.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=keys,extrasaction='ignore'); w.writeheader(); [w.writerow(r) for r in rows]
summary={'validated_edge':rows,'max_Xi_z1':max([r['Xi_z1'] for r in rows],default=None),
         'max_Xi_any_z0_3':max([r['Xi_max_z0_3'] for r in rows],default=None)}
(OUT/'edge_scan_summary.json').write_text(json.dumps(summary,indent=2))
if not rows: sys.exit(2)
