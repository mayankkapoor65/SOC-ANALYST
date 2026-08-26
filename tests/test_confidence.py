import unittest

from app.services.hybrid_detection_service import calculate_confidence, _safe_unit_interval


class TestSafeUnitInterval(unittest.TestCase):
    def test_none_returns_default(self):
        self.assertEqual(_safe_unit_interval(None), 0.0)

    def test_negative_clamped_to_zero(self):
        self.assertEqual(_safe_unit_interval(-0.5), 0.0)

    def test_above_one_clamped(self):
        self.assertEqual(_safe_unit_interval(1.7), 1.0)

    def test_valid_value_unchanged(self):
        self.assertEqual(_safe_unit_interval(0.5), 0.5)

    def test_invalid_string_returns_default(self):
        self.assertEqual(_safe_unit_interval("bad"), 0.0)


class TestCalculateConfidence(unittest.TestCase):
    def test_all_false_returns_zero(self):
        self.assertEqual(calculate_confidence(False, False, False, 0, 0, 0), 0.0)

    def test_none_ml_score_safe(self):
        result = calculate_confidence(False, True, False, 0, None, 0)
        self.assertEqual(result, 0.0)

    def test_negative_ml_score_clamped(self):
        result = calculate_confidence(False, True, False, 0, -0.5, 0)
        self.assertEqual(result, 0.0)

    def test_high_ml_score_capped(self):
        result = calculate_confidence(False, True, False, 0, 1.7, 0)
        self.assertEqual(result, 0.35)

    def test_never_exceeds_one(self):
        result = calculate_confidence(True, True, True, 100, 1.0, 30)
        self.assertLessEqual(result, 1.0)
        self.assertGreaterEqual(result, 0.0)

    def test_never_negative(self):
        result = calculate_confidence(False, True, False, 0, -1.0, -10)
        self.assertGreaterEqual(result, 0.0)

    def test_negative_deviation_score_safe(self):
        result = calculate_confidence(False, False, True, 0, 0, -10)
        self.assertEqual(result, 0.0)


if __name__ == "__main__":
    unittest.main()
