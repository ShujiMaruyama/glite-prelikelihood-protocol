#!/usr/bin/env python3
"""Independent fail-closed connector: physical CLASS receipt -> c26 early-shell gate.

This script NEVER runs CLASS; an absent/malformed native receipt cannot pass.
"""
import argparse
import json
from pathlib import Path
from c23_freeze import verify
from c26_occupancy_gate import audit_initial_gate


def audit_native_receipt(manifest, native_receipt):
    verify(manifest)
    if native_receipt.get('schema') != 'rims-c23-native-background-attempt-v1':
        raise ValueError('Not a canonical physical-background receipt')
    ident=native_receipt.get('id')
    cases=[c for c in manifest['cases'] if c['id']==ident]
    if len(cases)!=1:
        raise ValueError('Unrecognized frozen physical case ID')
    case=cases[0]
    if native_receipt.get('case_sha256')!=case['input_sha256'] or native_receipt.get('source_freeze_hash')!=manifest['freeze_hash']:
        raise ValueError('Physical source case/hash differs from frozen grid')
    if native_receipt.get('synthetic_fixture') is not False:
        raise ValueError('Synthetic fixture cannot be a physical result')
    if native_receipt.get('run_status')!='solver_completed':
        return {'case_id':ident,'gate':'NATIVE_SOLVER_NOT_COMPLETED','gate_pass':False}
    gate=native_receipt.get('c26_initial_shell')
    if not isinstance(gate,dict):
        return {'case_id':ident,'gate':'MISSING_C26_INITIAL_RECEIPT','gate_pass':False}
    if gate.get('gate')=='INITIAL_GATE_DATA_ERROR':
        return {'case_id':ident,'gate':'INITIAL_GATE_DATA_ERROR','gate_pass':False}
    return audit_initial_gate(case,manifest,gate)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--manifest',type=Path,required=True)
    p.add_argument('--native-receipt',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    m=json.loads(a.manifest.read_text());r=json.loads(a.native_receipt.read_text())
    result=audit_native_receipt(m,r)
    if a.out.exists():raise RuntimeError('Refusing overwrite of existing c26 result')
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    if not result['gate_pass']:raise SystemExit(2)
    print('c26 physical initial occupation gate: PASS (not model inference)')

if __name__=='__main__':main()
