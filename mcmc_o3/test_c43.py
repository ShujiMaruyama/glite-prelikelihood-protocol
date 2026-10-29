from pathlib import Path
import contextlib,subprocess,sys,os,pytest,math,re,difflib
ROOT=Path(__file__).resolve().parents[1]
LIB=Path(__file__).resolve().parent if (Path(__file__).resolve().parent/'c43_ndf15_patcher.py').is_file() else ROOT/'src'
sys.path.insert(0,str(LIB))
import c43_ndf15_patcher as p
import c43_phase_audit as a

# A deliberately minimal *synthetic* stand-in. This is NOT the CLASS evolver.
MOCK='''#include "evolver_ndf15.h"
#include <math.h>
#define class_call(e,...) do {if ((e)!=0) return 1;} while (0)
#define _FALSE_ 0
static void eqvec(double *src,double *dst,int count) {for (int i=1;i<=count;i++) dst[i]=src[i];}
static int simulate_derivs(double x, double *y, double *dy,void *work, char *err) {
  (void)y;(void)dy;(void)work;(void)err;
  if(x > -22.0) {
    fprintf(stderr,"RIMS_C39_TERMS_V1 a=%.17g ratio=-1.006e-10 tolerance=1e-10\\n",exp(x));
    return 1;
  }
  return 0;
}
static int run_mock(double x_ini,double x_final) {
  double t0,tfinal,tnew=0,t=0;double ynew[2]={0,0};double y[2]={0,0};double f0[2]={0,0};
  int stepstat[6]={0,0,0,0,0,0},k=1,iter=1,Jcurrent=0,neq=1;
  char error_message[50]={0};void *parameters_and_workspace_for_derivs=NULL;
  int (*derivs)(double,double *,double *,void *,char *)=simulate_derivs;
  t0 = x_ini;
  tfinal = x_final;
  (void)tfinal;(void)Jcurrent;
  for (int j=0;j<3;j++) {
    tnew=t0+.10*(j+1);
    for (iter=1;iter<=1;iter++) {
          class_call((*derivs)(tnew,ynew+1,f0+1,parameters_and_workspace_for_derivs,error_message),
                 error_message,error_message);
    }
    /* End of conditionless FOR loop */
    stepstat[0] += 1;
    t = tnew;
    eqvec(ynew,y,neq);
    Jcurrent = _FALSE_;
  }
  return 0;
}
int main(void) { return run_mock(-22.15,-20.0); }
'''

def synthetic_run(tmp_path,mode='1'):
    patched=p.instrument(MOCK,require_pinned=False)
    (tmp_path/'evolver_ndf15.h').write_text('/* Mock-only header */\n')
    (tmp_path/'mock.c').write_text(patched)
    exe=tmp_path/'synthetic'
    cc=subprocess.run(['gcc','-Wall','-Wextra','-Werror','-std=c11','-O0','-I'+str(tmp_path),str(tmp_path/'mock.c'),'-lm','-o',str(exe)],capture_output=True,text=True)
    assert cc.returncode==0,cc.stderr
    env=dict(os.environ,RIMS_C43_NDF_TRACE=mode)
    return subprocess.run([str(exe)],capture_output=True,text=True,env=env)

def test_trace_disabled_by_default(tmp_path):
    r=synthetic_run(tmp_path,'0')
    assert r.returncode==1
    assert p.PREFIX not in r.stderr
    assert 'RIMS_C39_TERMS_V1' in r.stderr

def test_source_guard():
    with pytest.raises(ValueError,match='blob'):
        p.instrument(MOCK,require_pinned=True)

def test_c43_instrument_does_not_change_original(tmp_path):
    original=MOCK
    instrumented=p.instrument(original,require_pinned=False)
    assert original==MOCK
    for k in (p.BEGIN,p.TRIAL,p.GATE,p.COMMIT):assert k in instrumented
    with pytest.raises(ValueError,match='Already traced'):
        p.instrument(instrumented,require_pinned=False)

def test_duplicate_anchor_fail_closed():
    with pytest.raises(ValueError,match='duplicate'):
        p.instrument(MOCK+'\n'+p.COMMIT,require_pinned=False)

def test_mock_compiles_and_phase_acceptance_audited(tmp_path):
    r=synthetic_run(tmp_path)
    assert r.returncode==1
    d=a.parse(r.stderr)
    assert d['status']=='FAILED_NEWTON_TRIAL_CONFIRMED'
    assert d['accepted_gate_count_in_final_evolver']==1
    assert d['committed_step_count_in_final_evolver']==1
    assert d['last_committed_background_g_measured'] is False
    assert d['same_accepted_trajectory_root_bracket_proved'] is False
    assert d['physical_stability_proved'] is False
    assert d['veto_a']>d['last_committed_a']

def test_phase_parser_rejects_no_veto():
    with pytest.raises(ValueError,match='Exactly one'):
        a.parse('RIMS_C43_NDF_TRACE_V1 kind=BEGIN xini=-23 xfinal=0')

def test_phase_parser_rejects_dup_key():
    with pytest.raises(ValueError,match='Duplicate'):
        a.parse_event('RIMS_C43_NDF_TRACE_V1 kind=BEGIN xini=1 xini=2 xfinal=3')

def test_phase_parser_rejects_unknown_kind():
    with pytest.raises(ValueError,match='Unknown'):
        a.parse_event('RIMS_C43_NDF_TRACE_V1 kind=BAD x=4')

def test_phase_parser_rejects_nan():
    with pytest.raises(ValueError,match='Nonfinite'):
        a.parse_event('RIMS_C43_NDF_TRACE_V1 kind=TRIAL x=nan accepted=0 failed=0 order=1 iter=1')

def test_phase_parser_rejects_negative_counter():
    with pytest.raises(ValueError,match='Negative'):
        a.parse_event('RIMS_C43_NDF_TRACE_V1 kind=TRIAL x=0 accepted=-1 failed=0 order=1 iter=1')

def test_phase_veto_different_loga_rejected(tmp_path):
    r=synthetic_run(tmp_path)
    with pytest.raises(ValueError,match='does not match'):
        a.parse(re.sub(r'(kind=TRIAL x=)[^ ]+( accepted=1)',r'\g<1>-21.92\g<2>',r.stderr))

def test_phase_no_fake_commit(tmp_path):
    r=synthetic_run(tmp_path)
    false_commit='RIMS_C43_NDF_TRACE_V1 kind=COMMIT x=-21.95 accepted=2 failed=0 order=1\n'
    t=r.stderr.replace('RIMS_C39_TERMS_V1 ',false_commit+'RIMS_C39_TERMS_V1 ')
    with pytest.raises(ValueError,match='Veto must immediately follow'):
        a.parse(t)

def test_gate_without_commit_is_not_evidence(tmp_path):
    r=synthetic_run(tmp_path)
    t='\n'.join(x for x in r.stderr.splitlines() if 'kind=COMMIT ' not in x)
    d=a.parse(t)
    assert d['accepted_gate_count_in_final_evolver']==1
    assert d['committed_step_count_in_final_evolver']==0
    assert d['accept_gate_without_committed_state_count']==1
    assert d['last_committed_a'] is None

def test_bad_veto_threshold_rejected(tmp_path):
    r=synthetic_run(tmp_path)
    with pytest.raises(ValueError,match='strict'):
        a.parse(r.stderr.replace('tolerance=1e-10','tolerance=1e-8'))

def test_rejected_candidate_not_same_as_accepted(tmp_path):
    r=synthetic_run(tmp_path)
    assert 'kind=TRIAL' in r.stderr and 'kind=COMMIT' in r.stderr
    d=a.parse(r.stderr)
    assert d['last_committed_loga']!=d['latest_failed_trial_loga']

def test_phase_source_identity_readonly():
    assert p.PINNED_NDF15_BLOB=='0d293723510171ae9a732c80da32adb9ee52701f'
    assert p.PINNED_UPSTREAM=='e85808324f51fc694d12e3ed7439552a3c3f9540'


def test_source_telemetry_is_insertions_only():
    old=MOCK.splitlines(keepends=True)
    new=p.instrument(MOCK,require_pinned=False).splitlines(keepends=True)
    assert all(tag in ('equal','insert') for tag,_,_,_,_ in difflib.SequenceMatcher(a=old,b=new,autojunk=False).get_opcodes())
    assert new!=old
