from __future__ import annotations
from typing import Any
import numpy as np
from cobaya.theories.classy.classy import classy as CobayaClassy


class RIMSShellClassy(CobayaClassy):
    """CLASS wrapper using the physical bounded-shell coordinate u_i.

    The sampled pair is (rims_alpha_U, rims_shell_u_i). The raw transition
    coordinate is deterministically reconstructed as

        phi_t = phi_i - u_i/(2 alpha_U),  phi_i = 4.44.

    The decoupled alpha_U=0 hypothesis is kept as a separate scalar model.
    """

    rims_norm_tolerance: float = 3.0e-9
    rims_norm_maxiter: int = 16
    rims_norm_default_ref: float = 4.11730971054
    rims_phi_i: float = 4.44

    def initialize(self):
        super().initialize()
        self._rims_last_phi_ref = self.rims_norm_default_ref
        self._rims_last_signature = None

    def get_can_support_params(self):
        names = list(super().get_can_support_params())
        for name in [
            "Omega_scf", "omega_idm", "omega_cdm",
            "rims_alpha_U", "rims_shell_u_i",
        ]:
            if name not in names:
                names.append(name)
        return names

    @staticmethod
    def _enabled(args: dict[str, Any]) -> bool:
        v = args.get("rims_enabled", "no")
        return v.strip().lower() in {"yes", "y", "true", "1"} if isinstance(v, str) else bool(v)

    @staticmethod
    def _find_key(bg, preferred, contains):
        if preferred in bg:
            return preferred
        hits = []
        for k in bg:
            low = k.lower().replace(" ", "").replace("_", "")
            if all(t.lower().replace("_", "") in low for t in contains):
                hits.append(k)
        if not hits:
            raise RuntimeError(f"Missing background key {preferred}; keys={list(bg)}")
        return sorted(hits, key=len)[0]

    @staticmethod
    def _today_index(bg):
        for k in bg:
            if k.strip().lower() == "z":
                return int(np.nanargmin(np.abs(np.asarray(bg[k], float))))
        return -1

    def _normalization_args(self, args, phi_ref):
        q = dict(args)
        q["rims_phi_ref"] = float(phi_ref)
        q["rims_require_normalization"] = "no"
        q["output"] = ""
        q.pop("ic", None)
        for k in [
            "lensing", "l_max_scalars", "non_linear", "hmcode_version",
            "P_k_max_1/Mpc", "P_k_max_h/Mpc", "z_pk",
        ]:
            q.pop(k, None)
        return q

    def _background_endpoint(self, args, phi_ref):
        raw = self.classy_module.Class()
        try:
            raw.set(**self._normalization_args(args, phi_ref))
            raw.compute()
            bg = raw.get_background()
            i = self._today_index(bg)
            pk = self._find_key(bg, "phi_scf", ("phi", "scf"))
            mk = self._find_key(bg, "rims_mratio", ("rims", "mratio"))
            return float(np.asarray(bg[pk], float)[i]), float(np.asarray(bg[mk], float)[i])
        finally:
            try:
                raw.empty()
            except Exception:
                pass

    def _solve_phi_ref(self, args):
        alpha = float(args.get("rims_alpha_U", 0.0))
        if not self._enabled(args) or alpha <= 0:
            return self.rims_norm_default_ref
        sig = (
            round(float(args.get("H0", 0)), 7),
            round(float(args.get("omega_b", 0)), 10),
            round(float(args.get("omega_cdm", 0)), 10),
            round(float(args.get("omega_idm", 0)), 10),
            round(float(args.get("Omega_scf", 0)), 9),
            round(alpha, 10),
            round(float(args.get("rims_phi_transition", 0)), 8),
        )
        pref = self._rims_last_phi_ref if self._rims_last_signature is not None else self.rims_norm_default_ref
        for _ in range(int(self.rims_norm_maxiter)):
            phi, mr = self._background_endpoint(args, pref)
            if not (np.isfinite(phi) and np.isfinite(mr)):
                raise self.classy_module.CosmoComputationError("non-finite RIMS normalization endpoint")
            if abs(mr - 1) <= self.rims_norm_tolerance:
                self._rims_last_phi_ref = pref
                self._rims_last_signature = sig
                return pref
            pref = phi
        raise self.classy_module.CosmoComputationError(
            f"RIMS normalization did not converge in {self.rims_norm_maxiter} iterations"
        )

    def set(self, params_values_dict):
        if not self.extra_args.get("output", ""):
            for k in ["non_linear", "hmcode_version"]:
                self.extra_args.pop(k, None)
        args = {self.translate_param(p): v for p, v in params_values_dict.items()}
        args.update(self.extra_args)
        if self._enabled(args):
            alpha = float(args.pop("rims_alpha_U"))
            u = float(args.pop("rims_shell_u_i"))
            if alpha <= 0:
                raise self.classy_module.CosmoComputationError("interacting shell branch requires alpha_U>0")
            args["rims_alpha_U"] = alpha
            args["rims_phi_transition"] = self.rims_phi_i - u / (2 * alpha)
            args["rims_phi_ref"] = self._solve_phi_ref(args)
            args["rims_require_normalization"] = "yes"
        self.param_dict_debug("Setting shell-adapted parameters: %r", args)
        self.classy.set(**args)
