#!/usr/bin/env python3
"""C42-B: fail-closed, build-only verification of the pinned C42-A source overlay.

The prepare stage restores independently audited C42-A source bytes from a
locally rebuilt pinned CLASS tree.  The verify-built stage checks the imported
native extension without calling classy.Class or CLASS.compute.  Neither stage
tries a cosmological integration nor weakens any RIMS stability check.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib
import importlib.machinery
import json
import os
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import c42a_source_probe as a

FIXED={
 'class_commit':'e85808324f51fc694d12e3ed7439552a3c3f9540',
 'case_id':'rims_002',
 'background_before':'08f6bad70c6c479bc5d6946d2a6332263bca47f8a8d7f7dcc87d9c93df681027',
 'ndf_before':'eaa907b6a785a2d29f194ba19e1a28f0c5f9938e59770695bd543aaecc4f1604',
 'background_after':'dbbaa6b24b2b87cc6c058b4313ba026722467f8f23e80e8fde328e60c1467b9d',
 'ndf_after':'c48e0b807df2d0cc2a859e59fc06483cd866bab199b65afb3db66f3b56070f38',
}

def digest(b):return hashlib.sha256(b).hexdigest()

def require(condition,why):
    if not condition:raise ValueError(why)

def verify_original_physics(g):
    # Record the exact original physical veto (no tolerance masking),
    # scalar equation, and source-level timing markers before build.
    require('pvecback[pba->index_bg_rims_stability_margin] < -pba->rims_stability_tolerance' in g,
            'original strict stability veto missing')
    require('3.*pvecback[pba->index_bg_rho_idm]*rims_mass_curvature_value' in g,
            'RIMS physical source term missing')
    require('RIMS_C39_TERMS_V1' in g, 'C39 provenance marker missing')
    require('RIMS_C42A_INIT_ENTER_V1' in g and 'RIMS_C42A_OUTPUT_OK_V1' in g,
            'C42A initialization/output markers missing')

def stage(source:Path,out:Path):
    require(not out.exists(),'output exists; refuse overwrite')
    b=source/'source/background.c'
    n=source/'tools/evolver_ndf15.c'
    require(b.is_file() and n.is_file(),'CLASS source paths missing')
    old_b=b.read_bytes();old_n=n.read_bytes()
    require(digest(old_b)==FIXED['background_before'],'source background.c is not C39 pinned')
    require(digest(old_n)==FIXED['ndf_before'],'source NDF15 is not upstream pinned')
    new_b,new_n=a.prepare(old_b,old_n)
    require(digest(new_b)==FIXED['background_after'],'C42A run #1 background source mismatch')
    require(digest(new_n)==FIXED['ndf_after'],'C42A run #1 NDF source mismatch')
    verify_original_physics(new_b.decode())
    require(new_n.count(b'RIMS_C42A_NDF_STEP_OK_V1')==1,'accepted-step marker multiplicity')
    require(new_n.count(b'RIMS_C42A_NDF_ENTER_V1')==1,'NDF start marker multiplicity')
    out.mkdir(parents=True)
    b.write_bytes(new_b); n.write_bytes(new_n)
    audit={'schema':'RIMS_C42B_NATIVE_COMPILE_ONLY_GATE_V1',
           'state':'C42A_PINNED_INSTRUMENTED_SOURCE_STAGED',
           'class_upstream_commit':FIXED['class_commit'],
           'physical_case':FIXED['case_id'],
           'native_CLASS_computes':0,
           'source_provenance':'C42A GitHub source preflight #1 artifact 12868361304',
           'source_sha256_before':{'background.c':digest(old_b),'evolver_ndf15.c':digest(old_n)},
           'source_sha256_after':{'background.c':digest(new_b),'evolver_ndf15.c':digest(new_n)},
           'native_build_certified':False,
           'native_solver_result_certified':False,
           'numerical_convergence_certified':False,
           'physical_stability_certified':False,
           'stability_tolerance_changed':False,
           'scientific_parameters_changed':False,
           'byte_exact_reversibility':True,
           'accepted_step_diagnostics_executed':False}
    save(out/'audit.json',audit)
    print('C42B PINNED INSTRUMENTATION STAGED; CLASS.compute 0')
    return audit

def save(path:Path,data):
    path.write_text(json.dumps(data,sort_keys=True,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

def verify(source:Path,out:Path):
    audit_path=out/'audit.json'
    require(audit_path.is_file(),'stage audit missing')
    j=json.loads(audit_path.read_text())
    require(j['state']=='C42A_PINNED_INSTRUMENTED_SOURCE_STAGED','state mismatch')
    require(j['native_CLASS_computes']==0,'unexpected physical compute claim')
    require(digest((source/'source/background.c').read_bytes())==FIXED['background_after'],
            'compiled source must match original C42A preflight')
    require(digest((source/'tools/evolver_ndf15.c').read_bytes())==FIXED['ndf_after'],
            'compiled NDF15 source must match original C42A preflight')
    import classy
    mod=sys.modules.get(classy.Class.__module__) or importlib.import_module(classy.Class.__module__)
    binary=Path(mod.__file__).resolve(strict=True)
    require(any(str(binary).endswith(s) for s in importlib.machinery.EXTENSION_SUFFIXES),
            'classy.Class must originate from native compiled extension')
    require(source.resolve() in binary.parents,'imported classy extension outside pinned source')
    require(binary.stat().st_size>100000,'native shared library unexpectedly small')
    require(not j['native_solver_result_certified'],'build receipt cannot certify physics')
    j.update(state='PINNED_C42A_NATIVE_EXTENSION_COMPILED_AND_IMPORTED',
             native_build_certified=True,compiled_CLASS_binary_path=str(binary),
             compiled_CLASS_sha256=digest(binary.read_bytes()),
             compiled_CLASS_size=binary.stat().st_size,
             classy_class_module=classy.Class.__module__)
    save(audit_path,j)
    print('C42B NATIVE BUILD/IMPORT VERIFIED; CLASS.compute 0')
    return j

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--stage',choices=['prepare','verify-built'],required=True)
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a1=p.parse_args()
    if a1.stage=='prepare':stage(a1.source,a1.out)
    else:verify(a1.source,a1.out)

if __name__=='__main__':main()
