#!/usr/bin/env python3
"""C55 source-locked C54 auxiliary observer added to pinned C52 CLASS stack.

Only logs fields already computed in a successful derivative; never computes new
physical background quantities, never alters the original stability veto.
The native CLASS compilation and run are independent acceptance gates.
"""
from __future__ import annotations
import argparse,difflib,hashlib,json,subprocess
from pathlib import Path
import c52_instrument as c52

BASE_MARKER='RIMS_C46_DERIV_EVAL_V1'
AUX_MARKER='RIMS_C54_DERIV_AUX_V1'
FUNCTION='int background_derivs('
EXIT='  return _SUCCESS_;'
TRACE='''  /* C55: passively log runtime scalar metadata ONLY after terminal
   * derivative success and after original RIMS physical veto. */
  if (pba->has_rims == _TRUE_ &&
      getenv("RIMS_C46_PASSIVE_TRACE") != NULL &&
      strcmp(getenv("RIMS_C46_PASSIVE_TRACE"),"1") == 0 &&
      getenv("RIMS_C54_AUX_TRACE") != NULL &&
      strcmp(getenv("RIMS_C54_AUX_TRACE"),"1") == 0) {
    fprintf(stderr,"RIMS_C54_DERIV_AUX_V1 kind=DERIV_AUX x=%a V=%a phi_prime=%a rho_scf=%a iphi=%d iphip=%d lam=%a palpha=%a pA=%a pB=%a alpha_U=%a phi_t=%a has_dcdm=%d has_dr=%d has_fld=%d\\n",
        loga,pvecback[pba->index_bg_V_scf],pvecback[pba->index_bg_phi_prime_scf],
        pvecback[pba->index_bg_rho_scf],pba->index_bi_phi_scf,pba->index_bi_phi_prime_scf,
        pba->scf_parameters[0],pba->scf_parameters[1],pba->scf_parameters[2],
        pba->scf_parameters[3],pba->rims_alpha_U,pba->rims_phi_transition,
        pba->has_dcdm,pba->has_dr,pba->has_fld);
    fflush(stderr);
  }
'''
def sha(b):return hashlib.sha256(b).hexdigest()
def additive(old,new):
    return all(tag in ('equal','insert') for tag,*_ in difflib.SequenceMatcher(
        None,old.splitlines(keepends=True),new.splitlines(keepends=True),
        autojunk=False).get_opcodes())
def instrument(bg52:str)->str:
    if bg52.count(BASE_MARKER)!=1 or AUX_MARKER in bg52:
        raise ValueError('C52 derivative-success marker missing or C54 duplicate')
    if bg52.count(FUNCTION)!=1:raise ValueError('Frozen derivative function is not unique')
    begin=bg52.index(FUNCTION);end=bg52.find('\n}',begin)
    if end<begin:raise ValueError('Frozen derivative function end missing')
    body=bg52[begin:end]
    if body.count(EXIT)!=1 or body.index(BASE_MARKER)>body.index(EXIT):
        raise ValueError('C52 terminal success anchor is wrong')
    pos=begin+body.index(EXIT)
    updated=bg52[:pos]+TRACE+bg52[pos:]
    if not additive(bg52,updated) or updated.count(AUX_MARKER)!=1:
        raise ValueError('Unexpected source modification')
    return updated
def compose(bg0:bytes,nd0:bytes):
    bg52,nd52,rec52,rec43=c52.compose(bg0,nd0)
    bg55=instrument(bg52.decode('utf8','strict')).encode('utf8')
    receipt={'schema':'RIMS_C55_RUNTIME_AUX_SOURCE_LOCK_V1',
       'original_c39_background_sha256':rec52['original_c39_background_sha256'],
       'original_ndf_git_blob_sha1':rec52['original_ndf_git_blob_sha1'],
       'upstream_commit':rec52['upstream_commit'],
       'c52_background_sha256':rec52['background_output_sha256'],
       'c52_ndf_sha256':rec52['ndf_output_sha256'],
       'background_output_sha256':sha(bg55),
       'ndf_output_sha256':sha(nd52),
       'insertion_only':True,'original_veto_unchanged':True,
       'additional_physical_evaluations':0,
       'terminal_derivative_success_only':True,
       'native_CLASS_executed':False,'accepted_g_observed':False}
    return bg55,nd52,receipt,rec43
def stage(source:Path,dest:Path,install=False):
    root=source.resolve(strict=True)
    head=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()
    if head!=c52.UPSTREAM:raise ValueError('Not original pinned CLASS commit')
    bgfile=root/'source/background.c';ndfile=root/'tools/evolver_ndf15.c'
    bg0=bgfile.read_bytes();nd0=ndfile.read_bytes()
    bg55,nd55,receipt,rec43=compose(bg0,nd0)
    if dest.exists():raise FileExistsError('Never overwrite previous provenance')
    dest.mkdir(parents=True)
    (dest/'background_before.c').write_bytes(bg0)
    (dest/'ndf15_before.c').write_bytes(nd0)
    (dest/'background_C55.c').write_bytes(bg55)
    (dest/'ndf15_C55.c').write_bytes(nd55)
    if install:
        if bgfile.read_bytes()!=bg0 or ndfile.read_bytes()!=nd0:
            raise RuntimeError('Concurrent pinned CLASS source drift')
        bgfile.write_bytes(bg55);ndfile.write_bytes(nd55)
        receipt['applied_to_temporary_CLASS_checkout']=True
    else:receipt['applied_to_temporary_CLASS_checkout']=False
    (dest/'source_lock.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    (dest/'c43_source_lock.json').write_text(json.dumps(rec43,sort_keys=True,indent=2)+'\n')
    return receipt
def main():
    p=argparse.ArgumentParser()
    p.add_argument('--class-source',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--install',action='store_true')
    a=p.parse_args()
    print(json.dumps(stage(a.class_source,a.out,install=a.install),sort_keys=True,indent=2))
if __name__=='__main__':main()
