import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ENV = {**os.environ, "PYTHONPATH": str(REPO_ROOT / "src")}


def run_cli(args, cwd, input_text=None, expect_ok=True):
    cmd = ["python", "-m", "marketing_agent.cli", *args]
    result = subprocess.run(
        cmd,
        cwd=cwd,
        env=ENV,
        text=True,
        input=input_text,
        capture_output=True,
    )
    if expect_ok and result.returncode != 0:
        raise AssertionError(f"Command failed: {' '.join(cmd)}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    return result


class CampaignCliTests(unittest.TestCase):
    def test_create_open_and_readiness(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            run_cli(["create", "2026-04-test-campaign"], cwd)
            run_cli(["open", "2026-04-test-campaign"], cwd)
            result = run_cli(["readiness-score"], cwd)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["score"], 0)
            self.assertGreater(len(payload["missing_required"]), 0)

    def test_intake_interactive_sets_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            run_cli(["create", "2026-04-intake-test"], cwd)
            run_cli(["open", "2026-04-intake-test"], cwd)
            run_cli(["intake", "--interactive", "--max-questions", "1"], cwd, input_text="Demo Offer\n")

            campaign_file = cwd / "campaigns" / "2026-04-intake-test" / "campaign.yaml"
            data = json.loads(campaign_file.read_text())
            self.assertEqual(data["offer"]["name"], "Demo Offer")
            self.assertGreaterEqual(data["qa"]["readiness_score"], 1)

    def test_generate_gate_when_readiness_low(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            run_cli(["create", "2026-04-gate-test"], cwd)
            run_cli(["open", "2026-04-gate-test"], cwd)
            result = run_cli(["generate"], cwd, expect_ok=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Minimum 85 required", result.stderr)

    def test_qa_and_export_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            run_cli(["create", "2026-04-qa-export"], cwd)
            run_cli(["open", "2026-04-qa-export"], cwd)
            run_cli(["qa"], cwd)
            run_cli(["export"], cwd)

            qa_dir = cwd / "campaigns" / "2026-04-qa-export" / "qa"
            export_dir = cwd / "campaigns" / "2026-04-qa-export" / "exports"
            self.assertTrue(any(qa_dir.glob("qa-*.json")))
            self.assertTrue(any(export_dir.glob("scheduler-package-*.json")))


if __name__ == "__main__":
    unittest.main()
