from pathlib import Path
import csv, json, math, shutil, subprocess, sys
import numpy as np

ROOT = Path.cwd()
CLASS = ROOT / 'class_public' / 'class'
WORK = ROOT / 'scan_work'
OUT = ROOT / 'scan_results'
WORK.mkdir(exist_ok=True)
OUT.mkdir(exist_ok=True)

lambdas = [5., 10., 20., 40., 60., 80., 100., 120.]
omegas = [1e-3, 1e-2, 3e-2, 1e-1, 3e-1]
ztargets = [0., 0.5, 1., 2., 3.]

def tag(x):
    return f'{x:.6g}'.replace('-', 'm').replace('.', 'p').replace('+','')

def ini_text(lam, omega_scf, phi_ref, prefix, require_norm=False, norm_tol=1e-8):
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
Omega_scf = {omega_scf:.12g}
scf_parameters = {lam:.12g}, 0., 0., 0., 4.44, 0.
attractor_ic_scf = no
scf_tuning_index = 0
rims_enabled = yes
rims_alpha_U = 0.01
rims_phi_transition = 100.
rims_phi_ref = {phi_ref:.16g}
rims_enforce_stability = yes
rims_stability_tolerance = 1.e-10
rims_require_normalization = {'yes' if require_norm else 'no'}
rims_normalization_tolerance = {norm_tol:.3e}
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

def run_one(lam, omega, phi_ref, label, require_norm=False, norm_tol=1e-8):
    d = WORK / label
    d.mkdir(parents=True, exist_ok=True)
    prefix = str((d / 'run_').resolve())
    ini = d / 'run.ini'
    ini.write_text(ini_text(lam, omega, phi_ref, prefix, require_norm, norm_tol))
    cp = subprocess.run([str(CLASS), str(ini)], cwd=ROOT/'class_public', text=True, capture_output=True)
    (d/'stdout.txt').write_text(cp.stdout)
    (d/'stderr.txt').write_text(cp.stderr)
    bg = d/'run__background.dat'
    if cp.returncode != 0 or not bg.exists():
        return {'success': False, 'returncode': cp.returncode, 'label': label,
                'lambda': lam, 'Omega_scf': omega,
                'stdout_tail': cp.stdout[-2000:], 'stderr_tail': cp.stderr[-2000:]}
    a = np.loadtxt(bg)
    z = a[:,0]; H = a[:,3]; phi = a[:,18]; s = a[:,23]
    mratio = a[:,26]; meff2 = a[:,28]; stab = a[:,29]
    mask = (z >= 0.) & (z <= 3.)
    if not np.any(mask):
        return {'success': False, 'returncode': 99, 'label': label,
                'lambda': lam, 'Omega_scf': omega, 'stderr_tail': 'no z=0..3 rows'}
    xi = np.sqrt(np.maximum(meff2[mask],0.))/H[mask]
    rec = {
        'success': True, 'label': label, 'lambda': lam, 'Omega_scf': omega,
        'phi_ref': phi_ref, 'phi_today': float(phi[-1]),
        'mratio_today': float(mratio[-1]), 's_today': float(s[-1]),
        'min_stab_all': float(np.min(stab)),
        'Xi_min_z0_3': float(np.min(xi)), 'Xi_max_z0_3': float(np.max(xi)),
    }
    for zz in ztargets:
        i = int(np.argmin(np.abs(z-zz)))
        rec[f'Xi_z{zz:g}'] = float(math.sqrt(max(meff2[i],0.))/H[i])
        rec[f's_z{zz:g}'] = float(s[i])
    return rec

coarse=[]
initial_ref=4.343497008603
for lam in lambdas:
    for omega in omegas:
        label=f'coarse_l{tag(lam)}_o{tag(omega)}'
        rec=run_one(lam,omega,initial_ref,label,False)
        coarse.append(rec)
        print('COARSE',lam,omega,rec.get('success'),rec.get('Xi_z1'),rec.get('mratio_today'),flush=True)

ok=[r for r in coarse if r.get('success') and r.get('Xi_z1',0)>0 and r.get('min_stab_all',-1)>=-1e-10]
targets={'shielded':0.3,'transition':3.0,'qs_resolvable':12.0}
chosen={}
for name,target in targets.items():
    if ok:
        chosen[name]=min(ok,key=lambda r: abs(math.log(r['Xi_z1']/target)))

normalized=[]
for name,seed in chosen.items():
    lam=seed['lambda']; omega=seed['Omega_scf']; phi_ref=initial_ref
    history=[]; final=None
    for it in range(12):
        label=f'norm_{name}_it{it}_l{tag(lam)}_o{tag(omega)}'
        rec=run_one(lam,omega,phi_ref,label,False)
        history.append(rec)
        if not rec.get('success'):
            break
        final=rec
        if abs(rec['mratio_today']-1.) < 2e-9:
            break
        phi_ref=rec['phi_today']
    validated=None
    if final and abs(final['mratio_today']-1.) < 1e-8:
        label=f'validated_{name}_l{tag(lam)}_o{tag(omega)}'
        validated=run_one(lam,omega,phi_ref,label,True,1e-8)
        if validated.get('success'):
            shutil.copy2(WORK/label/'run__background.dat',OUT/f'{name}_background.dat')
            shutil.copy2(WORK/label/'run.ini',OUT/f'{name}.ini')
    normalized.append({'regime_target':name,'target_Xi_z1':targets[name],
                       'coarse_seed':seed,'iteration_history':history,
                       'validated':validated})

fields=['success','lambda','Omega_scf','phi_ref','phi_today','mratio_today','s_today','min_stab_all',
        'Xi_min_z0_3','Xi_max_z0_3','Xi_z0','Xi_z0.5','Xi_z1','Xi_z2','Xi_z3','label']
with open(OUT/'coarse_scan.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore'); w.writeheader()
    for r in coarse:w.writerow(r)
(OUT/'scan_summary.json').write_text(json.dumps({'coarse':coarse,'chosen_normalized':normalized},indent=2))

final_rows=[]
for item in normalized:
    v=item.get('validated')
    if v and v.get('success'):
        x=v['Xi_z1']
        regime='horizon-shielded' if x<1 else ('relativistic-transition' if x<10 else 'QS-resolvable')
        final_rows.append({'target':item['regime_target'],'regime_at_z1':regime,**v})
keys=['target','regime_at_z1','lambda','Omega_scf','phi_ref','phi_today','mratio_today','s_today','min_stab_all',
      'Xi_min_z0_3','Xi_max_z0_3','Xi_z0','Xi_z0.5','Xi_z1','Xi_z2','Xi_z3','label']
with open(OUT/'validated_regimes.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=keys,extrasaction='ignore'); w.writeheader()
    for r in final_rows:w.writerow(r)

if not final_rows:
    print('No normalized representatives found',file=sys.stderr)
    sys.exit(2)
