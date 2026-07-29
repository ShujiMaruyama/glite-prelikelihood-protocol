from __future__ import annotations

from typing import Any

import numpy as np
from cobaya.theories.classy.classy import classy as CobayaClassy


class RIMSClassy(CobayaClassy):
    """Cobaya CLASS wrapper with deterministic RIMS mass normalization.

    ``rims_phi_ref`` is not a cosmological degree of freedom.  It is the
    reference field value that enforces m_d(a=1)=m_U.  For each sampled
    cosmology this wrapper solves phi_ref=phi(z=0) with a background-only
    CLASS calculation and then runs the requested full calculation with the
    native RIMS normalization gate enabled.
    """

    rims_norm_tolerance: float = 2.0e-9
    rims_norm_maxiter: int = 16
    rims_norm_default_ref: float = 4.11730971054

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
        candidates.sort(key=lambda k: ("scf" not in k.lower(), len(k)))
        return candidates[0]

    @staticmethod
    def _today_index(background: dict[str, Any]) -> int:
        # Do not assume the Python background arrays inherit the file-output
        # ordering.  Select the z=0 entry explicitly.
        zkeys = [k for k in background if k.strip().lower() == "z"]
        if zkeys:
            z = np.asarray(background[zkeys[0]], dtype=float)
            return int(np.nanargmin(np.abs(z)))
        # CLASS normally returns early->late ordering; retain a safe fallback.
        return -1

    def _normalization_args(self, args: dict[str, Any], phi_ref: float) -> dict[str, Any]:
        trial = dict(args)
        trial["rims_phi_ref"] = float(phi_ref)
        trial["rims_require_normalization"] = "no"
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
                idx = self._today_index(bg)
                phi_today = float(np.asarray(bg[key], dtype=float)[idx])
            finally:
                try:
                    raw.empty()
                except Exception:
                    pass

            if not np.isfinite(phi_today):
                raise self.classy_module.CosmoComputationError(
                    "RIMS phi_ref normalization returned non-finite phi(z=0)"
                )

            if abs(phi_today - guess) <= self.rims_norm_tolerance:
                self._rims_last_phi_ref = phi_today
                self._rims_last_signature = signature
                return phi_today

            guess = 0.25 * guess + 0.75 * phi_today

        raise self.classy_module.CosmoComputationError(
            f"RIMS phi_ref normalization did not converge after {self.rims_norm_maxiter} iterations; last={guess}"
        )

    def set(self, params_values_dict):
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
