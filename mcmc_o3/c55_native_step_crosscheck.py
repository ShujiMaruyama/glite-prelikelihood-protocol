#!/usr/bin/env python3
"""Independent small-form read-only cross-check of frozen C44 native phase steps.
Run as: python mcmc_o3/c55_native_step_crosscheck.py ORIGINAL_C44_STDERR.txt
No CLASS compute. No accepted-state effective-mass measurement.
"""
from pathlib import Path
import sys,hashlib,math,re,json
H='9e6fb2fcc83cd47fb7e0168a83952da8ad093da86698bf8300aacb601875e42d'
R=re.compile(r'^RIMS_C43_NDF_TRACE_V1 kind=(COMMIT|TRIAL|ACCEPT_GATE) x=([^ ]+) accepted=(\d+) failed=(\d+) order=(\d+)(?: iter=(\d+))?$')
def independent(data:bytes):
    if hashlib.sha256(data).hexdigest()!=H:raise ValueError('Non-original C44 artifact')
    commit=[];counts={'COMMIT':0,'TRIAL':0,'ACCEPT_GATE':0}
    last_trial=None
    for line in data.decode('utf8').splitlines():
        m=R.match(line)
        if m:
            kind,x,accepted,failed,order,itr=m.groups()
            counts[kind]+=1
            if kind=='COMMIT':commit.append((float(x),int(accepted),int(failed),int(order)))
            if kind=='TRIAL':last_trial=(float(x),int(accepted),int(failed),int(order),int(itr))
    if counts!={'COMMIT':618,'TRIAL':845,'ACCEPT_GATE':618}:raise ValueError('Native phase counts drifted')
    if len(commit)!=618 or any(q[1]!=i for i,q in enumerate(commit,1)):raise ValueError('Accepted sequence gap')
    x=[q[0] for q in commit];dx=[y-x for x,y in zip(x,x[1:])]
    if not all(h>0 for h in dx):raise ValueError('Nonmonotone original log(a)')
    if last_trial[1]!=618 or last_trial[-1]!=1 or not math.isclose(last_trial[0]-x[-1],dx[-1],abs_tol=1e-14):
        raise ValueError('Terminal trial not same proposed interval')
    if set(round(h,14) for h in dx[-100:])!={round(dx[-1],14)}:
        raise ValueError('Terminal step-width plateau mismatch')
    return dict(schema='C55_NATIVE_INDEPENDENT_STEP_CROSSCHECK_V1',
        original_sha256=H,accepted=618,trial_count=845,
        last100_constant_dx=dx[-1],
        last100_increased_internal_failed_counter=commit[-1][2]-commit[-100][2],
        last100_orders=sorted(set(q[3] for q in commit[-100:])),
        terminal_trial_iteration=last_trial[-1],terminal_trial_dx=last_trial[0]-x[-1],
        accepted_mass_observations=0,physical_solution_certified=False,
        note='Reanalysis of ORIGINAL C44 native log only, no new CLASS execution')
if __name__=='__main__':
    print(json.dumps(independent(Path(sys.argv[1]).read_bytes()),indent=2))
