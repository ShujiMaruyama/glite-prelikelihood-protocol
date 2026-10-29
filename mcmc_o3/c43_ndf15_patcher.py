#!/usr/bin/env python3
"""C43 opt-in source-locked NDF15 execution-phase tracing; never edits input.

Only inserts stderr metadata markers; no calls to the background functions,
changes to adaptive steps, RIMS equations, solver tolerance, or veto settings.
Even a passing instrumentation test does not certify a native CLASS run.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

PINNED_UPSTREAM = 'e85808324f51fc694d12e3ed7439552a3c3f9540'
PINNED_NDF15_BLOB = '0d293723510171ae9a732c80da32adb9ee52701f'
PREFIX = 'RIMS_C43_NDF_TRACE_V1'
ENV = 'RIMS_C43_NDF_TRACE'
INCLUDE = '#include "evolver_ndf15.h"'
BEGIN = '  t0 = x_ini;\n  tfinal = x_final;'
TRIAL = '''          class_call((*derivs)(tnew,ynew+1,f0+1,parameters_and_workspace_for_derivs,error_message),
                 error_message,error_message);'''
GATE = '    /* End of conditionless FOR loop */\n    stepstat[0] += 1;'
COMMIT = '    t = tnew;\n    eqvec(ynew,y,neq);\n    Jcurrent = _FALSE_;'


def git_blob_sha(raw:bytes)->str:
    return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\x00'+raw).hexdigest()


def instrument(source:str, *, require_pinned=True)->str:
    if require_pinned and git_blob_sha(source.encode('utf-8')) != PINNED_NDF15_BLOB:
        raise ValueError('NDF15 original pinned blob does not match: STOP')
    if PREFIX in source:
        raise ValueError('Already traced: no duplicate instrumentation allowed')
    for key in (INCLUDE,BEGIN,TRIAL,GATE,COMMIT):
        if source.count(key)!=1:
            raise ValueError('Missing or duplicate frozen NDF15 source anchor: '+key[:65])
    include = '''
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
/* C43 strictly opt-in telemetry; disabled by default. */
static int rims_c43_trace_enabled(void) {
  const char *e = getenv("RIMS_C43_NDF_TRACE");
  return e != NULL && strcmp(e,"1")==0;
}
'''
    source=source.replace(INCLUDE,INCLUDE+include,1)
    source=source.replace(BEGIN,BEGIN+'''
  if (rims_c43_trace_enabled()) {
    fprintf(stderr,"RIMS_C43_NDF_TRACE_V1 kind=BEGIN xini=%.17g xfinal=%.17g\\n",x_ini,x_final);
    fflush(stderr);
  }''',1)
    source=source.replace(TRIAL,'''          if (rims_c43_trace_enabled()) {
            fprintf(stderr,"RIMS_C43_NDF_TRACE_V1 kind=TRIAL x=%.17g accepted=%d failed=%d order=%d iter=%d\\n",tnew,stepstat[0],stepstat[1],k,iter);
            fflush(stderr);
          }
'''+TRIAL,1)
    source=source.replace(GATE,GATE+'''
    if (rims_c43_trace_enabled()) {
      fprintf(stderr,"RIMS_C43_NDF_TRACE_V1 kind=ACCEPT_GATE x=%.17g accepted=%d failed=%d order=%d\\n",tnew,stepstat[0],stepstat[1],k);
      fflush(stderr);
    }''',1)
    source=source.replace(COMMIT,COMMIT+'''
    if (rims_c43_trace_enabled()) {
      fprintf(stderr,"RIMS_C43_NDF_TRACE_V1 kind=COMMIT x=%.17g accepted=%d failed=%d order=%d\\n",t,stepstat[0],stepstat[1],k);
      fflush(stderr);
    }''',1)
    if source.count(PREFIX)!=4:
        raise AssertionError('Exactly four types of event must be instrumented')
    return source


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source',required=True)
    p.add_argument('--out',required=True)
    p.add_argument('--receipt',required=True)
    a=p.parse_args();inp=Path(a.source);out=Path(a.out);receipt=Path(a.receipt)
    if out.exists() or out.resolve()==inp.resolve() or receipt.exists():
        raise FileExistsError('No overwrite of input, output, or receipt')
    before=inp.read_bytes()
    patched=instrument(before.decode('utf-8'),require_pinned=True).encode('utf-8')
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_bytes(patched)
    receipt.parent.mkdir(parents=True,exist_ok=True)
    result={'schema':'RIMS_C43_PHASE_TELEMETRY_SOURCE_AUDIT_V1',
       'upstream_commit':PINNED_UPSTREAM,
       'original_source_blob_sha1':git_blob_sha(before),
       'source_before_sha256':hashlib.sha256(before).hexdigest(),
       'source_after_sha256':hashlib.sha256(patched).hexdigest(),
       'observed_phases':['BEGIN','TRIAL','ACCEPT_GATE','COMMIT'],
       'trace_env_key':ENV,'trace_env_value_required':'1',
       'no_background_function_added':True,
       'physical_veto_unchanged':True,
       'native_CLASS_executed':False,
       'accepted_physical_g_measured':False,
       'numerical_convergence_proved':False}
    receipt.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print('PINNED C43 SOURCE INSTRUMENTATION WRITTEN; NO CLASS EXECUTED')

if __name__=='__main__':main()
