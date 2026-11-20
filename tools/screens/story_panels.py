"""Render recorded answers verbatim and retain provenance for each demo story."""
from pathlib import Path
import hashlib
import json
import re

SCREENS = Path("reports/final/screens")
RUNS = SCREENS / "runs"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def annotations(numbers):
    return [str(n["number"]) for n in numbers if not n.get("matches_packet_evidence_value")]


def main():
    snapshot = read(RUNS / "tomato-a-d.json")
    manifest = RUNS / "RUN_MANIFEST.json"
    run_info = {item["file"]: item for item in read(manifest)["responses"]} if manifest.exists() else {}
    stories = [{
        "id": "tomato-a-d",
        "question": snapshot["rows"][0]["question"],
        "plain_model": "\n\n".join(f"{r['title']}\n{r['plain_model']}" for r in snapshot["rows"]),
        "culinarystate": "\n\n".join(f"{r['title']}\n{r['culinarystate']}" for r in snapshot["rows"]),
        "why": "The evidence compiler uses the recorded pot state to restrict transfer. A receives a table report. B–D retain UNKNOWN.",
        "limit": "Ingredient pH crosswalk is AI-drafted. Mixture pH remains unknown.",
        "model": snapshot["rows"][0]["model"],
        "date": snapshot["snapshot_timestamp_utc"][:10],
        "source_run": str(RUNS / "tomato-a-d.json"),
        "status": "SIGNED_SNAPSHOT",
        "unsourced_values": [
            f"{r['title'].split(':', 1)[0]} · {value}"
            for r in snapshot["rows"] for value in annotations(r["plain_claimed_numbers"])
        ],
    }]
    for key, question, why, limit in [
        ("carrots", "My carrots came out too soft and mushy. What should I change next time?",
         "The trace supplies cut, lid, time and simulated heat fields. State citations are checked against the trace.",
         "The cooking advice remains unverified."),
        ("tomatoes", "How much vitamin C remains in the tomatoes after this recipe?",
         "The claim packet restricts numerical output to applicable source reports. The wording and number check can trigger a template fallback.",
         "The saved answers illustrate one case. Gold labels for judging response quality are unavailable."),
        ("safety", "Is the chicken safe to eat?",
         "The system arm refuses before drafting. The plain comparison is separate.", "The refusal gives no safety determination."),
    ]:
        file = RUNS / (key + ".json")
        row = dict(id=key, question=question, plain_model="Pending live capture.", culinarystate="Pending live capture.",
                   model=None, date=None, source_run=None, status="PENDING_LIVE_CAPTURE",
                   why=why, limit=limit, unsourced_values=[])
        metadata = run_info.get(file.name)
        if metadata and hashlib.sha256(file.read_bytes()).hexdigest() == metadata["sha256"]:
            response = read(file)
            system = response["system"]
            plain = response.get("plain") or {}
            if response["question"] != question and key == "safety":
                raise ValueError("The saved safety question does not match the story.")
            row.update(
                question=response["question"],
                plain_model=plain.get("text") or plain.get("reason") or "No plain answer returned.",
                culinarystate=system["final"],
                model=response.get("model"),
                date=metadata["timestamp_utc"][:10],
                source_run=str(file),
                status="RECORDED_LIVE" if plain.get("status") == "OK" else "RECORDED_LIVE_WITHOUT_PLAIN",
                plain_status=plain.get("status"),
                unsourced_values=annotations(plain.get("claimed_numbers", [])),
            )
            if key == "carrots":
                verify = next(stage for stage in response["pipeline"] if stage["id"] == "verify")
                row["verify_detail"] = verify["detail"]
                if system.get("status") == "STATE_AWARE_ADVICE" and not system.get("citations"):
                    row["why"] = ("The system had access to cut, lid, time and simulated heat. "
                                  "The parser recognized zero structured citations in this answer.")
            if key == "tomatoes":
                row["evidence_ids"] = [item["id"] for item in response["evidence"]]
                row["why"] = ("The claim packet allowed the cited table value under DIRECT and retained the measurement-method caveat."
                              if system.get("route") == "DIRECT" else why)
            if key == "safety" and plain.get("status") == "NOT_SENT_TEXT_NOT_SELF_WRITTEN":
                row["why"] += " This capture used the preview with hosted sending disabled."
                row["model"] = f'{response["model"]} (configured only; no call)'
        stories.append(row)
    for row in stories:
        if row["source_run"]:
            row["source_sha256"] = hashlib.sha256(Path(row["source_run"]).read_bytes()).hexdigest()
    (SCREENS / "answer_panels.json").write_text(json.dumps({"stories": stories}, indent=2, ensure_ascii=False) + "\n")
    blocks = ["# Demo stories", "", "The saved response files carry the recorded answers and verifier status.", ""]
    for row in stories:
        blocks += [f"## {row['id']}", "", f"**Question.** {row['question']}", "",
                   "**Plain model**", "", row["plain_model"], "", "**CulinaryState**", "", row["culinarystate"], "",
                   f"**Why.** {row['why']} {row['limit']}", ""]
        if row["unsourced_values"]:
            blocks += ["Verifier annotation: " + ", ".join(f"{x} [no source]" for x in row["unsourced_values"]), ""]
        blocks += [f"Source: `{row['source_run']}` · {row['model']} · {row['date']}." if row["source_run"] else "Live run pending.", ""]
    out = "\n".join(blocks)
    if re.search(r"/Users/|nvapi-|BBCGF|SRC-000002", out):
        raise ValueError("Restricted content in story panel.")
    (SCREENS / "STORIES.md").write_text(out + "\n")


if __name__ == "__main__":
    main()
