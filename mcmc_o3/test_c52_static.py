"""C52 source-lock regressions; no CLASS.compute is called in these tests."""
import hashlib,sys,pytest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import c43_ndf15_patcher as c43
import c52_instrument as inst
import c52_native_audit as audit
import test_c43

BG='''#include "background.h"
#define _SUCCESS_ 0
/* RIMS_C39_TERMS_V1 */
int background_derivs(double loga,double*y,double*dy,void* parameters_and_workspace,char*error_message) {
  struct background_parameters_and_workspace * pbpaw=parameters_and_workspace;
  struct background *pba=pbpaw->pba;
  double *pvecback=pbpaw->pvecback;
  double a=exp(loga);
  int normal_info=0;
  class_call(background_functions(pba, a, y, normal_info, pvecback),
             pba->error_message,
             error_message);
  dy[0]=y[0]+1;
  return _SUCCESS_;
}
'''
def setup_mock(monkeypatch):
    blob=c43.git_blob_sha(test_c43.MOCK.encode())
    monkeypatch.setattr(inst,'PINNED_BG',inst.sha(BG.encode()))
    monkeypatch.setattr(inst,'PINNED_NDF',blob)
    monkeypatch.setattr(c43,'PINNED_NDF15_BLOB',blob)

def test_original_source_pin_refuses_other_code():
    with pytest.raises(ValueError,match='not exact pinned'):
        inst.compose(b'other',b'other')
def test_instrumented_source_is_additive_and_exact(monkeypatch):
    setup_mock(monkeypatch)
    bg,nd,receipt,c43receipt=inst.compose(BG.encode(),test_c43.MOCK.encode())
    assert receipt['insertion_only'] is True
    assert receipt['original_veto_unchanged'] is True
    assert receipt['additional_physical_evaluations']==0
    assert bg.count(b'RIMS_C46_DERIV_EVAL_V1')==1
    assert nd.count(b'RIMS_C45_COMMITTED_STATE_V1')==1
    assert nd.count(b'RIMS_C43_NDF_TRACE_V1 kind=COMMIT')==1
    assert c43receipt['source_after_sha256']==receipt['c43_only_sha256']
def test_reject_existing_partial_log(monkeypatch):
    setup_mock(monkeypatch)
    tampered=BG.replace('dy[0]', '/* RIMS_C46_DERIV_EVAL_V1 */ dy[0]')
    monkeypatch.setattr(inst,'PINNED_BG',inst.sha(tampered.encode()))
    with pytest.raises(ValueError,match='duplicate observer'):
        inst.compose(tampered.encode(),test_c43.MOCK.encode())
def test_signed_zero_does_not_match():
    assert audit.bits('0x0p+0')!=audit.bits('-0x0p+0')
def test_reject_decimal_and_nonfinite_fields():
    for v in ['0.0','nan','0x1p+1024']:
        with pytest.raises(ValueError):audit.bits(v)
def test_refuse_partial_derivative():
    with pytest.raises(ValueError):
        audit.parsed('RIMS_C46_DERIV_EVAL_V1 kind=DERIV x=0x1p+0','deriv')
def test_pinned_input_refuse_parameter_relaxation():
    with pytest.raises(ValueError,match='physical parameters'):
        audit.verify_provenance({'rims_enabled':'no'},{},{},b'', '.', '.')
def test_no_physical_stability_claim_from_static_scripts():
    assert 'accepted_state_stability_proven' in Path(audit.__file__).read_text()
    assert 'native_CLASS_executed' in Path(inst.__file__).read_text()
