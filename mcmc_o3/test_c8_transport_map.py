from __future__ import annotations

import numpy as np

from c8_transport_map import H0_MIN, H0_WIDTH, h0_from_q, q_from_h0


def circular_error(a, b):
    return np.abs(np.mod(a - b + 0.5, 1.0) - 0.5)


def main():
    rng = np.random.default_rng(20260907)
    n = 200_000
    q = rng.random(n)
    omega = rng.uniform(0.001, 0.18, n)
    alpha = rng.uniform(0.0001, 0.12, n)
    shell_u = rng.uniform(-2.44234703537, 1.09861228867, n)

    h0 = h0_from_q(q, omega, alpha, shell_u)
    q_back = q_from_h0(h0, omega, alpha, shell_u)
    inverse_max = float(np.max(circular_error(q_back, q)))
    assert inverse_max < 1e-12, inverse_max
    assert np.all(h0 >= H0_MIN)
    assert np.all(h0 < H0_MIN + H0_WIDTH)

    # Empirical push-forward test: uniform periodic q must remain uniform H0
    u = np.sort((h0 - H0_MIN) / H0_WIDTH)
    ecdf = np.arange(1, n + 1) / n
    ks_sup = float(np.max(np.abs(ecdf - u)))
    assert ks_sup < 0.01, ks_sup

    # Local Jacobian dH0/dq = H0_WIDTH away from the wrap point.
    eps = 1e-7
    q0 = np.array([0.20, 0.35, 0.65, 0.80])
    o0 = np.full_like(q0, 0.09)
    a0 = np.full_like(q0, 0.05)
    u0 = np.full_like(q0, -1.5)
    hp = h0_from_q(q0 + eps, o0, a0, u0)
    hm = h0_from_q(q0 - eps, o0, a0, u0)
    jac = (hp - hm) / (2 * eps)
    assert np.allclose(jac, H0_WIDTH, rtol=0, atol=1e-6), jac

    # Quadrature check of the evidence measure for a localized test likelihood.
    grid = (np.arange(200_000) + 0.5) / 200_000
    hg = h0_from_q(grid, 0.09, 0.05, -1.5)
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
