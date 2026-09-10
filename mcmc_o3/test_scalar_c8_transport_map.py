from __future__ import annotations

import numpy as np

from scalar_c8_transport_map import H0_MIN, H0_WIDTH, h0_from_q, q_from_h0


def circular_error(a, b):
    return np.abs(np.mod(a - b + 0.5, 1.0) - 0.5)


def main():
    rng = np.random.default_rng(20260907)
    n = 200_000
    q = rng.random(n)
    omega = rng.uniform(0.001, 0.180, n)

    h0 = h0_from_q(q, omega)
    q_back = q_from_h0(h0, omega)
    inverse_max = float(np.max(circular_error(q_back, q)))
    assert inverse_max < 1e-12, inverse_max
    assert np.all(h0 >= H0_MIN)
    assert np.all(h0 < H0_MIN + H0_WIDTH)

    u = np.sort((h0 - H0_MIN) / H0_WIDTH)
    ecdf = np.arange(1, n + 1) / n
    ks_sup = float(np.max(np.abs(ecdf - u)))
    assert ks_sup < 0.01, ks_sup

    eps = 1e-7
    q0 = np.array([0.20, 0.35, 0.65, 0.80])
    o0 = np.full_like(q0, 0.07)
    hp = h0_from_q(q0 + eps, o0)
    hm = h0_from_q(q0 - eps, o0)
    jac = (hp - hm) / (2 * eps)
    assert np.allclose(jac, H0_WIDTH, rtol=0, atol=1e-6), jac

    grid = (np.arange(200_000) + 0.5) / 200_000
    hg = h0_from_q(grid, 0.07)
    direct_h = H0_MIN + H0_WIDTH * grid
    f_q = np.exp(-0.5 * ((hg - 68.0) / 0.7) ** 2)
    f_h = np.exp(-0.5 * ((direct_h - 68.0) / 0.7) ** 2)
    evidence_diff = float(abs(np.mean(f_q) - np.mean(f_h)))
    assert evidence_diff < 1e-10, evidence_diff

    print({
        'inverse_max_circular_error': inverse_max,
        'empirical_uniform_ks_sup': ks_sup,
        'jacobian': jac.tolist(),
        'localized_evidence_integral_abs_diff': evidence_diff,
        'status': 'PASS',
    })


if __name__ == '__main__':
    main()
