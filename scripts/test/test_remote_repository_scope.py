"""Upload-scope regression tests; no files or scientific data are written."""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("remote_scope", ROOT / "scripts/manage_remote_repository.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ScopeTests(unittest.TestCase):
    def setUp(self):
        self.rules = MODULE.policy(ROOT)

    def test_small_scientific_results_remain_allowed(self):
        for path in ["results/raw/confusion.csv", "results/summary/report.md", "results/processed/counts.json"]:
            self.assertIsNone(MODULE.reason(path, 1000, self.rules))

    def test_size_boundary_is_strict(self):
        self.assertIsNone(MODULE.reason("results/summary/example.csv", 1999999, self.rules))
        self.assertEqual(MODULE.reason("results/summary/example.csv", 2000000, self.rules), "file_size_limit")

    def test_archives_and_assets_blocked_even_when_small(self):
        for path in ["archive/report.md", "results/archive/report.md", "output/compile-record.txt",
                     "results/processed/counts.npz", "figures/chart.pdf", "legacy/paper.docx"]:
            self.assertIsNotNone(MODULE.reason(path, 10, self.rules))

    def test_path_escape_blocked(self):
        self.assertIsNotNone(MODULE.reason("../example.md", 10, self.rules))
        self.assertIsNotNone(MODULE.reason("/example.md", 10, self.rules))

    def test_active_small_documentation_exceptions(self):
        for path in ["output/README.md", "output/preview-manifest.json",
                     "legacy/figures/four_site_classification/site_coordinates.csv"]:
            self.assertIsNone(MODULE.reason(path, 1000, self.rules))
            self.assertEqual(MODULE.reason(path, 2000000, self.rules), "file_size_limit")


if __name__ == "__main__":
    unittest.main()
