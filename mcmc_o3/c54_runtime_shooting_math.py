#!/usr/bin/env python3
"""C54 runnable source-specific numerical check, not a new native CLASS execution.

Frozen C44 trial: CLASS scf shooting changes runtime lambda. The accepted-state
reconstruction is conditional on source-attested C46/C54/C45 same-step records.
"""
import argparse,json,math

PHI_T=-26.51196042031118
ALPHA=0.01
VETO=-1.0049389722010728e-10
def sigmoid(phi):
    z=2*ALPHA*(phi-PHI_T)
    if z>=0:return 1/(1+math.exp(-z))
    w=math.exp(z);return w/(1+w)
def potential(phi,lam):
    if not(math.isfinite(lam) and 0<lam<1000):raise ValueError('runtime lambda required')
    return math.exp(-lam*phi)
def accepted_reconstruction(*,a,phi_eval,phip_eval,phi_commit,phip_commit,
                            H_eval,rho_idm_eval,runtime_lambda,source_attested=False,
                            same_accepted_step=False):
    """Pure algebraic reconstruction; output is NOT a direct native measurement."""
    if not(source_attested is True and same_accepted_step is True):
        raise ValueError('Source and accepted-step provenance are mandatory')
    vals=(a,phi_eval,phip_eval,phi_commit,phip_commit,H_eval,rho_idm_eval,runtime_lambda)
    if not all(map(math.isfinite,vals)) or a<=0 or H_eval<=0 or rho_idm_eval<0:
        raise ValueError('nonfinite/nonpositive original source data')
    se,sc=sigmoid(phi_eval),sigmoid(phi_commit)
    if not (0<se<=1 and 0<sc<=1):raise ValueError('invalid RIMS logistic state')
    Ve,Vc=potential(phi_eval,runtime_lambda),potential(phi_commit,runtime_lambda)
    rho_c=rho_idm_eval*math.sqrt(sc/se)
    h2=H_eval**2+(rho_c-rho_idm_eval)+(
        ((phip_commit**2-phip_eval**2)/(2*a*a))+Vc-Ve)/3
    if not(math.isfinite(h2) and h2>0):raise ValueError('nonpositive reconstructed H^2')
    k=ALPHA**2*(1-sc)*(1-3*sc)
    ratio=(runtime_lambda**2*Vc+3*rho_c*k)/h2
    return {'schema':'RIMS_C54_ALGEBRAIC_ACCEPTED_G_V1',
        'source_attested':True,'same_accepted_step':True,
        'runtime_lambda':runtime_lambda,'H2_reconstructed':h2,
        'rho_idm_reconstructed':rho_c,
        'm_eff2_over_H2_reconstructed':ratio,'g_reconstructed':ratio+1e-10,
        'native_class_compute_performed':False,
        'direct_native_accepted_g_measured':False,
        'roundoff_enclosure_certified':False,
        'physical_stability_proven':False}
def c44_trial_source_check():
    """Read-only check of original C39 rejected Newton trial; no accepted g."""
    phi=4.4399999947111519
    Vpp=7.2704406617212974e-103
    lam=math.sqrt(3/.001)
    theory=lam**2*potential(phi,lam)
    if not math.isclose(theory,Vpp,rel_tol=1e-12):
        raise ValueError('original shooting lambda audit failed')
    return {'schema':'RIMS_C54_C44_REJECTED_TRIAL_SHOOTING_CHECK',
            'runtime_lambda_inferred_from_original_source':lam,
            'lambda_directly_measured_by_C54':False,
            'source_Vpp_predicted':theory,'original_vpp':Vpp,
            'input_lambda':5.,'original_failed_newton_trial_not_committed':True,
            'accepted_g_measured':False}
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--accepted-json',help='Optional same-step source-attested derivative/commit values')
    a=ap.parse_args()
    if a.accepted_json:
        with open(a.accepted_json) as f:j=json.load(f)
        out=accepted_reconstruction(**j)
    else:out=c44_trial_source_check()
    print(json.dumps(out,sort_keys=True,indent=2,allow_nan=False))
if __name__=='__main__':main()
