from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.cwd()
CAMPAIGNS_DIR = ROOT / "campaigns"
CONTEXT_FILE = ROOT / ".campaign-context"

REQUIRED_PATHS: dict[str, int] = {
    "offer.name": 3,
    "offer.summary": 3,
    "offer.regular_price": 3,
    "offer.promo_price": 3,
    "offer.deadline_iso": 3,
    "market_diagnosis_10.keeps_them_awake_at_night": 3,
    "market_diagnosis_10.fears": 3,
    "market_diagnosis_10.anger_and_targets": 3,
    "market_diagnosis_10.top_3_daily_frustrations": 3,
    "market_diagnosis_10.key_trends_affecting_them": 3,
    "market_diagnosis_10.secret_ardent_desires": 3,
    "market_diagnosis_10.built_in_decision_bias": 3,
    "market_diagnosis_10.own_language": 3,
    "market_diagnosis_10.competitors_and_their_pitch": 3,
    "market_diagnosis_10.failed_competing_attempts": 3,
    "buyer_priorities_ranked": 2,
    "offer_decomposition.features": 3,
    "offer_decomposition.benefits": 3,
    "offer_decomposition.hidden_benefit.statement": 2,
    "objection_bank.reasons_not_to_respond": 2,
    "objection_bank.rebuttals": 2,
    "messaging_strategy.cta.primary": 2,
    "messaging_strategy.cta.urgency_devices": 2,
}

INTAKE_QUESTIONS: dict[str, str] = {
    "market_diagnosis_10.keeps_them_awake_at_night": "What keeps them awake at night?",
    "market_diagnosis_10.fears": "What are they afraid of?",
    "market_diagnosis_10.anger_and_targets": "What are they angry about, and at whom?",
    "market_diagnosis_10.top_3_daily_frustrations": "What are their top 3 daily frustrations?",
    "market_diagnosis_10.key_trends_affecting_them": "What trends are impacting their life/business?",
    "market_diagnosis_10.secret_ardent_desires": "What do they secretly desire most?",
    "market_diagnosis_10.built_in_decision_bias": "Is there a decision-making bias?",
    "market_diagnosis_10.own_language": "What language/jargon do they use?",
    "market_diagnosis_10.competitors_and_their_pitch": "Who else sells similar offers, and how?",
    "market_diagnosis_10.failed_competing_attempts": "What similar attempts have failed and why?",
    "offer_decomposition.hidden_benefit.statement": "What hidden benefit matters deeply but isn't obvious?",
    "objection_bank.reasons_not_to_respond": "What objections, doubts, fears, excuses prevent response?",
    "messaging_strategy.cta.primary": "What is the primary CTA?",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def default_campaign() -> dict[str, Any]:
    return {
        "version": "1.0",
        "campaign_id": "",
        "created_at": "",
        "updated_at": "",
        "status": "intake",
        "owners": {"strategist": "", "copy_lead": "", "approver": ""},
        "brand": {"name": "", "voice": {"adjectives": [], "do_not_use": []}, "compliance_notes": []},
        "offer": {
            "name": "",
            "type": "",
            "summary": "",
            "regular_price": None,
            "promo_price": None,
            "currency": "USD",
            "promo_code": "",
            "deadline_iso": "",
            "quantity_limit": None,
            "guarantee": {"type": "", "terms": ""},
            "links": {"sales_page": "", "checkout_page": "", "thank_you_page": ""},
        },
        "audience": {
            "segment_name": "",
            "market_awareness_stage": "",
            "sophistication_level": "",
            "language_terms": [],
            "decision_biases": [],
        },
        "market_diagnosis_10": {
            "keeps_them_awake_at_night": "",
            "fears": [],
            "anger_and_targets": [],
            "top_3_daily_frustrations": [],
            "key_trends_affecting_them": [],
            "secret_ardent_desires": [],
            "built_in_decision_bias": "",
            "own_language": [],
            "competitors_and_their_pitch": [],
            "failed_competing_attempts": [],
        },
        "buyer_priorities_ranked": [],
        "offer_decomposition": {"features": [], "benefits": [], "hidden_benefit": {"statement": "", "why_it_matters": ""}},
        "damaging_admission": {"disadvantages_or_flaws": [], "admission_copy_blocks": [], "mitigation_points": []},
        "objection_bank": {"reasons_not_to_respond": [], "rebuttals": []},
        "proof_library": {"testimonials": [], "authority_signals": [], "roi_examples": []},
        "messaging_strategy": {
            "core_promise": "",
            "unique_mechanism": "",
            "big_idea": "",
            "primary_formula": "",
            "headline_candidates": [],
            "subheadline_candidates": [],
            "story_assets": {"founder_story": "", "customer_story": "", "slice_of_life_story": ""},
            "cta": {"primary": "", "urgency_devices": [], "intimidation_elements": [], "ego_appeals": []},
        },
        "channel_plan": {
            "channels": {
                "email": {"enabled": True, "goals": [], "constraints": {"min_words": 0, "max_words": 0}, "sequence_plan": []},
                "landing_page": {"enabled": True, "sections_required": ["hero", "problem", "mechanism", "proof", "offer", "guarantee", "faq", "cta", "ps"]},
                "social": {"enabled": True, "platforms": ["instagram", "facebook", "linkedin", "x"], "post_count_target": 0, "creative_needed": True},
                "ads": {"enabled": False, "platforms": [], "variants_target": 0},
            }
        },
        "content_outputs": {"email_sequence": [], "landing_page_copy": {}, "social_posts": [], "ad_copy": [], "creative_briefs": []},
        "qa": {
            "readiness_score": 0,
            "copy_quality_score": 0,
            "checklist_coverage": {"total_items": 0, "completed_items": 0, "missing_required": []},
            "fail_conditions_triggered": [],
            "last_qa_run_at": "",
        },
        "approval": {"required_reviewers": [], "decisions": []},
        "scheduling": {"publishing_window": {"start_iso": "", "end_iso": ""}, "scheduled_items": [], "export_paths": []},
        "reusables": {"winning_headlines": [], "winning_hooks": [], "winning_objection_rebuttals": [], "winning_ctas": [], "lessons_learned": []},
        "revision_history": [],
    }


def _campaign_dir(campaign_id: str) -> Path:
    return CAMPAIGNS_DIR / campaign_id


def _campaign_file(campaign_id: str) -> Path:
    return _campaign_dir(campaign_id) / "campaign.yaml"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _save(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2))


def _require_active() -> tuple[str, Path, dict[str, Any]]:
    if not CONTEXT_FILE.exists():
        raise ValueError("No active campaign. Run: campaign open <campaign_id>")
    campaign_id = CONTEXT_FILE.read_text().strip()
    file_path = _campaign_file(campaign_id)
    if not file_path.exists():
        raise ValueError(f"Campaign file missing: {file_path}")
    return campaign_id, file_path, _load(file_path)


def _is_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, (list, dict)):
        return len(value) == 0
    return False


def _get_path(data: dict[str, Any], path: str) -> Any:
    cur: Any = data
    for key in path.split("."):
        if not isinstance(cur, dict) or key not in cur:
            raise KeyError(path)
        cur = cur[key]
    return cur


def _set_path(data: dict[str, Any], path: str, value: Any) -> Any:
    cur: dict[str, Any] = data
    keys = path.split(".")
    for key in keys[:-1]:
        if key not in cur or not isinstance(cur[key], dict):
            cur[key] = {}
        cur = cur[key]
    old = cur.get(keys[-1])
    cur[keys[-1]] = value
    return old


def _missing_required(data: dict[str, Any]) -> list[str]:
    missing = []
    for path in REQUIRED_PATHS:
        try:
            val = _get_path(data, path)
        except KeyError:
            missing.append(path)
            continue
        if _is_missing(val):
            missing.append(path)
    return missing


def _readiness(data: dict[str, Any]) -> tuple[int, list[str]]:
    total = sum(REQUIRED_PATHS.values())
    missing = _missing_required(data)
    rem = sum(REQUIRED_PATHS[p] for p in missing)
    return round((total - rem) / total * 100), missing


def _update_qa(data: dict[str, Any]) -> tuple[int, list[str]]:
    score, missing = _readiness(data)
    data["qa"]["readiness_score"] = score
    data["qa"]["checklist_coverage"] = {
        "total_items": len(REQUIRED_PATHS),
        "completed_items": len(REQUIRED_PATHS) - len(missing),
        "missing_required": missing,
    }
    data["updated_at"] = now_iso()
    return score, missing


def _write_change(campaign_id: str, path: str, old: Any, new: Any) -> None:
    change_log = _campaign_dir(campaign_id) / "history" / "changes.log"
    change_log.parent.mkdir(parents=True, exist_ok=True)
    with change_log.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"timestamp": now_iso(), "path": path, "old": str(old)[:300], "new": str(new)[:300]}) + "\n")


def cmd_create(args: argparse.Namespace) -> int:
    cid = args.campaign_id
    if len(cid) < 9 or cid[4] != "-" or cid[7] != "-":
        raise ValueError("campaign_id must look like YYYY-MM-slug")
    cdir = _campaign_dir(cid)
    if cdir.exists() and not args.force:
        raise ValueError(f"Campaign exists: {cid} (use --force to overwrite)")
    cdir.mkdir(parents=True, exist_ok=True)
    for sub in ["artifacts", "qa", "history", "exports"]:
        (cdir / sub).mkdir(parents=True, exist_ok=True)
        (cdir / sub / ".gitkeep").touch(exist_ok=True)
    data = default_campaign()
    data["campaign_id"] = cid
    ts = now_iso()
    data["created_at"] = ts
    data["updated_at"] = ts
    score, _ = _update_qa(data)
    _save(_campaign_file(cid), data)
    print(f"Created campaign: {cid}")
    print(f"Readiness score: {score}")
    return 0


def cmd_list(_: argparse.Namespace) -> int:
    CAMPAIGNS_DIR.mkdir(parents=True, exist_ok=True)
    for d in sorted(p.name for p in CAMPAIGNS_DIR.iterdir() if p.is_dir()):
        print(d)
    return 0


def cmd_open(args: argparse.Namespace) -> int:
    cid = args.campaign_id
    cfile = _campaign_file(cid)
    if not cfile.exists():
        raise ValueError(f"Campaign file not found: {cfile}")
    CONTEXT_FILE.write_text(cid)
    data = _load(cfile)
    score, missing = _readiness(data)
    print(f"Active campaign: {cid}")
    print(f"Status: {data.get('status','unknown')}")
    print(f"Readiness: {score}")
    print(f"Missing required fields: {len(missing)}")
    return 0


def cmd_get(args: argparse.Namespace) -> int:
    _, _, data = _require_active()
    value = _get_path(data, args.path)
    print(json.dumps(value, indent=2))
    return 0


def _parse_value(raw: str) -> Any:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        low = raw.lower().strip()
        if low == "true":
            return True
        if low == "false":
            return False
        if low == "null":
            return None
        try:
            return int(raw)
        except ValueError:
            try:
                return float(raw)
            except ValueError:
                return raw


def cmd_set(args: argparse.Namespace) -> int:
    cid, cfile, data = _require_active()
    new_val = _parse_value(args.value)
    old_val = _set_path(data, args.path, new_val)
    score, _ = _update_qa(data)
    _save(cfile, data)
    _write_change(cid, args.path, old_val, new_val)
    print(f"Updated {args.path}")
    print(f"Readiness: {score}")
    return 0


def cmd_save(_: argparse.Namespace) -> int:
    cid, cfile, data = _require_active()
    _update_qa(data)
    _save(cfile, data)
    snapshot = _campaign_dir(cid) / "history" / f"snapshot-{datetime.now().strftime('%Y%m%d-%H%M%S')}.yaml"
    _save(snapshot, data)
    print(f"Saved campaign and snapshot: {snapshot}")
    return 0


def cmd_readiness(_: argparse.Namespace) -> int:
    _, cfile, data = _require_active()
    score, missing = _update_qa(data)
    _save(cfile, data)
    print(json.dumps({"score": score, "status": data.get("status", "unknown"), "missing_required": missing}, indent=2))
    return 0


def cmd_intake(_: argparse.Namespace) -> int:
    _, _, data = _require_active()
    _, missing = _readiness(data)
    if not missing:
        print("All required fields are complete.")
        return 0
    print("Missing required fields and intake prompts:\n")
    for p in missing:
        print(f"- {p}: {INTAKE_QUESTIONS.get(p, f'Provide value for {p}')}")
    return 0


def cmd_generate(args: argparse.Namespace) -> int:
    cid, _, data = _require_active()
    score, missing = _readiness(data)
    if score < 85:
        raise ValueError(f"Readiness score is {score}. Minimum 85 required. Missing: {', '.join(missing)}")
    channels = [c.strip() for c in args.channels.split(",") if c.strip()]
    adir = _campaign_dir(cid) / "artifacts"
    adir.mkdir(parents=True, exist_ok=True)
    for c in channels:
        artifact = {
            "campaign_id": cid,
            "channel": c,
            "generated_at": now_iso(),
            "inputs": {
                "core_promise": data.get("messaging_strategy", {}).get("core_promise", ""),
                "big_idea": data.get("messaging_strategy", {}).get("big_idea", ""),
                "cta": data.get("messaging_strategy", {}).get("cta", {}).get("primary", ""),
            },
            "draft": {"headline": "", "body": "", "cta": data.get("messaging_strategy", {}).get("cta", {}).get("primary", "")},
        }
        _save(adir / f"{c}.generated.yaml", artifact)
        print(f"Generated placeholder artifact: {adir / f'{c}.generated.yaml'}")
    return 0


def cmd_qa(_: argparse.Namespace) -> int:
    cid, cfile, data = _require_active()
    score, missing = _readiness(data)
    fails = []
    if not data.get("messaging_strategy", {}).get("headline_candidates"):
        fails.append("No headline candidates provided")
    if not data.get("messaging_strategy", {}).get("cta", {}).get("primary"):
        fails.append("Missing primary CTA")
    if _is_missing(data.get("offer", {}).get("guarantee", {}).get("terms")):
        fails.append("Guarantee terms missing")
    quality = max(0, min(100, score - len(fails) * 10))
    report = {
        "campaign_id": cid,
        "ran_at": now_iso(),
        "readiness_score": score,
        "copy_quality_score": quality,
        "missing_required": missing,
        "fail_conditions": fails,
    }
    qdir = _campaign_dir(cid) / "qa"
    qdir.mkdir(parents=True, exist_ok=True)
    rpt = qdir / f"qa-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    rpt.write_text(json.dumps(report, indent=2))
    data["qa"]["readiness_score"] = score
    data["qa"]["copy_quality_score"] = quality
    data["qa"]["fail_conditions_triggered"] = fails
    data["qa"]["last_qa_run_at"] = report["ran_at"]
    data["updated_at"] = now_iso()
    _save(cfile, data)
    print(f"QA report written: {rpt}")
    print(json.dumps(report, indent=2))
    return 0


def cmd_export(_: argparse.Namespace) -> int:
    cid, cfile, data = _require_active()
    adir = _campaign_dir(cid) / "artifacts"
    edir = _campaign_dir(cid) / "exports"
    edir.mkdir(parents=True, exist_ok=True)
    artifacts = []
    for f in sorted(adir.glob("*.generated.yaml")):
        artifacts.append(_load(f))
    package = {"campaign_id": cid, "exported_at": now_iso(), "offer": data.get("offer", {}), "channels": artifacts}
    out = edir / f"scheduler-package-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    out.write_text(json.dumps(package, indent=2))
    data["scheduling"]["export_paths"].append(str(out))
    data["updated_at"] = now_iso()
    _save(cfile, data)
    print(f"Exported package: {out}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="campaign", description="Campaign memory CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("create")
    p.add_argument("campaign_id")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_create)

    p = sub.add_parser("list")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("open")
    p.add_argument("campaign_id")
    p.set_defaults(func=cmd_open)

    p = sub.add_parser("get")
    p.add_argument("path")
    p.set_defaults(func=cmd_get)

    p = sub.add_parser("set")
    p.add_argument("path")
    p.add_argument("value")
    p.set_defaults(func=cmd_set)

    p = sub.add_parser("save")
    p.set_defaults(func=cmd_save)

    p = sub.add_parser("readiness-score")
    p.set_defaults(func=cmd_readiness)

    p = sub.add_parser("intake")
    p.set_defaults(func=cmd_intake)

    p = sub.add_parser("generate")
    p.add_argument("--channels", default="email,landing_page,social")
    p.set_defaults(func=cmd_generate)

    p = sub.add_parser("qa")
    p.set_defaults(func=cmd_qa)

    p = sub.add_parser("export")
    p.set_defaults(func=cmd_export)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (ValueError, KeyError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
