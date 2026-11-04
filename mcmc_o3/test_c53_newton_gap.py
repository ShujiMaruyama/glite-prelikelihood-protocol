"""C53 source-locked phase provenance regression; no CLASS native compute."""
import sys, pytest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import c53_newton_gap_audit as a
def cm(seq='1',x='0x1p+0',y='0x1.0000000000001p+0'):
    return f'RIMS_C45_COMMITTED_STATE_V1 kind=COMMIT_STATE x={x} n=1 seq={seq} yhex={y}'
def dv(x='0x1p+0',y='0x1p+0'):
    return f'RIMS_C46_DERIV_EVAL_V1 kind=DERIV x={x} n=1 yhex={y} H=0x1p+0 Vpp=0x1p-100 rho_idm=0x1p-10 phi=0x1p+0 ratio=0x1p-10'
def test_c44_no_vector_not_promoted():
    s='RIMS_C43_NDF_TRACE_V1 kind=COMMIT x=1 accepted=1 failed=0 order=1'
    assert a.classify(s)['status']=='NO_ACCEPTED_VECTOR_TELEMETRY'
def test_one_ulp_gap_rejected_as_exact():
    r=a.classify(dv()+'\n'+cm())
    assert (r['last_derivative_input_unequal'],r['last_derivative_input_exact'])==(1,0)
    assert r['per_step'][0]['mismatching_components']==1
    assert r['accepted_g_measured_by_this_program'] is False
def test_exact_state_only_reports_matching_state():
    r=a.classify(dv()+'\n'+cm(y='0x1p+0'))
    assert r['last_derivative_input_exact']==1
    assert not r['certifies_physical_stability']
def test_old_deriv_not_carried_over():
    r=a.classify(dv()+'\n'+cm(y='0x1p+0')+'\n'+cm(seq='2',x='0x1.1p+0'))
    assert r['missing_last_derivative']==1
def test_different_t_not_coerced():
    r=a.classify(dv(x='0x1p+0')+'\n'+cm(x='0x1.2p+0'))
    assert r['missing_last_derivative']==1
def test_sign_zero_is_distinct():
    r=a.classify(dv(x='-0x0p+0')+'\n'+cm(x='0x0p+0'))
    assert r['missing_last_derivative']==1
@pytest.mark.parametrize('tamper',['nan','1.0','0x1p+1024'])
def test_bad_hex_fails(tamper):
    with pytest.raises(ValueError):a.classify(dv(y=tamper)+'\n'+cm())
def test_wrong_sequence_rejected():
    with pytest.raises(ValueError):a.classify(cm(seq='2'))
def test_duplicate_field_rejected():
    with pytest.raises(ValueError):a.classify(cm()+' yhex=0x1p0')
def test_synthetic_deriv_does_not_create_accepted_mass():
    r=a.classify(dv()+'\n'+cm(y='0x1p+0'))
    assert 'accepted_g_observations' not in r
    assert r['trial_or_derivative_values_are_not_accepted_values'] is True
