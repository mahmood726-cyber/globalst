import json
import unittest
import hashlib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_PATH = PROJECT_ROOT / "data" / "cvd_synthesis_input.json"
OUTPUT_PATH = PROJECT_ROOT / "output" / "st_nma_results.json"

def calculate_hash(file_path):
    with open(file_path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

class TestGlobalSTPipeline(unittest.TestCase):
    def test_input_exists(self):
        self.assertTrue(INPUT_PATH.exists())

    def test_output_exists(self):
        self.assertTrue(OUTPUT_PATH.exists())

    @unittest.skipUnless(OUTPUT_PATH.exists(), "Pipeline output not generated yet")
    def test_results_structure(self):
        with open(OUTPUT_PATH, 'r') as f:
            data = json.load(f)
        self.assertIn("results", data)
        self.assertIn("truthcert", data)
        self.assertGreater(len(data['results']), 0)
        
    @unittest.skipUnless(OUTPUT_PATH.exists(), "Pipeline output not generated yet")
    def test_truthcert_integrity(self):
        # Verify that the results contain hashes for each region's evidence
        with open(OUTPUT_PATH, 'r') as f:
            data = json.load(f)
        for res in data['results']:
            self.assertIn("evidence_hash", res)
            self.assertEqual(len(res['evidence_hash']), 64) # SHA-256 length

if __name__ == "__main__":
    unittest.main()
