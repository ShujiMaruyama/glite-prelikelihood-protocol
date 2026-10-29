import importlib.util
import json
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import c42b_compile_gate as b

class TestCompileOnlyGate(unittest.TestCase):
    def test_pinned_source_sha(self):
        self.assertEqual(b.FIXED['background_after'],'dbbaa6b24b2b87cc6c058b4313ba026722467f8f23e80e8fde328e60c1467b9d')
        self.assertEqual(b.FIXED['ndf_after'],'c48e0b807df2d0cc2a859e59fc06483cd866bab199b65afb3db66f3b56070f38')
    def test_reject_missing_pinned(self):
        with tempfile.TemporaryDirectory() as d:
            s=pathlib.Path(d)
            (s/'source').mkdir();(s/'tools').mkdir()
            (s/'source/background.c').write_text('incorrect')
            (s/'tools/evolver_ndf15.c').write_text('incorrect')
            with self.assertRaises(ValueError):b.stage(s,s/'audit')
            self.assertFalse((s/'audit').exists())
    def test_no_class_compute(self):
        self.assertNotIn('classy.Class()',pathlib.Path(b.__file__).read_text())
        self.assertNotIn('.compute()',pathlib.Path(b.__file__).read_text())
    def test_no_veto_manipulation(self):
        src=pathlib.Path(b.__file__).read_text()
        self.assertNotIn('rims_enforce_stability="no"',src)
        self.assertNotIn('rims_stability_tolerance=0',src)
    def test_already_staged_refused(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d);target=p/'out';target.mkdir()
            with self.assertRaises(ValueError):b.stage(p,target)
    def test_missing_stage_receipt_refused(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)
            with self.assertRaises(ValueError):b.verify(p,p)
    def test_physics_verification_fails_closed(self):
        with self.assertRaises(ValueError):b.verify_original_physics('RIMS_C39_TERMS_V1')
    def test_pinned_static_artifact_inputs(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)
            (p/'source').mkdir();(p/'tools').mkdir()
            (p/'source/background.c').write_bytes(b'wrong physics')
            (p/'tools/evolver_ndf15.c').write_bytes(b'wrong')
            with self.assertRaises(ValueError):b.stage(p,p/'out')
    def test_native_before_import_not_certified(self):
        self.assertFalse('PINNED_C42A_NATIVE_EXTENSION_COMPILED_AND_IMPORTED' == 'C42A_PINNED_INSTRUMENTED_SOURCE_STAGED')

if __name__=='__main__':unittest.main()
