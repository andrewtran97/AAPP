import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BENCHMARK_PATH = ROOT / "benchmarks" / "evidence_pipeline_latency_bench.py"
FIXTURE_PATH = ROOT / "tests" / "fixtures" / "evidence_performance" / "sample_records.jsonl"


def load_benchmark_module():
    spec = importlib.util.spec_from_file_location(
        "evidence_pipeline_latency_bench",
        BENCHMARK_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load benchmark module spec")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class EvidencePerformancePlaneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.benchmark = load_benchmark_module()

    def test_load_records(self):
        records = self.benchmark.load_records(FIXTURE_PATH)

        self.assertEqual(len(records), 5)
        self.assertEqual(records[0]["record_id"], "b29-rec-001")

    def test_canonical_bytes_are_deterministic(self):
        left = {
            "b": 2,
            "a": 1,
        }
        right = {
            "a": 1,
            "b": 2,
        }

        self.assertEqual(
            self.benchmark.canonical_bytes(left),
            self.benchmark.canonical_bytes(right),
        )

    def test_benchmark_output_shape(self):
        records = self.benchmark.load_records(FIXTURE_PATH)
        result = self.benchmark.run_benchmark(records, iterations=3)

        required = {
            "record_count",
            "iterations",
            "total_seconds",
            "records_per_second",
            "min_seconds",
            "max_seconds",
            "avg_seconds",
        }

        self.assertEqual(set(result), required)
        self.assertEqual(result["record_count"], 5)
        self.assertEqual(result["iterations"], 3)

        for key in [
            "total_seconds",
            "records_per_second",
            "min_seconds",
            "max_seconds",
            "avg_seconds",
        ]:
            self.assertIsInstance(result[key], float)
            self.assertGreaterEqual(result[key], 0.0)


if __name__ == "__main__":
    unittest.main()
