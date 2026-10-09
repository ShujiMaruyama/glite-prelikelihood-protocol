#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, math, re
from pathlib import Path
import numpy as np

SCALES=[4.0,4.8,5.7]
SAMPLED=["q_H","omega_b","omega_dm","logA","n_s","tau_reio","Omega_scf","rims_alpha_U","rims_shell_u_i","A_planck"]
BURN=0.30
TARGET=0.30

def read_chain(p):
    first=p.read_text().splitlines()[0]
    names=first[1:].split()
    a=np.loadtxt(p); a=a[None,:] if a.ndim==1 else a
    return names,a

def reconstruct(a,names):
    wi=names.index("weight")
    w=np.rint(a[:,wi]).astype(int)
    assert np.all(w>=1) and np.max(np.abs(a[:,wi]-w))<1e-8
    full=np.repeat(a,w,axis=0)
    cut=int(math.floor(BURN*len(full)))
    return full[cut:],len(a),int(w.sum())

def log_audit(p):
    s=p.read_text(errors="replace")
    fatal=[]
    pat=re.compile(r"(Traceback|Segmentation fault|MPI_ABORT|Error in function|Likelihood.*error|CLASS.*error|exception occurred)",re.I)
    for line in s.splitlines():
        if pat.search(line): fatal.append(line[-500:])
    return {
      "dragging_present":"Dragging with number of interpolating steps:" in s,
      "step27_marker_present":"* 27 : (['A_planck'],)" in s,
      "fatal_markers":fatal[:100]
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--work-dir",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    root=Path(a.work_dir)
    import arviz as az
    records=[]
    for scale in SCALES:
        tag=str(scale).replace(".","p")
        chains=[]; names0=None; rows=0; weights=0; cs={}
        for i in range(1,5):
            p=root/"chains_c13b"/f"rims_c13b_27step_{tag}.{i}.txt"
            if not p.exists() or p.stat().st_size==0: raise FileNotFoundError(p)
            names,x=read_chain(p)
            if names0 is None: names0=names
            assert names==names0
            full,r,w=reconstruct(x,names)
            chains.append(full); rows+=r; weights+=w
            cs[str(i)]={"distinct_rows":r,"weight_sum":w,"acceptance":r/w,
                        "postburn_reconstructed_steps":len(full)}
        min_draws=min(len(c) for c in chains)
        diag={}
        for p in SAMPLED:
            arr=np.stack([c[-min_draws:,names0.index(p)] for c in chains],axis=0)
            diag[p]={
              "rank_Rhat":float(np.asarray(az.rhat(arr,method="rank"))),
              "bulk_ESS":float(np.asarray(az.ess(arr,method="bulk"))),
              "tail_ESS":float(np.asarray(az.ess(arr,method="tail",prob=(0.05,0.95))))
            }
        la=log_audit(root/f"c13b_{tag}.log")
        agg=rows/weights
        passed=(0.20<=agg<=0.50 and all(0.10<=v["acceptance"]<=0.65 for v in cs.values())
                and all(v["distinct_rows"]>=10 for v in cs.values())
                and la["dragging_present"] and la["step27_marker_present"] and not la["fatal_markers"])
        records.append({
          "proposal_scale":scale,"aggregate_acceptance":agg,"chains":cs,
          "diagnostic_target_passed":passed,"log_audit":la,
          "worst_rank_Rhat":max(({"parameter":p,**v} for p,v in diag.items()),key=lambda d:d["rank_Rhat"]),
          "minimum_bulk_ESS":min(({"parameter":p,**v} for p,v in diag.items()),key=lambda d:d["bulk_ESS"]),
          "minimum_tail_ESS":min(({"parameter":p,**v} for p,v in diag.items()),key=lambda d:d["tail_ESS"]),
          "eligible_for_inference":False
        })
    passing=[r for r in records if r["diagnostic_target_passed"]]
    selected=min(passing,key=lambda r:(abs(r["aggregate_acceptance"]-TARGET),r["proposal_scale"]))["proposal_scale"] if passing else None
    out={
      "schema":"rims-phaseii-o3-c13b-27step-selection-v1",
      "role":"bounded_nonproduction_27step_drag_scale_sentinel",
      "records":records,
      "selected_proposal_scale":selected,
      "sentinel_samples_eligible_for_inference":False,
      "automatic_follow_on":False,
      "automatic_long_run":False,
      "production_gate":{"GetDist_Rminus1_lt":0.01,"minimum_headline_ESS_ge":1000.0},
      "claim_boundary":{"production_posterior":False,"Bayes_factor":False,"model_preference":False,"LambdaCDM_competitiveness_verified":False}
    }
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True))
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__": main()
