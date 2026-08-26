import os
import unittest

from app.services.ml_anomaly_service import (
    _safe_joblib_load,
    _safe_realpath,
    MODEL_PATH,
    _MODELS_DIR,
)


class TestModelLoadingSecurity(unittest.TestCase):
    def test_path_traversal_rejected(self):
        with self.assertRaises(ValueError):
            _safe_realpath("/etc/passwd")

    def test_unexpected_filename_rejected(self):
        bad_path = os.path.join(_MODELS_DIR, "../models/malicious.pkl")
        result = _safe_joblib_load(bad_path)
        self.assertIsNone(result)

    def test_missing_model_returns_none(self):
        missing = os.path.join(_MODELS_DIR, "nonexistent.pkl")
        result = _safe_joblib_load(missing)
        self.assertIsNone(result)

    def test_allowed_paths_resolve_inside_models_dir(self):
        resolved = _safe_realpath(MODEL_PATH)
        self.assertTrue(resolved.startswith(os.path.realpath(_MODELS_DIR)))


if __name__ == "__main__":
    unittest.main()
