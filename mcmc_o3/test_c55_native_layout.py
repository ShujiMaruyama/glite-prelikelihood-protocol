"""Frozen CLASS C55 native layout tests. Synthetic fixtures are NOT native results."""
import math,sys,pytest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import c55_accepted_g_reconstruct as c

def fixture(phi=4.44, phi_c=4.4402,phi_prime=0.01,pp_c=0.011,wrong_index=False):
    a=1e-8;log_a=math.log(a);lam=math.sqrt(3000.);rho=1e16;H=1.4e13
    ys=[0.03,phi,phi_prime,3.,4.,5.,6.]
    yc=[0.03,phi_c,pp_c,3.,4.,5.,6.]
    V=math.exp(-lam*phi);s=c.sig(phi);k=c.ALPHA**2*(1-s)*(1-3*s)
    hx=float.hex
    deriv=dict(kind='DERIV',x=hx(log_a),n='7',yhex=','.join(map(hx,ys)),
        H=hx(H),Vpp=hx(lam*lam*V),rho_idm=hx(rho),phi=hx(phi),
        ratio=hx((lam*lam*V+3*rho*k)/(H*H)))
    aux=dict(kind='DERIV_AUX',x=hx(log_a),V=hx(V),phi_prime=hx(phi_prime),
        rho_scf=hx((phi_prime**2/(2*a*a)+V)/3),
        iphi=('0' if wrong_index else '1'),iphip=('1' if wrong_index else '2'),
        lam=hx(lam),palpha=hx(0.),pA=hx(0.),pB=hx(0.),
        alpha_U=hx(c.ALPHA),phi_t=hx(c.PHI_T),has_dcdm='0',has_dr='0',has_fld='0')
    commit=dict(kind='COMMIT_STATE',x=hx(log_a),seq='1',n='7',yhex=','.join(map(hx,yc)))
    return '\n'.join(f'{marker} '+' '.join(k+'='+v for k,v in row.items())
         for marker,row in ((c.D,deriv),(c.A,aux),(c.C,commit)))
def test_source_layout_and_algebra():
    z=c.audit(fixture());assert z['accepted_algebraic_reconstructions']==1
    a=z['records'][0]
    assert a['native_index_tau']==0 and a['native_scalar_phi_index']==1 and a['native_scalar_phi_prime_index']==2
    assert a['state_difference_components']==2
    assert not a['direct_native_accepted_g_measured']
def test_wrong_old_c54_indices_rejected():
    with pytest.raises(ValueError,match='indices'):c.audit(fixture(wrong_index=True))
def test_old_scalar_index_zero_is_not_phi():
    z=c.audit(fixture())
    assert z['records'][0]['phi_accepted']==4.4402
def test_no_native_state_not_promoted():
    z=c.audit('RIMS_C43_NDF_TRACE_V1 kind=COMMIT x=0.1 accepted=1 failed=0 order=1')
    assert z['total_commits']==0 and not z['native_accepted_g_directly_measured']
def test_incomplete_aux_cannot_create_accepted_g():
    parts=fixture().splitlines()
    z=c.audit('\n'.join((parts[0],parts[2])))
    assert z['accepted_algebraic_reconstructions']==0
    assert z['missing_unmatched']==[1]
def test_conformal_time_does_not_define_phi():
    z=c.audit(fixture())
    assert z['records'][0]['phi_accepted']!=0.03
def test_unverified_negative_source_ratio_rejected():
    parts=fixture().splitlines()
    parts[0]=parts[0].replace(' Vpp=', ' Vpp=-0x1p+1 other=')
    with pytest.raises(ValueError):c.audit('\n'.join(parts))
@pytest.mark.parametrize('bad',['nan','1.0','0x1p+1024'])
def test_refuse_nonbinary_stale_float(bad):
    with pytest.raises(ValueError):c.fp(bad)
