#!/usr/bin/env python3
"""RIMS C42-A source-only instrumentation preparation; NO CLASS executions.

Fail closed on unexpected source lineages and identical-anchor changes. Emits a
non-invasive (in arithmetic/control-flow terms) diagnostic source overlay only.
Does NOT claim unchanged floating-point trajectories, which require auditing.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

BACKGROUND_C39_SHA256 = '08f6bad70c6c479bc5d6946d2a6332263bca47f8a8d7f7dcc87d9c93df681027'
NDF15_UPSTREAM_GIT_BLOB_SHA1 = '0d293723510171ae9a732c80da32adb9ee52701f'
C42A_PREFIX = 'RIMS_C42A_'

def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def git_blob_sha1(b: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest()

# All anchors are from fixed CLASS upstream e858083... (and its C39 overlay).
BACKGROUND_HOOKS = [
 ('PRE_INITIAL_CONDITIONS',
 '''  /** - impose initial conditions with background_initial_conditions() */
  class_call(background_initial_conditions(ppr,pba,pvecback,pvecback_integration,&(loga_ini)),
             pba->error_message,
             pba->error_message);
''',
 '''  /** RIMS C42-A diagnostic: source/initialization context only. */
  if (pba->has_rims == _TRUE_) {
    fprintf(stderr,"RIMS_C42A_INIT_ENTER_V1\\n"); fflush(stderr);
  }
''',
 'before'),
 ('POST_INITIAL_CONDITIONS',
 '''  /** - Determine output vector */
''',
 '''  /** RIMS C42-A: initial conditions returned without the native veto. */
  if (pba->has_rims == _TRUE_) {
    fprintf(stderr,"RIMS_C42A_INIT_OK_V1 a_ini=%.17g\\n",exp(loga_ini)); fflush(stderr);
  }
''',
 'before'),
 ('CALLBACK',
 '''  class_call(background_functions(pba, a, y, long_info, bg_table_row),
             pba->error_message,
             pba->error_message);
''',
 '''  /* C42-A: callback has been called by ndf15 AFTER accepted step;
     sample at the requested output grid node may be INTERPOLATED. */
  if (pba->has_rims == _TRUE_ && index_loga < 16) {
    fprintf(stderr,"RIMS_C42A_OUTPUT_OK_V1 index=%d a=%.17g "
            "H=%.17g rho_idm=%.17g Vpp=%.17g "
            "mass_curvature=%.17g s=%.17g ratio=%.17g\\n",
            index_loga,a,bg_table_row[pba->index_bg_H],
            bg_table_row[pba->index_bg_rho_idm],
            bg_table_row[pba->index_bg_ddV_scf],
            rims_mass_curvature(pba,y[pba->index_bi_phi_scf]),
            bg_table_row[pba->index_bg_rims_s],
            bg_table_row[pba->index_bg_rims_stability_margin]);
    fflush(stderr);
  }
''',
 'after'),
]
NDF_HOOKS = [
 ('NDF_INITIAL_DERIVATIVE',
 '''  for(ii=0;ii<6;ii++) stepstat[ii] = 0;
''',
 '''  /* C42-A diagnostic, before the first derivative call. */
  fprintf(stderr,"RIMS_C42A_NDF_ENTER_V1 t0=%.17g a0=%.17g\\n",t0,exp(t0));
  fflush(stderr);
''',
 'after'),
 ('ACCEPTED_STEP',
 '''    stepstat[0] += 1;

    /* Update dif: */
''',
 '''    /* C42-A: this point is after successful local error acceptance;
       a later output callback can nevertheless reject interpolation. */
    if (stepstat[0] <= 64) {
      fprintf(stderr,"RIMS_C42A_NDF_STEP_OK_V1 n=%d a=%.17g\\n",stepstat[0],exp(tnew));
      fflush(stderr);
    }
''',
 'after_match_first_line'),
]

def inject(original: str, hooks: list[tuple[str,str,str,str]], label: str):
    if C42A_PREFIX in original:
        raise ValueError(f'{label}: pre-existing C42-A markers (cannot overlay twice)')
    out=original
    inserts=[]
    for name,anchor,insertion,position in hooks:
        if original.count(anchor) != 1:
            raise ValueError(f'{label}: ambiguous/missing {name} anchor (found {original.count(anchor)})')
        if position == 'before':
            replacement=insertion+anchor
        elif position == 'after':
            replacement=anchor+insertion
        elif position == 'after_match_first_line':
            first, remainder=anchor.split('\n',1)
            replacement=first+'\n'+insertion+remainder
        else:
            raise ValueError('invalid hook')
        if out.count(anchor)!=1:
            raise ValueError(f'{label}: overlapping hook anchors')
        out=out.replace(anchor,replacement,1)
        inserts.append(insertion)
    recovered=out
    for insertion in reversed(inserts):
        if recovered.count(insertion)!=1:
            raise AssertionError(f'{label}: reversible exact insertion not established')
        recovered=recovered.replace(insertion,'',1)
    if recovered!=original:
        raise AssertionError(f'{label}: source changed outside declared diagnostic additions')
    if out.count(C42A_PREFIX)!=len(hooks):
        raise AssertionError(f'{label}: unexpected marker multiplicity')
    return out

def prepare(bkg: bytes, ndf: bytes):
    if sha(bkg) != BACKGROUND_C39_SHA256:
        raise ValueError('C39 instrumented background.c SHA256 not pinned')
    if git_blob_sha1(ndf) != NDF15_UPSTREAM_GIT_BLOB_SHA1:
        raise ValueError('NDF15 upstream git blob SHA1 not pinned')
    bs=bkg.decode('utf-8')
    ns=ndf.decode('utf-8')
    if 'RIMS_C39_TERMS_V1' not in bs or 'pba->rims_stability_tolerance' not in bs:
        raise ValueError('missing original physical gate/C39 overlay')
    if 'if (err>rtol)' not in ns or '(*output)(t_vec[next]' not in ns:
        raise ValueError('unrecognized adaptive solver acceptance/output semantics')
    bo=inject(bs,BACKGROUND_HOOKS,'background.c')
    no=inject(ns,NDF_HOOKS,'evolver_ndf15.c')
    return bo.encode('utf-8'),no.encode('utf-8')

def run(background: Path, ndf: Path, out_dir: Path):
    if out_dir.exists():
        raise FileExistsError(f'refusing overwrite: {out_dir}')
    bkg=background.read_bytes()
    ndf_raw=ndf.read_bytes()
    bo,no=prepare(bkg,ndf_raw)
    out_dir.mkdir(parents=True)
    bp=out_dir/'background.c';np=out_dir/'evolver_ndf15.c'
    bp.write_bytes(bo);np.write_bytes(no)
    info={
     'schema':'RIMS_C42A_SOURCE_ONLY_OVERLAY_AUDIT_V1',
     'status':'SOURCE_INSTRUMENTATION_PREPARED_ONLY',
     'physical_class_computes':0,
     'original_case':'rims_002',
     'background_source_sha256_before':sha(bkg),
     'background_source_sha256_after':sha(bo),
     'ndf_source_git_blob_sha1_before':git_blob_sha1(ndf_raw),
     'ndf_source_sha256_before':sha(ndf_raw),
     'ndf_source_sha256_after':sha(no),
     'byte_exact_reversibility':True,
     'printed_trial_values_promoted_to_accepted':False,
     'output_on_interpolation_grid_not_step_endpoint':True,
     'source_output_rows_max_per_background_solve':16,
     'source_accepted_steps_max_per_ndf_invocation':64,
     'numerical_solution_or_convergence_certified':False,
     'native_execution_or_solver_build_certified':False,
     'unchanged_floating_point_trajectory_certified':False,
     'changes_only':['stderr source context markers','stderr first 64 accepted-step markers','stderr first 16 output-grid callbacks'],
     'evidence_status':'STATIC_SOURCE_GATE_ONLY'
    }
    (out_dir/'audit.json').write_text(json.dumps(info,indent=2,sort_keys=True)+'\n')
    return info

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--background',required=True,type=Path)
    p.add_argument('--ndf15',required=True,type=Path)
    p.add_argument('--out',required=True,type=Path)
    a=p.parse_args()
    v=run(a.background,a.ndf15,a.out)
    print('C42A SOURCE ONLY: NO CLASS COMPUTES',v['background_source_sha256_after'],v['ndf_source_sha256_after'])
if __name__=='__main__':main()
