import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from c42a_source_probe import inject,BACKGROUND_HOOKS,NDF_HOOKS,prepare,sha,git_blob_sha1

def fixture(hooks):
    return ''.join('\n-- SECTION --\n'+h[1] for h in hooks)

class SourceGateTests(unittest.TestCase):
    def test_background_anchor_insert_and_reconstruct(self):
        base=fixture(BACKGROUND_HOOKS)
        result=inject(base,BACKGROUND_HOOKS,'background')
        self.assertIn('RIMS_C42A_INIT_OK_V1',result)
        self.assertIn('RIMS_C42A_OUTPUT_OK_V1',result)
        self.assertIn('class_call(background_functions(',result)
        self.assertNotEqual(result,base)
    def test_ndf_acceptance_hook_after_stepstat_increment(self):
        base=fixture(NDF_HOOKS)
        result=inject(base,NDF_HOOKS,'ndf')
        self.assertLess(result.index('stepstat[0] += 1;'),result.index('RIMS_C42A_NDF_STEP_OK_V1'))
        self.assertLess(result.index('RIMS_C42A_NDF_STEP_OK_V1'),result.index('/* Update dif: */'))
    def test_duplicated_anchor_fails(self):
        a=fixture(BACKGROUND_HOOKS)
        self.assertRaisesRegex(ValueError,'ambiguous',inject,a+BACKGROUND_HOOKS[0][1],BACKGROUND_HOOKS,'background')
    def test_missing_anchor_fails(self):
        a=fixture(NDF_HOOKS)
        self.assertRaisesRegex(ValueError,'ambiguous',inject,a.replace('stepstat[0] += 1;','stepstat[0] += 2;'),NDF_HOOKS,'ndf')
    def test_reoverlay_forbidden(self):
        a=fixture(NDF_HOOKS)
        instrumented=inject(a,NDF_HOOKS,'ndf')
        self.assertRaisesRegex(ValueError,'pre-existing',inject,instrumented,NDF_HOOKS,'ndf')
    def test_rejects_non_sha_pinned_bkg(self):
        self.assertRaisesRegex(ValueError,'SHA256 not pinned',prepare,b'example',b'solver')
    def test_git_blob_sha(self):
        import hashlib
        self.assertEqual(git_blob_sha1(b'hello\n'),hashlib.sha1(b'blob 6\0hello\n').hexdigest())
    def test_all_markers_are_source_only(self):
        hooks=BACKGROUND_HOOKS+NDF_HOOKS
        self.assertEqual(len(hooks),5)
        self.assertTrue(all('fprintf(stderr,' in x[2] for x in hooks))
        self.assertTrue(all('RIMS_C42A_' in x[2] for x in hooks))
        self.assertTrue(all('class_test(' not in x[2] and 'ppr->tol_' not in x[2] for x in hooks))
    def test_gate_does_not_change_physics_input(self):
        b=inject(fixture(BACKGROUND_HOOKS),BACKGROUND_HOOKS,'background')
        self.assertNotIn('rims_enforce_stability =',b)
        self.assertNotIn('rims_stability_tolerance =',b)
    def test_output_is_source_grid_not_claimed_integrator_endpoint(self):
        code=inject(fixture(BACKGROUND_HOOKS),BACKGROUND_HOOKS,'background')
        self.assertIn('index_loga < 16',code)
        self.assertIn('INTERPOLATED',code)

if __name__=='__main__':unittest.main()
