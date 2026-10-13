from __future__ import annotations

import argparse, json, math
from pathlib import Path
import numpy as np

DEFAULT_PARAMS = [
    'H0','omega_b','omega_dm','logA','n_s','tau_reio','Omega_scf',
    'rims_alpha_U','rims_shell_u_i','A_planck'
]


def read_chain(path: Path):
    first = path.open(encoding='utf-8').readline().strip()
    if not first.startswith('#'):
        raise ValueError(f'No Cobaya header in {path}')
    names = first[1:].split()
    a = np.loadtxt(path)
    if a.ndim == 1:
        a = a[None, :]
    if a.shape[1] != len(names):
        raise ValueError(f'Column mismatch {path}: {a.shape[1]} != {len(names)}')
    return names, a


def expand_weighted(a: np.ndarray):
    w = np.rint(a[:,0]).astype(int)
    if np.any(w < 1) or not np.allclose(w, a[:,0], rtol=0, atol=1e-8):
        raise ValueError('Expected positive integer MCMC multiplicity weights')
    return np.repeat(a[:,2:], w, axis=0), int(w.sum())


def autocorr_fft(x):
    x = np.asarray(x, float)
    n = len(x)
    if n < 4:
        return np.ones(n)
    y = x - x.mean()
    var = np.dot(y,y)/n
    if not np.isfinite(var) or var <= 0:
        return np.ones(n)
    size = 1 << (2*n - 1).bit_length()
    f = np.fft.rfft(y, n=size)
    acov = np.fft.irfft(f*np.conjugate(f), n=size)[:n]
    acov = acov / np.arange(n,0,-1)
    return acov / acov[0]


def tau_geyer(x):
    rho = autocorr_fft(x)
    n = len(rho)
    if n < 3:
        return 1.0
    pairs=[]
    k=1
    while k+1 < n:
        g = rho[k] + rho[k+1]
        if not np.isfinite(g) or g <= 0:
            break
        pairs.append(float(g))
        k += 2
    if pairs:
        for i in range(1,len(pairs)):
            if pairs[i] > pairs[i-1]:
                pairs[i] = pairs[i-1]
    tau = 1.0 + 2.0*sum(pairs)
    return float(max(1.0, min(tau, len(x))))


def split_drift(x):
    n=len(x)
    if n < 4:
        return None
    h=n//2
    a=x[:h]; b=x[-h:]
    sd=np.std(x, ddof=1)
    return {
        'first_half_mean': float(np.mean(a)),
        'second_half_mean': float(np.mean(b)),
        'half_drift_sigma': float((np.mean(b)-np.mean(a))/sd) if sd>0 else 0.0,
    }


def summarize_series(x):
    x=np.asarray(x,float)
    tau=tau_geyer(x)
    d={
        'n_steps': int(len(x)),
        'mean': float(np.mean(x)),
        'std': float(np.std(x,ddof=1)) if len(x)>1 else 0.0,
        'tau_int': tau,
        'ess_acf': float(len(x)/tau),
    }
    d.update(split_drift(x) or {})
    return d


def chain_files(root: Path):
    fs=[]
    for i in range(1,5):
        p=Path(f'{root}.{i}.txt')
        if p.exists(): fs.append((i,p))
    if len(fs)<2:
        raise FileNotFoundError(f'Need >=2 chains for {root}')
    return fs


def load_expanded(root: Path, burn=0.30):
    out={}
    columns=None
    for i,p in chain_files(root):
        names,a=read_chain(p)
        cur=names[2:]
        if columns is None: columns=cur
        elif columns != cur: raise ValueError('Inconsistent chain headers')
        x,total=expand_weighted(a)
        cut=int(math.floor(burn*len(x)))
        out[i]={'x':x[cut:], 'full':x, 'total_weight':total, 'distinct_rows':int(a.shape[0]), 'a':a, 'names':names}
    return columns,out


def parent_added(current, parent):
    audit={}
    for i in current:
        if i not in parent: continue
        ca=current[i]['a']; pa=parent[i]['a']
        exact = ca.shape[0]>=pa.shape[0] and np.array_equal(ca[:pa.shape[0]],pa)
        add=ca[pa.shape[0]:] if exact else np.empty((0,ca.shape[1]))
        ws=float(add[:,0].sum()) if len(add) else 0.0
        audit[str(i)]={
            'prefix_exact': bool(exact),
            'parent_distinct_rows': int(pa.shape[0]),
            'current_distinct_rows': int(ca.shape[0]),
            'added_distinct_rows': int(len(add)),
            'added_weight_sum': ws,
            'added_acceptance_estimate': float(len(add)/ws) if ws>0 else None,
        }
    vals=[v['added_acceptance_estimate'] for v in audit.values() if v['added_acceptance_estimate'] is not None]
    return {'chains':audit,'prefix_exact_all':all(v['prefix_exact'] for v in audit.values()),
            'mean_chain_acceptance_estimate': float(np.mean(vals)) if vals else None,
            'total_added_rows':sum(v['added_distinct_rows'] for v in audit.values()),
            'total_added_weight':sum(v['added_weight_sum'] for v in audit.values())}


def pooled_pca(columns, chains, params):
    idx=[columns.index(p) for p in params if p in columns]
    pnames=[columns[j] for j in idx]
    mats=[d['x'][:,idx] for d in chains.values()]
    z=np.vstack(mats)
    mu=np.mean(z,axis=0); sd=np.std(z,axis=0,ddof=1); sd[sd==0]=1
    z=(z-mu)/sd
    corr=np.corrcoef(z,rowvar=False)
    eigval,eigvec=np.linalg.eigh(corr)
    order=np.argsort(eigval)[::-1]; eigval=eigval[order]; eigvec=eigvec[:,order]
    pcs=[]
    for k in range(min(len(pnames),5)):
        v=eigvec[:,k]
        m=int(np.argmax(np.abs(v)))
        if v[m]<0: v=-v
        pcs.append({'pc':k+1,'eigenvalue':float(eigval[k]),
                    'loadings':{p:float(q) for p,q in zip(pnames,v)}})
    return {'parameters':pnames,'correlation_matrix':corr.tolist(),'pcs':pcs}


def main():
    ap=argparse.ArgumentParser(description='RIMS/Scalar chain-level transport audit')
    ap.add_argument('--root',required=True)
    ap.add_argument('--model',required=True)
    ap.add_argument('--out',required=True)
    ap.add_argument('--parent-root')
    ap.add_argument('--burnin',type=float,default=0.30)
    args=ap.parse_args()
    root=Path(args.root)
    columns,chains=load_expanded(root,args.burnin)
    params=[p for p in DEFAULT_PARAMS if p in columns]
    result={'schema':'rims-transport-audit-v1','model':args.model,'root':str(root),
            'burnin_fraction':args.burnin,'parameters':params,'chains':{}}
    for i,d in chains.items():
        result['chains'][str(i)]={'postburn_weighted_steps':int(len(d['x'])),'parameters':{}}
        for p in params:
            result['chains'][str(i)]['parameters'][p]=summarize_series(d['x'][:,columns.index(p)])
    result['pooled_pca']=pooled_pca(columns,chains,params)
    def pooled_corr(a,b):
        xx=np.concatenate([d['x'][:,columns.index(a)] for d in chains.values()])
        yy=np.concatenate([d['x'][:,columns.index(b)] for d in chains.values()])
        return float(np.corrcoef(xx,yy)[0,1])
    result['ridge_correlations']={}
    for a,b in [('H0','Omega_scf'),('logA','tau_reio'),('Omega_scf','rims_alpha_U'),('Omega_scf','rims_shell_u_i')]:
        if a in columns and b in columns:
            result['ridge_correlations'][f'{a}__{b}']=pooled_corr(a,b)
    if args.parent_root:
        _,par=load_expanded(Path(args.parent_root),args.burnin)
        result['continuation_transport']=parent_added(chains,par)
        result['acf_improvement_vs_parent']={}
        for i in chains:
            if i not in par: continue
            result['acf_improvement_vs_parent'][str(i)]={}
            for p in params:
                j=columns.index(p)
                tc=tau_geyer(chains[i]['x'][:,j]); tp=tau_geyer(par[i]['x'][:,j])
                result['acf_improvement_vs_parent'][str(i)][p]={
                    'parent_tau_int':tp,'current_tau_int':tc,
                    'tau_ratio_current_over_parent':float(tc/tp) if tp>0 else None,
                }
    bottleneck=[]
    for i,c in result['chains'].items():
        for p,d in c['parameters'].items():
            if d['ess_acf'] < 50 or abs(d.get('half_drift_sigma',0)) > 0.5:
                bottleneck.append({'chain':int(i),'parameter':p,'ess_acf':d['ess_acf'],
                                   'tau_int':d['tau_int'],'half_drift_sigma':d.get('half_drift_sigma')})
    result['diagnostic_bottlenecks']=sorted(bottleneck,key=lambda q:q['ess_acf'])
    Path(args.out).write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({'model':args.model,'output':args.out,'ridge_correlations':result['ridge_correlations'],
                      'top_bottlenecks':result['diagnostic_bottlenecks'][:10],
                      'continuation_transport':result.get('continuation_transport')},indent=2))

if __name__=='__main__': main()
