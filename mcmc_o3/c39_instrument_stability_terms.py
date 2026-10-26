#!/usr/bin/env python3
"""C39 diagnostic-only source overlay: print the two physical m_eff^2 terms
AT the unmodified native CLASS RIMS stability rejection.

No parameter, tolerance, algebra, guard, or control flow is altered. This
script refuses ambiguous/unexpected source and preserves before/after hashes.
Run on already pinned-and-patched original CLASS, BEFORE native compilation.
"""
import argparse, hashlib, json
from pathlib import Path

ANCHOR = """    class_test((pba->rims_enforce_stability == _TRUE_) &&
               (pvecback[pba->index_bg_rims_stability_margin] < -pba->rims_stability_tolerance),
               pba->error_message,
               "RIMS stability gate failed at a=%e: m_eff^2/H^2=%e < -%e","""

OVERLAY = r'''    /* C39 DIAGNOSTIC ONLY: no changed physics/threshold/stability veto.
       Always print ORIGINAL physical source values before the existing test. */
    if ((pba->rims_enforce_stability == _TRUE_) &&
        (pvecback[pba->index_bg_rims_stability_margin] < -pba->rims_stability_tolerance)) {
      double c39_h = pvecback[pba->index_bg_H];
      double c39_vpp = pvecback[pba->index_bg_ddV_scf];
      double c39_rho = pvecback[pba->index_bg_rho_idm];
      double c39_masscurv = rims_mass_curvature_value;
      double c39_matter_term = 3.*c39_rho*c39_masscurv;
      double c39_sum = pvecback[pba->index_bg_rims_meff2];
      double c39_h2 = c39_h*c39_h;
      fprintf(stderr,
        "RIMS_C39_TERMS_V1 a=%.17g phi=%.17g s=%.17g H=%.17g "
        "Vpp=%.17g rho_idm=%.17g mass_curvature=%.17g matter_term=%.17g "
        "raw_meff2=%.17g h2=%.17g ratio=%.17g tolerance=%.17g\n",
        a,phi,rims_s_value,c39_h,c39_vpp,c39_rho,c39_masscurv,
        c39_matter_term,c39_sum,c39_h2,
        pvecback[pba->index_bg_rims_stability_margin],
        pba->rims_stability_tolerance);
      fflush(stderr);
    }
'''

def sha(data):
    return hashlib.sha256(data).hexdigest()

def overlay(original):
    if original.count(ANCHOR) != 1:
        raise ValueError("Original native stability gate is absent/ambiguous; refusing modification")
    if "RIMS_C39_TERMS_V1" in original:
        raise ValueError("Cannot instrument the same CLASS source twice")
    modified = original.replace(ANCHOR, OVERLAY + ANCHOR)
    assert modified.count(ANCHOR) == 1
    # Critical firewall: stripping exactly the added overlay restores every
    # byte of original source, including the original sign and tolerance.
    if modified.replace(OVERLAY, "", 1) != original:
        raise ValueError("Non-diagnostic source change detected")
    return modified

def install(path,report):
    src=Path(path)
    if not src.is_file():raise FileNotFoundError(src)
    if Path(report).exists():raise FileExistsError("Refuse to overwrite source-change audit")
    raw=src.read_bytes()
    before=raw.decode("utf-8")
    after=overlay(before).encode("utf-8")
    if sha(raw)==sha(after):raise RuntimeError("Instrumentation unexpectedly identical")
    src.write_bytes(after)
    result={"schema":"rims-c39-source-overlay-v1",
        "source_file":str(src),
        "source_sha256_before_overlay":sha(raw),
        "source_sha256_after_overlay":sha(after),
        "reconstruction_original_sha256":sha(after.replace(OVERLAY.encode("utf-8"),b"",1)),
        "veto_gate_preserved":True,"changed_scientific_parameters":False,
        "changed_tolerance":False,"retuned_shooting":False,
        "only_addition":"stderr diagnostic on original native veto branch",
        "new_CLASS_computes":0}
    Path(report).parent.mkdir(parents=True,exist_ok=True)
    Path(report).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--audit-out",type=Path,required=True)
    a=p.parse_args()
    result=install(a.source,a.audit_out)
    print("C39_SOURCE_OVERLAY_SHA256",result["source_sha256_before_overlay"],
          result["source_sha256_after_overlay"])
if __name__=="__main__":main()
