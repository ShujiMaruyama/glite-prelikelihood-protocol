from __future__ import annotations

import numpy as np

# Frozen c6 scalar diagnostic predictor. Sampler transport only.
OMEGA_MU = 0.06988961182249204
OMEGA_SD = 0.030640502057554492
HREF = 68.0
H0_MIN = 55.0
H0_MAX = 82.0
H0_WIDTH = H0_MAX - H0_MIN

# Features: [1, o, o^2], fitted only on post-burn c6 scalar diagnostic chains.
H_COEFF = np.array([
    68.00781035064747,
    -0.48114439376854024,
    -0.11363064315320584,
], dtype=float)


def hhat(omega_scf):
    o = (np.asarray(omega_scf) - OMEGA_MU) / OMEGA_SD
    c = H_COEFF
    return c[0] + c[1]*o + c[2]*o*o


def h0_from_q(q_h, omega_scf):
    shift = (hhat(omega_scf) - HREF) / H0_WIDTH
    return H0_MIN + H0_WIDTH * np.mod(np.asarray(q_h) + shift, 1.0)


def q_from_h0(h0, omega_scf):
    shift = (hhat(omega_scf) - HREF) / H0_WIDTH
    return np.mod((np.asarray(h0) - H0_MIN) / H0_WIDTH - shift, 1.0)
