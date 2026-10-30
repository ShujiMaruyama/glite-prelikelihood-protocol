#!/usr/bin/env python3
"""RIMS C47: conditional local beta-kappa fingerprint, not an observation."""
from __future__ import annotations
import argparse,json,math
from pathlib import Path

def fingerprint(alpha:float,s:float)->dict:
    if not(math.isfinite(alpha) and alpha>0 and math.isfinite(s) and 0<s<1):
        raise ValueError('Positive finite alpha and 0<s<1 required')
    beta=alpha*(1-s)
    kappa=alpha**2*(1-s)*(1-3*s)
    delta=kappa-beta**2
    assert delta<0
    return dict(alpha=alpha,s=s,beta=beta,kappa=kappa,
                kappa_exponential=beta**2,curvature_difference=delta,
                curvature_difference_ratio_to_alpha_squared=delta/alpha**2,
                d_beta_d_phi=-2*alpha**2*s*(1-s),
                alpha_recovered=(3*beta**2-kappa)/(2*beta),
                curvature_maximum_negative_at_s=2/3,
                curvature_sign_zero_at_s=1/3,
                matched_exponential_discrimination_max_s=.5,
                delta_kappa_sech2=-.5*alpha**2/math.cosh(alpha*(math.log(s/(1-s))/(2*alpha)))**2,
                field_distance_negative_curvature_turnover=math.log(2)/(2*alpha),
                delta_kappa_full_width_half_max=2*math.acosh(math.sqrt(2))/alpha)

def uncertainty_budget(*,beta:float,kappa:float,sigma_beta:float,sigma_kappa:float,
                       corr:float=0.,require_resolved_beta:bool=True)->dict:
    a=(beta,kappa,sigma_beta,sigma_kappa,corr)
    if not all(map(math.isfinite,a)) or sigma_beta<=0 or sigma_kappa<=0 or not(-1<corr<1):
        raise ValueError('Finite, strictly positive uncertainties and nonsingular correlation required')
    if beta<=0:raise ValueError('Positive RIMS coupling required')
    if require_resolved_beta and beta/sigma_beta<=5:
        raise ValueError('beta must be resolved at >5 sigma for stable alpha inversion')
    covariance=corr*sigma_beta*sigma_kappa
    diff=kappa-beta**2
    variance_diff=sigma_kappa**2+4*beta**2*sigma_beta**2-4*beta*covariance
    if variance_diff<=0:raise ValueError('Singular discrimination variance')
    recovered=(3*beta**2-kappa)/(2*beta)
    grad_beta=1.5+kappa/(2*beta**2)
    grad_kappa=-1/(2*beta)
    variance_alpha=(grad_beta*sigma_beta)**2+(grad_kappa*sigma_kappa)**2+2*grad_beta*grad_kappa*covariance
    if variance_alpha<=0:raise ValueError('Singular inferred-alpha variance')
    return dict(schema='RIMS_C47_CONDITIONAL_RECONSTRUCTION_BUDGET_V1',
        delta_kappa=diff,delta_sigma=math.sqrt(variance_diff),
        local_delta_SNR=abs(diff)/math.sqrt(variance_diff),
        alpha_reconstructed=recovered,alpha_sigma_linearized=math.sqrt(variance_alpha),
        beta_SNR=beta/sigma_beta,
        requires_separately_identified_beta_kappa=True,
        covariance_used=[[sigma_beta**2,covariance],[covariance,sigma_kappa**2]],
        physical_forward_map_validated=False,real_survey_significance=False,
        observational_detection=False)

def example(alpha=.01,s=.65,relative_sigma_beta=.01,relative_sigma_kappa=.05,corr=0.):
    f=fingerprint(alpha,s)
    q=uncertainty_budget(beta=f['beta'],kappa=f['kappa'],
        sigma_beta=abs(f['beta'])*relative_sigma_beta,
        sigma_kappa=abs(f['kappa'])*relative_sigma_kappa,corr=corr)
    return dict(schema='RIMS_C47_USER_DEFINED_ERROR_TOY_V1',fingerprint=f,
                uncertainty=q,assumed_relative_sigma_beta=relative_sigma_beta,
                assumed_relative_sigma_kappa=relative_sigma_kappa,
                assumed_corr=corr,conditional_design_only=True)

def main():
    a=argparse.ArgumentParser()
    a.add_argument('--output',type=Path,required=True)
    a.add_argument('--alpha',type=float,default=.01)
    a.add_argument('--s',type=float,default=.65)
    a.add_argument('--relative-sigma-beta',type=float,default=.01)
    a.add_argument('--relative-sigma-kappa',type=float,default=.05)
    a.add_argument('--corr',type=float,default=0.)
    x=a.parse_args()
    if x.output.exists():raise FileExistsError('Refuse to overwrite output')
    result=example(x.alpha,x.s,x.relative_sigma_beta,x.relative_sigma_kappa,x.corr)
    x.output.parent.mkdir(parents=True,exist_ok=True)
    x.output.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n')
    print('Conditional ONLY; beta-kappa local SNR =',result['uncertainty']['local_delta_SNR'])
if __name__=='__main__':main()
