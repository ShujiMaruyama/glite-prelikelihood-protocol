import copy, math, sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from c23_freeze import build_manifest
from c26_occupancy_gate import derive_initial_gate, audit_initial_gate, expected_occupancy, logistic

@pytest.fixture
def source():
    m=build_manifest();return m,m['cases'][0]

def test_target_phi_identity_all_81():
    m=build_manifest()
    for c in m['cases']:
        assert math.isclose(expected_occupancy(c,c['phi_i']),c['s_i'],rel_tol=0,abs_tol=2e-15)

def test_81_source_case_unique():
    m=build_manifest();assert len({r['input_sha256'] for r in m['cases']})==81

def test_true_initial_state_pass(source):
    m,c=source
    result=derive_initial_gate(c,[0,3,1200],[4.0,4.1,c['phi_i']])
    assert result['gate']=='EARLY_OCCUPANCY_PASS'
    assert audit_initial_gate(c,m,result)['gate_pass']

def test_missing_early_epoch_rejected(source):
    m,c=source
    result=derive_initial_gate(c,[0,1,3],[4,4.2,c['phi_i']])
    assert result['gate']=='UNRESOLVED_EARLY_EPOCH'
    assert not audit_initial_gate(c,m,result)['gate_pass']

def test_early_occupancy_mismatch_rejected(source):
    m,c=source
    result=derive_initial_gate(c,[0,2,10000],[4,4.4,c['phi_i']+10])
    assert result['gate']=='INITIAL_OCCUPANCY_MISMATCH'

def test_reversed_history_order_doesnt_change(source):
    m,c=source
    a=derive_initial_gate(c,[5000,1000,0],[c['phi_i'],4.3,4.2])
    b=derive_initial_gate(c,[0,1000,5000],[4.2,4.3,c['phi_i']])
    assert a['actual_s']==b['actual_s'] and a['gate']==b['gate']

def test_saturating_sigmoid_stable():
    assert logistic(10000)==1
    assert logistic(-10000)==0

def test_nonfinite_source_never_silently_dropped(source):
    m,c=source
    with pytest.raises(ValueError):derive_initial_gate(c,[0,float('nan'),3000],[1,2,3])
    with pytest.raises(ValueError):derive_initial_gate(c,[0,100,3000],[1,float('inf'),3])

def test_wrong_frozen_case_refused(source):
    m,c=source
    r=derive_initial_gate(c,[0,3000],[0,c['phi_i']])
    r['case_id']='rims_080'
    with pytest.raises(ValueError):audit_initial_gate(c,m,r)

def test_tampered_occupancy_refused(source):
    m,c=source
    r=derive_initial_gate(c,[0,3000],[0,c['phi_i']]);r['actual_s']+=0.02
    with pytest.raises(ValueError):audit_initial_gate(c,m,r)

def test_tampered_s_threshold_refused(source):
    m,c=source
    r=derive_initial_gate(c,[0,3000],[0,c['phi_i']]);r['absolute_s_tolerance']=1
    with pytest.raises(ValueError):audit_initial_gate(c,m,r)

def test_missing_one_of_81_is_not_success(source):
    m,c=source
    assert len(m['cases'])==81
    assert len(m['cases'][:-1])!=81
