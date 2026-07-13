import ast
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from aapp.bounded_mutation_verifier import verify_mutation_state
from aapp.bounded_mutation_workflow import digest_bytes, run_bounded_mutation


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "bounded_mutation_workflow"
    / "sample_workflow.json"
)


class BoundedMutationWorkflowTests(unittest.TestCase):
    def load_fixture(self):
        return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    def prepare_workspace(self):
        fixture = self.load_fixture()
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        target = root / fixture["request"]["target_relative_path"]
        target.parent.mkdir(parents=True)
        target.write_text(fixture["initial_content"], encoding="utf-8")
        request = dict(fixture["request"])
        request["workspace_root"] = str(root)
        return temp, root, target, request, fixture

    def test_successful_mutation_requires_independent_verification_before_receipt(self):
        temp, _root, target, request, fixture = self.prepare_workspace()
        self.addCleanup(temp.cleanup)

        result = run_bounded_mutation(request)

        self.assertEqual(result["status"], "VERIFIED")
        self.assertTrue(result["execution_performed"])
        self.assertEqual(target.read_text(encoding="utf-8"), fixture["expected_content"])
        self.assertEqual(result["verifier"]["verdict"], "VERIFIED")
        self.assertIsNotNone(result["receipt"])
        self.assertEqual(result["receipt"]["verifier_verdict"], "VERIFIED")
        self.assertEqual(result["receipt"]["pre_state_digest"], request["expected_pre_state_digest"])
        self.assertEqual(result["receipt"]["post_state_digest"], digest_bytes(fixture["expected_content"].encode("utf-8")))

    def test_absolute_target_path_is_denied_without_mutation(self):
        temp, _root, target, request, fixture = self.prepare_workspace()
        self.addCleanup(temp.cleanup)
        request["target_relative_path"] = str(target)

        result = run_bounded_mutation(request)

        self.assertEqual(result["status"], "DENIED")
        self.assertIn("ABSOLUTE_TARGET_PATH_FORBIDDEN", result["reason_codes"])
        self.assertFalse(result["execution_performed"])
        self.assertIsNone(result["receipt"])
        self.assertEqual(target.read_text(encoding="utf-8"), fixture["initial_content"])

    def test_path_traversal_is_denied_without_mutation(self):
        temp, root, target, request, fixture = self.prepare_workspace()
        self.addCleanup(temp.cleanup)
        outside = root.parent / f"{root.name}-outside.txt"
        outside.write_text(fixture["initial_content"], encoding="utf-8")
        self.addCleanup(lambda: outside.unlink(missing_ok=True))
        request["target_relative_path"] = "../" + outside.name

        result = run_bounded_mutation(request)

        self.assertEqual(result["status"], "DENIED")
        self.assertIn("PATH_TRAVERSAL_FORBIDDEN", result["reason_codes"])
        self.assertEqual(outside.read_text(encoding="utf-8"), fixture["initial_content"])
        self.assertEqual(target.read_text(encoding="utf-8"), fixture["initial_content"])

    def test_target_symlink_is_denied(self):
        temp, root, target, request, fixture = self.prepare_workspace()
        self.addCleanup(temp.cleanup)
        real_target = root / "workspace" / "real.txt"
        target.rename(real_target)
        target.symlink_to(real_target.name)

        result = run_bounded_mutation(request)

        self.assertEqual(result["status"], "DENIED")
        self.assertIn("TARGET_SYMLINK_FORBIDDEN", result["reason_codes"])
        self.assertEqual(real_target.read_text(encoding="utf-8"), fixture["initial_content"])

    def test_parent_symlink_is_denied(self):
        fixture = self.load_fixture()
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        actual = root / "actual"
        actual.mkdir()
        target = actual / "target.txt"
        target.write_text(fixture["initial_content"], encoding="utf-8")
        (root / "link").symlink_to(actual, target_is_directory=True)
        request = dict(fixture["request"])
        request["workspace_root"] = str(root)
        request["target_relative_path"] = "link/target.txt"

        result = run_bounded_mutation(request)

        self.assertEqual(result["status"], "DENIED")
        self.assertIn("PARENT_SYMLINK_FORBIDDEN", result["reason_codes"])
        self.assertEqual(target.read_text(encoding="utf-8"), fixture["initial_content"])

    def test_hard_linked_target_is_denied(self):
        temp, root, target, request, fixture = self.prepare_workspace()
        self.addCleanup(temp.cleanup)
        alias = root / "workspace" / "alias.txt"
        os.link(target, alias)

        result = run_bounded_mutation(request)

        self.assertEqual(result["status"], "DENIED")
        self.assertIn("TARGET_HARD_LINKED", result["reason_codes"])
        self.assertEqual(target.read_text(encoding="utf-8"), fixture["initial_content"])

    def test_stale_pre_state_digest_is_denied(self):
        temp, _root, target, request, fixture = self.prepare_workspace()
        self.addCleanup(temp.cleanup)
        request["expected_pre_state_digest"] = digest_bytes(b"stale")

        result = run_bounded_mutation(request)

        self.assertEqual(result["status"], "DENIED")
        self.assertIn("PRE_STATE_DIGEST_MISMATCH", result["reason_codes"])
        self.assertEqual(target.read_text(encoding="utf-8"), fixture["initial_content"])

    def test_missing_authority_reference_is_denied(self):
        temp, _root, target, request, fixture = self.prepare_workspace()
        self.addCleanup(temp.cleanup)
        del request["capability_ref"]

        result = run_bounded_mutation(request)

        self.assertEqual(result["status"], "DENIED")
        self.assertIn("MISSING_REQUIRED_FIELD", result["reason_codes"])
        self.assertEqual(target.read_text(encoding="utf-8"), fixture["initial_content"])

    def test_multiple_matches_are_denied(self):
        temp, _root, target, request, _fixture = self.prepare_workspace()
        self.addCleanup(temp.cleanup)
        target.write_text("before\nbefore\n", encoding="utf-8")
        request["expected_pre_state_digest"] = digest_bytes(target.read_bytes())

        result = run_bounded_mutation(request)

        self.assertEqual(result["status"], "DENIED")
        self.assertIn("EXACT_TEXT_NOT_UNIQUE", result["reason_codes"])
        self.assertEqual(target.read_text(encoding="utf-8"), "before\nbefore\n")

    def test_verifier_failure_restores_pre_state_and_emits_no_receipt(self):
        temp, _root, target, request, fixture = self.prepare_workspace()
        self.addCleanup(temp.cleanup)
        failed_verdict = {
            "verdict": "FAILED",
            "reason_codes": ["INJECTED_VERIFIER_FAILURE"],
            "actual_post_state_digest": None,
        }

        with mock.patch(
            "aapp.bounded_mutation_workflow.verify_mutation_state",
            return_value=failed_verdict,
        ):
            result = run_bounded_mutation(request)

        self.assertEqual(result["status"], "RECOVERED_FAILURE")
        self.assertEqual(result["recovery"]["status"], "RESTORED")
        self.assertIsNone(result["receipt"])
        self.assertEqual(target.read_text(encoding="utf-8"), fixture["initial_content"])

    def test_failed_recovery_creates_incident_shaped_evidence(self):
        temp, _root, _target, request, _fixture = self.prepare_workspace()
        self.addCleanup(temp.cleanup)
        failed_verdict = {
            "verdict": "FAILED",
            "reason_codes": ["INJECTED_VERIFIER_FAILURE"],
            "actual_post_state_digest": None,
        }
        failed_recovery = {
            "status": "FAILED",
            "reason_codes": ["INJECTED_RECOVERY_FAILURE"],
            "restored_digest": None,
        }

        with mock.patch(
            "aapp.bounded_mutation_workflow.verify_mutation_state",
            return_value=failed_verdict,
        ), mock.patch(
            "aapp.bounded_mutation_workflow._restore_original",
            return_value=failed_recovery,
        ):
            result = run_bounded_mutation(request)

        self.assertEqual(result["status"], "INCIDENT")
        self.assertIsNone(result["receipt"])
        self.assertIsNotNone(result["incident"])
        self.assertEqual(
            result["incident"]["incident_type"],
            "BOUNDED_MUTATION_RECOVERY_FAILURE",
        )

    def test_independent_verifier_reads_actual_filesystem_state(self):
        temp, _root, target, request, fixture = self.prepare_workspace()
        self.addCleanup(temp.cleanup)
        metadata = target.stat()
        target.write_text(fixture["expected_content"], encoding="utf-8")
        expected_digest = digest_bytes(fixture["expected_content"].encode("utf-8"))

        verified = verify_mutation_state(
            workspace_root=request["workspace_root"],
            target_relative_path=request["target_relative_path"],
            expected_post_state_digest=expected_digest,
            expected_device=metadata.st_dev,
            expected_inode=metadata.st_ino,
        )
        target.write_text("tampered\n", encoding="utf-8")
        failed = verify_mutation_state(
            workspace_root=request["workspace_root"],
            target_relative_path=request["target_relative_path"],
            expected_post_state_digest=expected_digest,
            expected_device=metadata.st_dev,
            expected_inode=metadata.st_ino,
        )

        self.assertEqual(verified["verdict"], "VERIFIED")
        self.assertEqual(failed["verdict"], "FAILED")
        self.assertIn("POST_STATE_DIGEST_MISMATCH", failed["reason_codes"])

    def test_runtime_modules_do_not_import_network_or_subprocess_modules(self):
        forbidden = {"socket", "subprocess", "requests", "urllib", "http", "ftplib"}
        for relative_path in (
            "aapp/bounded_mutation_workflow.py",
            "aapp/bounded_mutation_verifier.py",
        ):
            source = (Path(__file__).parents[1] / relative_path).read_text(encoding="utf-8")
            tree = ast.parse(source)
            imported = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported.update(alias.name.split(".")[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imported.add(node.module.split(".")[0])
            self.assertTrue(forbidden.isdisjoint(imported), (relative_path, imported))


if __name__ == "__main__":
    unittest.main()
