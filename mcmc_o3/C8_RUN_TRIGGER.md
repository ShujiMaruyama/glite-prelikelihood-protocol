# RIMS Phase II O3 c8p1 execution trigger

This commit launches the predeclared fresh four-chain c8 production candidate for Scalar and RIMS.

Execution contract:
- no c6/c7 samples are resumed or pooled;
- the Planck 2018 + DESI DR2 + Pantheon+ likelihood target is unchanged;
- the physical priors are unchanged;
- only the sampler coordinate H0 -> periodic q_H is changed via the frozen measure-preserving c6-derived shear;
- proposal_scale is reset to 2.4 with learn_proposal enabled;
- the first bounded segment is 90 minutes per model with four MPI chains;
- headline promotion remains forbidden unless GetDist R-1 < 0.01 and minimum headline ESS >= 1000.
