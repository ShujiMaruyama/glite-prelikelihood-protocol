#!/usr/bin/env python3
"""Independent source-locked early occupancy verification for a RIMS background.

This is an analytical/numerical integrity gate. It does not execute CLASS and does
not show that the background or its cosmological likelihood is physically valid.
"""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path

SCHEMA = 'rims-c26-early-shell-occupancy-v1'
DEFAULT_ABS_S_TOL = 1.0e-3
DEFAULT_EARLIEST_Z_MIN = 1.0e3


def logistic(x: float) -> float:
    """Overflow-free logistic occupancy 1/(1+exp(-x))."""
    if not math.isfinite(x):
        raise ValueError('Nonfinite logistic argument')
    if x >= 0:
        return 1.0/(1.0+math.exp(-x))
    y = math.exp(x)
    return y/(1.0+y)


def expected_occupancy(case: dict, phi: float) -> float:
    return logistic(2.0*float(case['alpha_U'])*(phi-float(case['phi_t'])))


def derive_initial_gate(case: dict, z_values, phi_values,
                        min_initial_z=DEFAULT_EARLIEST_Z_MIN,
                        abs_s_tol=DEFAULT_ABS_S_TOL) -> dict:
    if len(z_values) != len(phi_values) or len(z_values) < 2:
        raise ValueError('Invalid redshift/field vector shapes')
    if not all(math.isfinite(float(v)) for v in z_values):
        raise ValueError('Nonfinite history redshift; no silent trimming')
    if not all(math.isfinite(float(v)) for v in phi_values):
        raise ValueError('Nonfinite history scalar field; no silent trimming')
    idx = max(range(len(z_values)), key=lambda i:float(z_values[i]))
    z = float(z_values[idx]); phi = float(phi_values[idx])
    target = float(case['s_i'])
    calc = expected_occupancy(case, phi)
    err = abs(calc-target)
    if z < min_initial_z:
        state = 'UNRESOLVED_EARLY_EPOCH'
    elif err > abs_s_tol:
        state = 'INITIAL_OCCUPANCY_MISMATCH'
    else:
        state = 'EARLY_OCCUPANCY_PASS'
    return {
        'schema':SCHEMA,'case_id':case['id'],'case_sha256':case['input_sha256'],
        'initial_history_index':idx,'earliest_z':z,'earliest_phi':phi,
        'declared_phi_i':float(case['phi_i']), 'actual_s':calc,
        'declared_s_i':target,'absolute_s_error':err,
        'required_earliest_z_min':float(min_initial_z),
        'absolute_s_tolerance':float(abs_s_tol),'gate':state,
        'is_observational_result':False,
    }


def audit_initial_gate(case:dict, frozen_manifest:dict, receipt:dict) -> dict:
    if receipt.get('schema')!=SCHEMA or receipt.get('case_id')!=case['id'] or receipt.get('case_sha256')!=case['input_sha256']:
        raise ValueError('Identity/source case mismatch')
    if frozen_manifest.get('cases') is None or case not in frozen_manifest['cases']:
        raise ValueError('Case not part of frozen manifest')
    z = float(receipt['earliest_z']); phi = float(receipt['earliest_phi']); observed_s=float(receipt['actual_s'])
    expected_s = expected_occupancy(case,phi)
    if not math.isclose(observed_s,expected_s,rel_tol=0,abs_tol=1.e-13):
        raise ValueError('Tampered/inconsistent initial occupancy')
    if not math.isclose(float(receipt['declared_s_i']),float(case['s_i']),rel_tol=0,abs_tol=1.e-15):
        raise ValueError('Declared target occupancy modified')
    if not math.isclose(float(receipt['absolute_s_error']),abs(expected_s-float(case['s_i'])),rel_tol=0,abs_tol=1.e-13):
        raise ValueError('Reported occupancy error modified')
    if float(receipt['absolute_s_tolerance'])!=DEFAULT_ABS_S_TOL or float(receipt['required_earliest_z_min'])!=DEFAULT_EARLIEST_Z_MIN:
        raise ValueError('Frozen c26 thresholds changed')
    expected = derive_initial_gate(case,[0.0,z],[float(case['phi_i']),phi])
    if receipt['gate']!=expected['gate']:
        raise ValueError('Gate result inconsistent with history')
    return {'case_id':case['id'],'gate':expected['gate'], 'gate_pass':expected['gate']=='EARLY_OCCUPANCY_PASS'}


def main():
    import argparse
    from c23_freeze import verify
    ap=argparse.ArgumentParser();ap.add_argument('--manifest',type=Path,required=True)
    ap.add_argument('--receipt',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args()
    m=json.loads(a.manifest.read_text());verify(m)
    r=json.loads(a.receipt.read_text())
    hits=[c for c in m['cases'] if c['id']==r.get('case_id')]
    if len(hits)!=1:raise SystemExit('Wrong case ID')
    result=audit_initial_gate(hits[0],m,r)
    if a.output.exists():raise SystemExit('Refusing overwrite')
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    if not result['gate_pass']:raise SystemExit(2)
    print('c26 early occupancy gate PASS, not an observational result')

if __name__=='__main__':main()
