from __future__ import annotations

from typing import Any

import numpy as np
from cobaya.theories.classy.classy import classy as CobayaClassy


class RIMSClassy(CobayaClassy):
    """Cobaya CLASS wrapper with deterministic RIMS mass normalization.

    ``rims_phi_ref`` is a derived normalization coordinate, not a sampled
    cosmological degree of freedom.  The algorithm intentionally matches the
    previously validated profile/optimization pipeline: run the homogeneous
    background with the native normalization gate disabled, read both
    phi(z=0) and rims_mratio(z=0), update phi_ref <- phi(z=0) while the mass
    ratio differs from unity, then execute the full CLASS calculation with
    the native normalization gate enabled.
    """

    rims_norm_tolerance: float = 3.0e-9
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
    def _find_key(background: dict[str, Any], preferred: str, contains: tuple[str, ...]) -> str:
        if preferred in background:
            return preferred
        candidates = []
        for key in background:
            low = key.lower().replace(" ", "").replace("_", "")
            if all(token.lower().replace("_", "") in low for token in contains):
                candidates.append(key)
        if not candidates:
            raise RuntimeError(
                f"Could not identify background key {preferred!r}; available keys={list(background)}"
            )
        candidates.sort(key=len)
        return candidates[0]

    @staticmethod
    def _today_index(background: dict[str, Any]) -> int:
        for key in background:
            if key.strip().lower() == "z":
                z = np.asarray(background[key], dtype=float)
                return int(np.nanargmin(np.abs(z)))
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

    def _background_endpoint(self, args: dict[str, Any], phi_ref: float) -> tuple[float, float]:
        trial = self._normalization_args(args, phi_ref)
        raw = self.classy_module.Class()
        try:
            raw.set(**trial)
            raw.compute()
            bg = raw.get_background()
            idx = self._today_index(bg)
            phi_key = self._find_key(bg, "phi_scf", ("phi", "scf"))
            mratio_key = self._find_key(bg, "rims_mratio", ("rims", "mratio"))
            phi_today = float(np.asarray(bg[phi_key], dtype=float)[idx])
            mratio_today = float(np.asarray(bg[mratio_key], dtype=float)[idx])
        finally:
            try:
                raw.empty()
            except Exception:
                pass
        return phi_today, mratio_today

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
        pref = self._rims_last_phi_ref if self._rims_last_signature is not None else self.rims_norm_default_ref

        for _ in range(int(self.rims_norm_maxiter)):
            phi_today, mratio_today = self._background_endpoint(args, pref)
            if not np.isfinite(phi_today) or not np.isfinite(mratio_today):
                raise self.classy_module.CosmoComputationError(
                    "RIMS normalization returned a non-finite background endpoint"
                )
            if abs(mratio_today - 1.0) <= self.rims_norm_tolerance:
                self._rims_last_phi_ref = pref
                self._rims_last_signature = signature
                return pref
            pref = phi_today

        raise self.classy_module.CosmoComputationError(
            f"RIMS mass normalization did not converge after {self.rims_norm_maxiter} iterations"
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
