import json
import os
import unittest
import hashlib

def calculate_hash(file_path):
    with open(file_path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

class TestGlobalSTPipeline(unittest.TestCase):
    def test_input_exists(self):
        self.assertTrue(os.path.exists("globalst/data/cvd_synthesis_input.json"))

    def test_output_exists(self):
        self.assertTrue(os.path.exists("globalst/output/st_nma_results.json"))

    def test_results_structure(self):
        with open("globalst/output/st_nma_results.json", 'r') as f:
            data = json.load(f)
        self.assertIn("results", data)
        self.assertIn("truthcert", data)
        self.assertGreater(len(data['results']), 0)
        
    def test_truthcert_integrity(self):
        # Verify that the results contain hashes for each region's evidence
        with open("globalst/output/st_nma_results.json", 'r') as f:
            data = json.load(f)
        for res in data['results']:
            self.assertIn("evidence_hash", res)
            self.assertEqual(len(res['evidence_hash']), 64) # SHA-256 length

if __name__ == "__main__":
    unittest.main()
