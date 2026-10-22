import copy, sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from c23_freeze import build_manifest
from c26_occupancy_gate import derive_initial_gate
from c26_native_receipt_bridge import audit_native_receipt

def make_receipt():
    m=build_manifest();case=m['cases'][0]
    r={'schema':'rims-c23-native-background-attempt-v1',
       'id':case['id'],'case_sha256':case['input_sha256'],
       'source_freeze_hash':m['freeze_hash'],'synthetic_fixture':False,
       'run_status':'solver_completed',
       'c26_initial_shell':derive_initial_gate(case,[0,1,5000],[4,4.2,case['phi_i']])}
    return m,r

def test_earliest_snapshot_pass_when_verified():
    m,r=make_receipt();assert audit_native_receipt(m,r)['gate_pass']

def test_no_class_history_receipt_fail_closed():
    m,r=make_receipt();r.pop('c26_initial_shell')
    assert audit_native_receipt(m,r)['gate']=='MISSING_C26_INITIAL_RECEIPT'

def test_original_solver_failure_not_promoted():
    m,r=make_receipt();r['run_status']='solver_error'
    assert audit_native_receipt(m,r)['gate']=='NATIVE_SOLVER_NOT_COMPLETED'

def test_bogus_case_sha_rejected():
    m,r=make_receipt();r['case_sha256']='0'*64
    with pytest.raises(ValueError):audit_native_receipt(m,r)

def test_synthetic_fixture_rejected():
    m,r=make_receipt();r['synthetic_fixture']=True
    with pytest.raises(ValueError):audit_native_receipt(m,r)

def test_false_early_redshift_rejected():
    m,r=make_receipt();r['c26_initial_shell']['earliest_z']=3
    with pytest.raises(ValueError):audit_native_receipt(m,r)

def test_initial_data_error_stays_failure():
    m,r=make_receipt();r['c26_initial_shell']={'gate':'INITIAL_GATE_DATA_ERROR'}
    assert not audit_native_receipt(m,r)['gate_pass']
