#!/usr/bin/env python3
"""C52 pinned CLASS observer: C39 physical veto + C43 phases + C45 COMMIT + C50 terminal DERIV.

No extra derivative/background calls, no physical veto modifications.
Static source lock is NOT an executed CLASS solution.
"""
from __future__ import annotations
import argparse,difflib,hashlib,json,subprocess
from pathlib import Path
import c43_ndf15_patcher as c43

UPSTREAM='e85808324f51fc694d12e3ed7439552a3c3f9540'
PINNED_BG='08f6bad70c6c479bc5d6946d2a6332263bca47f8a8d7f7dcc87d9c93df681027'
PINNED_NDF='0d293723510171ae9a732c80da32adb9ee52701f'
C43_COMMIT='''    if (rims_c43_trace_enabled()) {
      fprintf(stderr,"RIMS_C43_NDF_TRACE_V1 kind=COMMIT x=%.17g accepted=%d failed=%d order=%d\\n",t,stepstat[0],stepstat[1],k);
      fflush(stderr);
    }'''
C45_INSERT='''
    /* C52: full state exactly after NDF15 COMMIT; never reevaluate derivative. */
    if (getenv("RIMS_C45_COMMIT_STATE_TRACE") != NULL &&
        strcmp(getenv("RIMS_C45_COMMIT_STATE_TRACE"),"1") == 0) {
      int c52_i;
      fprintf(stderr,"RIMS_C45_COMMITTED_STATE_V1 kind=COMMIT_STATE x=%a n=%d seq=%d yhex=",t,neq,stepstat[0]);
      for (c52_i=1;c52_i<=neq;c52_i++) {
        if (c52_i>1) fputc(',',stderr);
        fprintf(stderr,"%a",y[c52_i]);
      }
      fputc('\\n',stderr);
      fflush(stderr);
    }'''
BG_HEAD='#include "background.h"'
DERIV_NAME='int background_derivs('
BG_CALL='''  class_call(background_functions(pba, a, y, normal_info, pvecback),
             pba->error_message,
             error_message);'''
RETURN='  return _SUCCESS_;'
C50_INSERT='''  /* C52: only a fully successful background_derivs() emits DERIV. */
  if ((pba->has_rims == _TRUE_) &&
      (getenv("RIMS_C46_PASSIVE_TRACE") != NULL) &&
      (strcmp(getenv("RIMS_C46_PASSIVE_TRACE"),"1") == 0)) {
    int c52_i;
    fprintf(stderr,"RIMS_C46_DERIV_EVAL_V1 kind=DERIV x=%a n=%d yhex=",loga,pba->bi_size);
    for (c52_i=0;c52_i<pba->bi_size;c52_i++) {
      if (c52_i!=0) fputc(',',stderr);
      fprintf(stderr,"%a",y[c52_i]);
    }
    fprintf(stderr," H=%a Vpp=%a rho_idm=%a phi=%a ratio=%a\\n",
      pvecback[pba->index_bg_H],pvecback[pba->index_bg_ddV_scf],
      pvecback[pba->index_bg_rho_idm],pvecback[pba->index_bg_phi_scf],
      pvecback[pba->index_bg_rims_stability_margin]);
    fflush(stderr);
  }
'''
BG_INCLUDES='\n#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def insertions_only(before,after):
    return all(tag in ('equal','insert') for tag,*_ in difflib.SequenceMatcher(
        None,before.splitlines(keepends=True),after.splitlines(keepends=True),autojunk=False).get_opcodes())
def compose(bg:bytes,nd:bytes):
    if sha(bg)!=PINNED_BG or c43.git_blob_sha(nd)!=PINNED_NDF:
        raise ValueError('C52 source is not exact pinned C39 background / original NDF15')
    b=bg.decode('utf8','strict');n=nd.decode('utf8','strict')
    n43=c43.instrument(n,require_pinned=True)
    if n43.count(C43_COMMIT)!=1 or 'RIMS_C45_COMMITTED_STATE_V1' in n43:
        raise ValueError('C43 exact COMMIT anchor missing/duplicated')
    n52=n43.replace(C43_COMMIT,C43_COMMIT+C45_INSERT,1)
    if b.count(BG_HEAD)!=1 or b.count(DERIV_NAME)!=1 or b.count(BG_CALL)!=1 or 'RIMS_C46_DERIV_EVAL_V1' in b:
        raise ValueError('C39 background anchor mismatch or duplicate observer')
    start=b.index(DERIV_NAME)
    end=b.find('\n}',start)
    if end<start:raise ValueError('No terminal derivative body')
    body=b[start:end]
    if body.count(RETURN)!=1 or body.index(RETURN)<body.index(BG_CALL):
        raise ValueError('Derivative complete success exit ambiguous')
    if 'return _FAILURE_;' in body or 'goto ' in body:
        raise ValueError('Unexpected alternate control-flow in derivative body')
    insert=start+body.index(RETURN)
    b52=b[:insert]+C50_INSERT+b[insert:]
    b52=b52.replace(BG_HEAD,BG_HEAD+BG_INCLUDES,1)
    if any(not insertions_only(old,new) for old,new in ((b,b52),(n,n52))):
        raise ValueError('C52 observer modified native physics lines')
    if b52.count('RIMS_C39_TERMS_V1')!=1 or b52.count('RIMS_C46_DERIV_EVAL_V1')!=1:
        raise ValueError('Original native veto missing or passive logger duplicated')
    receipt={'schema':'RIMS_C52_SOURCE_LOCKED_NATIVE_PHASE_STACK_V1',
       'original_c39_background_sha256':sha(bg),'original_ndf_git_blob_sha1':c43.git_blob_sha(nd),
       'upstream_commit':UPSTREAM,'background_output_sha256':sha(b52.encode()),
       'ndf_output_sha256':sha(n52.encode()),'c43_only_sha256':sha(n43.encode()),
       'insertion_only':True,'original_veto_unchanged':True,
       'additional_physical_evaluations':0,
       'terminal_derivative_success_only':True,
       'native_CLASS_executed':False,'accepted_g_observed':False}
    c43_receipt={'original_source_blob_sha1':PINNED_NDF,
        'source_after_sha256':sha(n43.encode()),'native_CLASS_executed':False,
        'trace_env_value_required':'1'}
    return b52.encode(),n52.encode(),receipt,c43_receipt
def stage(source:Path,dest:Path,install=False):
    source=source.resolve(strict=True)
    head=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
    if head!=UPSTREAM:raise ValueError('Wrong frozen CLASS upstream revision')
    bgfile=source/'source/background.c';ndfile=source/'tools/evolver_ndf15.c'
    bg=bgfile.read_bytes();nd=ndfile.read_bytes()
    outbg,outnd,receipt,c43_receipt=compose(bg,nd)
    if dest.exists():raise FileExistsError('Never overwrite staging or prior audit data')
    dest.mkdir(parents=True)
    (dest/'original_background.c').write_bytes(bg)
    (dest/'original_ndf15.c').write_bytes(nd)
    (dest/'instrumented_background.c').write_bytes(outbg)
    (dest/'instrumented_ndf15.c').write_bytes(outnd)
    if install:
        if bgfile.read_bytes()!=bg or ndfile.read_bytes()!=nd:raise RuntimeError('Source changed during installation')
        bgfile.write_bytes(outbg);ndfile.write_bytes(outnd)
        receipt['applied_to_temporary_CLASS_checkout']=True
    else:receipt['applied_to_temporary_CLASS_checkout']=False
    (dest/'source_lock.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    (dest/'c43_source_lock.json').write_text(json.dumps(c43_receipt,indent=2,sort_keys=True)+'\n')
    return receipt
def main():
    p=argparse.ArgumentParser()
    p.add_argument('--class-source',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--install',action='store_true')
    a=p.parse_args()
    print(json.dumps(stage(a.class_source,a.out,install=a.install),indent=2))
if __name__=='__main__':main()
