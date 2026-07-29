from __future__ import annotations

from typing import Any

import numpy as np
from cobaya.theories.classy.classy import classy as CobayaClassy


class RIMSClassy(CobayaClassy):
    """Cobaya CLASS wrapper with deterministic RIMS mass normalization.

    The physical RIMS parameter space does not treat ``rims_phi_ref`` as a
    free cosmological coordinate.  It is the reference field value that
    enforces m_d(a=1)=m_U.  For every sampled cosmology this wrapper solves
    the fixed point phi_ref = phi(a=1) with a cheap background-only CLASS
    calculation, then performs the requested full CLASS calculation with the
    native V7 normalization gate enabled.
    """

    rims_norm_tolerance: float = 2.0e-9
    rims_norm_maxiter: int = 12
    rims_norm_default_ref: float = 4.343497008603

    def initialize(self):
        super().initialize()
        self._rims_last_phi_ref = self.rims_norm_default_ref
        self._rims_last_signature = None

    def get_can_support_params(self):
        names = list(super().get_can_support_params())
        for name in [
            "Omega_scf",
            "omega_idm",
            "omega_cdm",
            "rims_alpha_U",
            "rims_phi_transition",
        ]:
            if name not in names:
                names.append(name)
        return names

    @staticmethod
    def _is_rims_enabled(args: dict[str, Any]) -> bool:
        value = args.get("rims_enabled", "no")
        if isinstance(value, str):
            return value.strip().lower() in {"yes", "y", "true", "1"}
        return bool(value)

    @staticmethod
    def _pick_phi_key(background: dict[str, Any]) -> str:
        if "phi_scf" in background:
            return "phi_scf"
        candidates = [k for k in background if "phi" in k.lower() and "prime" not in k.lower()]
        if not candidates:
            raise RuntimeError(f"Could not identify scalar-field column in CLASS background keys: {list(background)}")
        # Prefer the standard CLASS scalar-field label if decoration changed.
        candidates.sort(key=lambda k: ("scf" not in k.lower(), len(k)))
        return candidates[0]

    def _normalization_args(self, args: dict[str, Any], phi_ref: float) -> dict[str, Any]:
        trial = dict(args)
        trial["rims_phi_ref"] = float(phi_ref)
        trial["rims_require_normalization"] = "no"
        # Only the homogeneous background is required for the fixed-point solve.
        trial["output"] = ""
        for key in [
            "lensing",
            "l_max_scalars",
            "non_linear",
            "hmcode_version",
            "P_k_max_1/Mpc",
            "P_k_max_h/Mpc",
            "z_pk",
        ]:
            trial.pop(key, None)
        return trial

    def _solve_phi_ref(self, args: dict[str, Any]) -> float:
        if not self._is_rims_enabled(args):
            return self.rims_norm_default_ref

        alpha = float(args.get("rims_alpha_U", 0.0))
        if abs(alpha) < 1.0e-14:
            # At alpha_U=0 the mass map is constant and the reference point is
            # physically irrelevant.  A fixed value avoids an artificial flat
            # sampling direction.
            return self.rims_norm_default_ref

        signature = (
            round(float(args.get("H0", 0.0)), 7),
            round(float(args.get("h", 0.0)), 9),
            round(float(args.get("omega_b", 0.0)), 10),
            round(float(args.get("omega_cdm", 0.0)), 10),
            round(float(args.get("omega_idm", 0.0)), 10),
            round(float(args.get("Omega_scf", 0.0)), 9),
            round(alpha, 9),
            round(float(args.get("rims_phi_transition", 0.0)), 7),
        )
        guess = self._rims_last_phi_ref if self._rims_last_signature is not None else self.rims_norm_default_ref

        for _ in range(int(self.rims_norm_maxiter)):
            trial = self._normalization_args(args, guess)
            raw = self.classy_module.Class()
            try:
                raw.set(**trial)
                raw.compute()
                bg = raw.get_background()
                key = self._pick_phi_key(bg)
                phi_today = float(np.asarray(bg[key])[-1])
            finally:
                try:
                    raw.empty()
                except Exception:
                    pass

            if not np.isfinite(phi_today):
                raise self.classy_module.CosmoComputationError("RIMS phi_ref normalization returned non-finite phi(a=1)")

            if abs(phi_today - guess) <= self.rims_norm_tolerance:
                self._rims_last_phi_ref = phi_today
                self._rims_last_signature = signature
                return phi_today

            # The V7 normalization map is a rapidly convergent fixed point in
            # the validated domain.  Mild damping protects excursions near the
            # stability boundary without changing the fixed point.
            guess = 0.25 * guess + 0.75 * phi_today

        raise self.classy_module.CosmoComputationError(
            f"RIMS phi_ref normalization did not converge after {self.rims_norm_maxiter} iterations"
        )

    def set(self, params_values_dict):
        # Reproduce Cobaya's standard parameter translation, then insert the
        # deterministic RIMS normalization before the full calculation.
        if not self.extra_args["output"]:
            for key in ["non_linear", "hmcode_version"]:
                self.extra_args.pop(key, None)

        args = {self.translate_param(p): v for p, v in params_values_dict.items()}
        args.update(self.extra_args)

        if self._is_rims_enabled(args):
            args["rims_phi_ref"] = self._solve_phi_ref(args)
            args["rims_require_normalization"] = "yes"

        self.param_dict_debug("Setting parameters: %r", args)
        self.classy.set(**args)
