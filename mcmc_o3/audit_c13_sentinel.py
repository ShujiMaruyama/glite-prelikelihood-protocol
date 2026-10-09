#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, math, re
from pathlib import Path
import numpy as np

SCALES=[5.7,7.0,8.2]
SAMPLED=["q_H","omega_b","omega_dm","logA","n_s","tau_reio","Omega_scf","rims_alpha_U","rims_shell_u_i","A_planck"]
BURN=0.30
TARGET=0.30

def read_chain(p:Path):
    first=p.read_text().splitlines()[0]
    if not first.startswith("#"): raise RuntimeError(f"missing header {p}")
    names=first[1:].split()
    a=np.loadtxt(p); a=a[None,:] if a.ndim==1 else a
    return names,a

def reconstruct(a,names):
    wi=names.index("weight")
    w=np.rint(a[:,wi]).astype(int)
    if np.any(w<1) or np.max(np.abs(a[:,wi]-w))>=1e-8: raise RuntimeError("bad weights")
    full=np.repeat(a,w,axis=0)
    cut=int(math.floor(BURN*len(full)))
    return full[cut:],len(a),int(w.sum())

def log_audit(p:Path):
    s=p.read_text(errors="replace")
    fat=[]
    pat=re.compile(r"(Traceback|Segmentation fault|MPI_ABORT|Error in function|Likelihood.*error|CLASS.*error|exception occurred)",re.I)
    for line in s.splitlines():
        if pat.search(line): fat.append(line[-500:])
    return {
      "full_drag_marker_present":"* 27 : (['A_planck'],)" in s,
      "dragging_present":"Dragging with number of interpolating steps:" in s,
      "fatal_markers":fat[:100]
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--work-dir",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    root=Path(a.work_dir)
    records=[]
    import arviz as az
    for scale in SCALES:
        tag=str(scale).replace(".","p")
        chains=[]; rows_total=0; weights_total=0; stats={}; names0=None
        for i in range(1,5):
            p=root/"chains_c13"/f"rims_c13_full_drag_{tag}.{i}.txt"
            if not p.exists() or p.stat().st_size==0: raise FileNotFoundError(p)
            names,x=read_chain(p)
            if names0 is None: names0=names
            if names!=names0: raise RuntimeError("header mismatch")
            full,rows,wsum=reconstruct(x,names)
            chains.append(full); rows_total+=rows; weights_total+=wsum
            stats[str(i)]={"distinct_rows":rows,"weight_sum":wsum,"acceptance":rows/wsum,
                           "postburn_reconstructed_steps":len(full)}
        agg=rows_total/weights_total
        min_draws=min(len(c) for c in chains)
        diag={}
        for p in SAMPLED:
            arr=np.stack([c[-min_draws:,names0.index(p)] for c in chains],axis=0)
            diag[p]={
              "rank_Rhat":float(np.asarray(az.rhat(arr,method="rank"))),
              "bulk_ESS":float(np.asarray(az.ess(arr,method="bulk"))),
              "tail_ESS":float(np.asarray(az.ess(arr,method="tail",prob=(0.05,0.95))))
            }
        la=log_audit(root/f"c13_{tag}.log")
        passed=(0.20<=agg<=0.50 and
                all(0.10<=v["acceptance"]<=0.65 for v in stats.values()) and
                all(v["distinct_rows"]>=10 for v in stats.values()) and
                la["full_drag_marker_present"] and la["dragging_present"] and not la["fatal_markers"])
        records.append({
          "proposal_scale":scale,"aggregate_acceptance":agg,"chains":stats,
          "diagnostic_target_passed":passed,"log_audit":la,
          "worst_rank_Rhat":max(({"parameter":p,**v} for p,v in diag.items()),key=lambda d:d["rank_Rhat"]),
          "minimum_bulk_ESS":min(({"parameter":p,**v} for p,v in diag.items()),key=lambda d:d["bulk_ESS"]),
          "minimum_tail_ESS":min(({"parameter":p,**v} for p,v in diag.items()),key=lambda d:d["tail_ESS"]),
          "eligible_for_inference":False
        })
    passing=[r for r in records if r["diagnostic_target_passed"]]
    selected=None
    if passing:
        selected=min(passing,key=lambda r:(abs(r["aggregate_acceptance"]-TARGET),r["proposal_scale"]))["proposal_scale"]
    out={
      "schema":"rims-phaseii-o3-c13-full-drag-selection-v1",
      "role":"bounded_nonproduction_full_drag_scale_sentinel",
      "records":records,
      "selected_proposal_scale":selected,
      "selection_rule":"among passing scales, minimize |aggregate_acceptance-0.30|; tie -> lower scale; if none pass -> stop",
      "sentinel_samples_eligible_for_inference":False,
      "automatic_follow_on":False,
      "automatic_long_run":False,
      "production_gate":{"GetDist_Rminus1_lt":0.01,"minimum_headline_ESS_ge":1000.0},
      "claim_boundary":{"production_posterior":False,"Bayes_factor":False,"model_preference":False,"LambdaCDM_competitiveness_verified":False}
    }
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True))
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__": main()
