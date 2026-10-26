from __future__ import annotations

import numpy as np

# Frozen c6 diagnostic predictor. This is a sampler transport map only.
OMEGA_MU = 0.08768051
OMEGA_SD = 0.02541329
ALPHA_MU = 0.04626285
ALPHA_SD = 0.02051664
SHELL_U_MU = -1.53784825
SHELL_U_SD = 0.48203115
HREF = 68.0
H0_MIN = 55.0
H0_MAX = 82.0
H0_WIDTH = H0_MAX - H0_MIN

# Features: [1, o, a, u, o^2, o*a]
H_COEFF = np.array([
    68.1447995,
    -0.678001096,
    0.273304965,
    -0.0397724341,
    -0.152357637,
    -0.00426803887,
], dtype=float)


def hhat(omega_scf, rims_alpha_u, rims_shell_u_i):
    o = (np.asarray(omega_scf) - OMEGA_MU) / OMEGA_SD
    a = (np.asarray(rims_alpha_u) - ALPHA_MU) / ALPHA_SD
    u = (np.asarray(rims_shell_u_i) - SHELL_U_MU) / SHELL_U_SD
    c = H_COEFF
    return c[0] + c[1]*o + c[2]*a + c[3]*u + c[4]*o*o + c[5]*o*a


def h0_from_q(q_h, omega_scf, rims_alpha_u, rims_shell_u_i):
    """Measure-preserving periodic shear from q_H in [0,1) to H0 in [55,82)."""
    shift = (hhat(omega_scf, rims_alpha_u, rims_shell_u_i) - HREF) / H0_WIDTH
    return H0_MIN + H0_WIDTH * np.mod(np.asarray(q_h) + shift, 1.0)


def q_from_h0(h0, omega_scf, rims_alpha_u, rims_shell_u_i):
    """Inverse periodic coordinate, modulo the unit interval."""
    shift = (hhat(omega_scf, rims_alpha_u, rims_shell_u_i) - HREF) / H0_WIDTH
    return np.mod((np.asarray(h0) - H0_MIN) / H0_WIDTH - shift, 1.0)
