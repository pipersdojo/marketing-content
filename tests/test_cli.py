import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ENV = {
    **os.environ,
    "PYTHONPATH": str(REPO_ROOT / "src"),
    "MARKETING_AGENT_PROMPTS_DIR": str(REPO_ROOT / "prompts"),
    "MARKETING_AGENT_RUBRIC_FILE": str(REPO_ROOT / "qa" / "rubric.json"),
}


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

    def test_qa_strict_fails_on_missing_criticals(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            run_cli(["create", "2026-04-qa-strict"], cwd)
            run_cli(["open", "2026-04-qa-strict"], cwd)
            result = run_cli(["qa", "--strict"], cwd, expect_ok=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing_primary_cta", result.stdout)

    def test_generate_template_provider_outputs_variants(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            run_cli(["create", "2026-04-generate-template"], cwd)
            run_cli(["open", "2026-04-generate-template"], cwd)

            run_cli(["set", "offer.name", "Offer"], cwd)
            run_cli(["set", "offer.summary", "Summary"], cwd)
            run_cli(["set", "offer.regular_price", "100"], cwd)
            run_cli(["set", "offer.promo_price", "50"], cwd)
            run_cli(["set", "offer.deadline_iso", "2026-12-31T23:59:00Z"], cwd)
            run_cli(["set", "market_diagnosis_10.keeps_them_awake_at_night", "stalled progress"], cwd)
            run_cli(["set", "market_diagnosis_10.fears", '["fear1"]'], cwd)
            run_cli(["set", "market_diagnosis_10.anger_and_targets", '["anger1"]'], cwd)
            run_cli(["set", "market_diagnosis_10.top_3_daily_frustrations", '["f1","f2","f3"]'], cwd)
            run_cli(["set", "market_diagnosis_10.key_trends_affecting_them", '["trend1"]'], cwd)
            run_cli(["set", "market_diagnosis_10.secret_ardent_desires", '["desire1"]'], cwd)
            run_cli(["set", "market_diagnosis_10.built_in_decision_bias", "analytical"], cwd)
            run_cli(["set", "market_diagnosis_10.own_language", '["jargon"]'], cwd)
            run_cli(["set", "market_diagnosis_10.competitors_and_their_pitch", '["comp"]'], cwd)
            run_cli(["set", "market_diagnosis_10.failed_competing_attempts", '["failed"]'], cwd)
            run_cli(["set", "buyer_priorities_ranked", '[{"priority":1,"want":"result","evidence":"x"}]'], cwd)
            run_cli(["set", "offer_decomposition.features", '["feature"]'], cwd)
            run_cli(["set", "offer_decomposition.benefits", '["benefit"]'], cwd)
            run_cli(["set", "offer_decomposition.hidden_benefit.statement", "hidden value"], cwd)
            run_cli(["set", "objection_bank.reasons_not_to_respond", '["obj"]'], cwd)
            run_cli(["set", "objection_bank.rebuttals", '[{"objection":"obj","response":"resp"}]'], cwd)
            run_cli(["set", "messaging_strategy.cta.primary", "Enroll now"], cwd)
            run_cli(["set", "messaging_strategy.cta.urgency_devices", '["deadline"]'], cwd)

            run_cli(["generate", "--channels", "email", "--provider", "template", "--variants", "2"], cwd)

            artifact_path = cwd / "campaigns" / "2026-04-generate-template" / "artifacts" / "email.generated.yaml"
            artifact = json.loads(artifact_path.read_text())
            self.assertEqual(len(artifact["variants"]), 2)
            self.assertEqual(artifact["variants"][0]["provider"], "template")


if __name__ == "__main__":
    unittest.main()
