from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path

import yaml


def load(path):
    return yaml.safe_load(Path(path).read_text())


def prior_of(p):
    return deepcopy(p.get('prior')) if isinstance(p, dict) else None


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def audit_pair(original_path, c8_path, model):
    old = load(original_path)
    new = load(c8_path)

    # Scientific likelihood and theory target must be byte-for-structure equivalent.
    assert old['likelihood'] == new['likelihood'], f'{model}: likelihood changed'
    assert old['theory'] == new['theory'], f'{model}: theory changed'

    op = old['params']
    np_ = new['params']

    # H0 prior is replaced only by the exact periodic unit-interval coordinate.
    assert op['H0']['prior'] == {'min': 55.0, 'max': 82.0}
    assert np_['q_H']['prior'] == {'min': 0.0, 'max': 1.0}
    assert np_['q_H'].get('periodic') is True
    assert np_['q_H'].get('drop') is True
    assert 'prior' not in np_['H0']
    assert np_['H0'].get('min') == 55.0 and np_['H0'].get('max') == 82.0

    # Every other physical sampled prior is frozen exactly.
    old_sampled = {k: prior_of(v) for k, v in op.items() if prior_of(v) is not None and k != 'H0'}
    new_sampled = {k: prior_of(v) for k, v in np_.items() if prior_of(v) is not None and k != 'q_H'}
    assert old_sampled == new_sampled, (model, old_sampled, new_sampled)

    # All deterministic physical transformations other than H0 must remain exact.
    for k, v in op.items():
        if k == 'H0':
            continue
        if isinstance(v, dict) and ('value' in v or 'derived' in v):
            assert k in np_, f'{model}: missing deterministic parameter {k}'
            for field in ('value', 'derived'):
                if field in v:
                    assert np_[k].get(field) == v.get(field), f'{model}: {k}.{field} changed'

    # Production convergence gate is unchanged. Sampler transport/initialization may differ.
    for field, expected in [('Rminus1_stop', 0.01), ('Rminus1_cl_stop', 0.15), ('Rminus1_cl_level', 0.95)]:
        assert float(new['sampler']['mcmc'][field]) == expected
    assert new['sampler']['mcmc']['learn_proposal'] is True
    assert float(new['sampler']['mcmc']['proposal_scale']) == 2.4

    return {
        'model': model,
        'original': original_path,
        'c8': c8_path,
        'original_sha256': sha256(original_path),
        'c8_sha256': sha256(c8_path),
        'likelihood_unchanged': True,
        'theory_unchanged': True,
        'non_H0_physical_priors_unchanged': True,
        'H0_prior_replaced_by_exact_periodic_unit_coordinate': True,
        'production_Rminus1_gate': 0.01,
        'target_distribution_changed': False,
    }


def main():
    out = {
        'schema': 'rims-phaseii-o3-c8-target-audit-v1',
        'scalar': audit_pair('mcmc_o3/scalar_exp.yaml', 'mcmc_o3/scalar_exp_c8_transport.yaml', 'scalar'),
        'rims': audit_pair('mcmc_o3/rims_exp_shell.yaml', 'mcmc_o3/rims_exp_shell_c8_transport.yaml', 'rims'),
    }
    out['status'] = 'PASS'
    Path('mcmc_o3/C8_TARGET_AUDIT.json').write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
