#!/usr/bin/env python3
"""
garden-migrate-v1-to-v2.py

One-shot migration from cerebro-lyncis:garden v1 → v2.

What it does:
1. Scans all `Diario/YYYY/MM/YYYY-MM-DD-garden.md` files (v1 logs).
2. Extracts suggestions from the "Sugestões para Revisão Manual" sections.
3. Builds `.garden/suggestions_state.json` with:
   - `first_seen` = earliest garden log that mentioned the suggestion
   - `last_seen`  = latest garden log that mentioned it
   - `run_count`  = number of garden logs that mentioned it
   - `check`      = best-effort machine-verifiable check (see heuristics below)
   - `resolved_at`= auto-detected if the check passes TODAY
4. Bootstraps `.garden/frontmatter-index.json` by reading YAML frontmatter of every .md in the vault.
5. Bootstraps `.garden/metrics.jsonl` with one line per historical garden log (counts parsed from log text where possible).
6. Does NOT modify any existing note.

Usage:
    python3 garden-migrate-v1-to-v2.py \\
        --vault "C:/Users/gabri/OneDrive/Desktop/Cérebro Obsidian/Cérebro Lyncis" \\
        [--dry-run] [--verbose]

Assumptions / limitations:
- Suggestion classification from free-form Portuguese text is best-effort.
  Items that cannot be matched to a check pattern get `check.type = "manual_only"`.
- Garden logs before a certain date may have different structure — the parser tolerates
  missing sections but warns in --verbose.
- Metrics parsing relies on text patterns in the "## Resumo" section; older logs may
  produce partial rows (nulls filled).

Safe to re-run: overwrites `.garden/suggestions_state.json` only after backing up the
previous version to `.garden/suggestions_state.json.bak-YYYYMMDDHHMMSS`.
"""
from __future__ import annotations
import argparse
import json
import os
import re
import shutil
import sys
from dataclasses import dataclass, asdict, field
from datetime import datetime, date
from pathlib import Path
from typing import Any

# ---------- Heuristics: suggestion text → machine-verifiable check ----------

CHECK_HEURISTICS: list[tuple[re.Pattern, dict[str, Any]]] = [
    # "Mover X/ para Y" → file_not_exists on X
    (
        re.compile(r"[Mm]over\s+[`]?([^\s`]+)[`]?\s+para", re.IGNORECASE),
        {"type": "file_not_exists", "file": "{0}"},
    ),
    # "Deletar/remover pasta X"
    (
        re.compile(r"(?:[Dd]eletar|[Rr]emover)\s+(?:pasta\s+)?[`]?([^\s`,.]+)[`]?", re.IGNORECASE),
        {"type": "file_not_exists", "file": "{0}"},
    ),
    # "Criar stub X" / "Considerar criar stubs: `nome`, `nome2`"
    (
        re.compile(r"[Cc]riar\s+stubs?\s*(?:para)?:?\s*[`]?([a-z][a-z0-9-]+)[`]?", re.IGNORECASE),
        {"type": "file_exists", "file": "Base de Conhecimento/ferramentas/{0}.md"},
    ),
    # "Excluir X do grafo" → json_path_contains on .obsidian/app.json (Obsidian-specific)
    (
        re.compile(r"[Ee]xcluir\s+[`]?([^\s`]+)[`]?\s+do\s+grafo", re.IGNORECASE),
        {
            "type": "json_path_contains",
            "file": ".obsidian/app.json",
            "path": "userIgnoreFilters",
            "contains": "{0}",
        },
    ),
]


def guess_check(text: str) -> dict[str, Any]:
    """Given a suggestion text line, return the best-guess check dict."""
    for pat, template in CHECK_HEURISTICS:
        m = pat.search(text)
        if m:
            resolved = {}
            for k, v in template.items():
                if isinstance(v, str) and "{0}" in v:
                    resolved[k] = v.format(m.group(1))
                else:
                    resolved[k] = v
            return resolved
    return {"type": "manual_only", "note": "auto-migrated from v1; no machine check inferable"}


# ---------- Slug ID generation ----------

def make_id(text: str, existing: set[str]) -> str:
    """Generate a short stable slug for a suggestion."""
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60].strip("-")
    if not slug:
        slug = "suggestion"
    base = slug
    i = 1
    while slug in existing:
        slug = f"{base}-{i}"
        i += 1
    return slug


# ---------- Garden log parsing ----------

GARDEN_LOG_RE = re.compile(r"(\d{4}-\d{2}-\d{2})-garden\.md$")
SUGGESTIONS_SECTION_RE = re.compile(
    r"## Sugest(?:õ|o)es.*?(?=\n## |\Z)", re.DOTALL | re.IGNORECASE
)
TODO_LINE_RE = re.compile(r"^\s*(?:[-*]\s+|\[\s*\]\s+|>\s+(?:[-*]\s+)?)(.+)$", re.MULTILINE)

RESUMO_AUDITADAS = re.compile(r"[Aa]uditadas:\s*(\d+)")
RESUMO_FIXED = re.compile(r"[Cc]orrigidos\s*automaticamente:\s*(\d+)")
RESUMO_SUGGESTIONS = re.compile(r"[Ss]ugest(?:õ|o)es.*?:\s*(\d+)")


@dataclass
class SuggestionRecord:
    id: str
    label: str
    first_seen: str
    last_seen: str
    run_count: int = 0
    category: str = "manual_action"
    check: dict[str, Any] = field(default_factory=dict)
    resolved_at: str | None = None
    resolved_reason: str | None = None
    escalated: bool = False


def parse_log(path: Path) -> tuple[date, list[str], dict[str, Any]]:
    """Return (log_date, suggestion_texts, metrics)."""
    m = GARDEN_LOG_RE.search(path.name)
    if not m:
        return None, [], {}
    log_date = datetime.strptime(m.group(1), "%Y-%m-%d").date()
    text = path.read_text(encoding="utf-8", errors="ignore")

    # Suggestions section
    sec_match = SUGGESTIONS_SECTION_RE.search(text)
    sug_texts: list[str] = []
    if sec_match:
        body = sec_match.group(0)
        for tm in TODO_LINE_RE.finditer(body):
            line = tm.group(1).strip()
            # Filter out section headers that leaked through
            if line.startswith("#") or len(line) < 8:
                continue
            sug_texts.append(line)

    # Metrics (best-effort)
    metrics: dict[str, Any] = {"date": log_date.isoformat()}
    for key, rex in (("total_notes", RESUMO_AUDITADAS),
                     ("auto_fixed", RESUMO_FIXED),
                     ("suggestions_open", RESUMO_SUGGESTIONS)):
        mm = rex.search(text)
        metrics[key] = int(mm.group(1)) if mm else None
    metrics["source"] = path.name
    metrics["garden_version"] = "1.0"
    return log_date, sug_texts, metrics


# ---------- Frontmatter index ----------

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
YAML_SIMPLE_LINE = re.compile(r"^([a-zA-Z_][a-zA-Z0-9_-]*):\s*(.*)$")


def parse_frontmatter(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")[:4000]
    except Exception:
        return {}
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    out: dict[str, Any] = {}
    for line in m.group(1).splitlines():
        mm = YAML_SIMPLE_LINE.match(line)
        if mm:
            out[mm.group(1)] = mm.group(2).strip().strip('"').strip("'")
    return out


def build_frontmatter_index(vault: Path, exclude: list[str]) -> dict[str, Any]:
    idx: dict[str, Any] = {}
    for md in vault.rglob("*.md"):
        rel_parts = md.relative_to(vault).parts
        if any(ex in rel_parts for ex in exclude):
            continue
        rel = str(md.relative_to(vault)).replace(os.sep, "/")
        fm = parse_frontmatter(md)
        try:
            fm["_mtime"] = md.stat().st_mtime
            fm["_size"] = md.stat().st_size
        except Exception:
            pass
        idx[rel] = fm
    return idx


# ---------- Main migration ----------

def run_check(vault: Path, check: dict[str, Any]) -> bool | None:
    ctype = check.get("type")
    try:
        if ctype == "file_exists":
            return (vault / check["file"]).exists()
        if ctype == "file_not_exists":
            return not (vault / check["file"]).exists()
        if ctype == "json_path_contains":
            fp = vault / check["file"]
            if not fp.exists():
                return False
            data = json.loads(fp.read_text(encoding="utf-8"))
            keys = check["path"].split(".")
            cur: Any = data
            for k in keys:
                if isinstance(cur, dict) and k in cur:
                    cur = cur[k]
                else:
                    return False
            if isinstance(cur, list):
                return any(check["contains"] in str(v) for v in cur)
            return check["contains"] in str(cur)
        if ctype == "grep_absent":
            fp = vault / check["path"]
            if not fp.exists():
                return True
            return not re.search(check["pattern"], fp.read_text(encoding="utf-8", errors="ignore"))
        if ctype == "frontmatter_field_value":
            fm = parse_frontmatter(vault / check["file"])
            val = fm.get(check["field"], "")
            return bool(re.search(check["regex"], str(val)))
        if ctype == "manual_only":
            return None
    except Exception:
        return None
    return None


def migrate(vault: Path, dry_run: bool = False, verbose: bool = False) -> int:
    garden_dir = vault / ".garden"
    state_file = garden_dir / "suggestions_state.json"
    metrics_file = garden_dir / "metrics.jsonl"
    index_file = garden_dir / "frontmatter-index.json"

    diario = vault / "Diario"
    if not diario.exists():
        print(f"[ERROR] {diario} not found", file=sys.stderr)
        return 1

    # 1. Find all v1 garden logs
    logs = sorted(diario.rglob("*-garden.md"))
    if verbose:
        print(f"[info] Found {len(logs)} garden logs")

    # 2. Aggregate suggestions across logs
    # Key = normalized label (lowercase alphanumeric) to dedupe across runs
    aggregated: dict[str, dict[str, Any]] = {}
    all_metrics: list[dict[str, Any]] = []

    for log in logs:
        log_date, texts, metrics = parse_log(log)
        if log_date is None:
            continue
        all_metrics.append(metrics)
        if verbose:
            print(f"[info] {log.name}: {len(texts)} suggestion lines")
        for t in texts:
            norm = re.sub(r"[^a-z0-9]+", "", t.lower())[:80]
            if not norm:
                continue
            rec = aggregated.setdefault(
                norm,
                {
                    "label_first": t,
                    "first_seen": log_date.isoformat(),
                    "last_seen": log_date.isoformat(),
                    "run_count": 0,
                },
            )
            rec["run_count"] += 1
            if log_date.isoformat() < rec["first_seen"]:
                rec["first_seen"] = log_date.isoformat()
            if log_date.isoformat() > rec["last_seen"]:
                rec["last_seen"] = log_date.isoformat()

    # 3. Build state file
    existing_ids: set[str] = set()
    suggestions: list[SuggestionRecord] = []
    today = date.today().isoformat()
    for norm, rec in sorted(aggregated.items(), key=lambda kv: kv[1]["first_seen"]):
        label = rec["label_first"]
        sug_id = make_id(label, existing_ids)
        existing_ids.add(sug_id)
        check = guess_check(label)
        # Auto-resolve if check passes now
        check_result = run_check(vault, check)
        resolved_at = today if check_result is True else None
        resolved_reason = "Auto-verified during migration — check passed." if resolved_at else None
        escalated = rec["run_count"] >= 3 and not resolved_at
        suggestions.append(
            SuggestionRecord(
                id=sug_id,
                label=label,
                first_seen=rec["first_seen"],
                last_seen=rec["last_seen"],
                run_count=rec["run_count"],
                category=(
                    "cleanup"    if "mover" in label.lower() or "deletar" in label.lower() or "remover" in label.lower()
                    else "stub"  if "stub" in label.lower() or "criar" in label.lower()
                    else "config" if "grafo" in label.lower() or "excluir" in label.lower()
                    else "manual_action"
                ),
                check=check,
                resolved_at=resolved_at,
                resolved_reason=resolved_reason,
                escalated=escalated,
            )
        )

    state = {
        "schema_version": "2.0",
        "last_run": today,
        "last_migration": datetime.now().isoformat(timespec="seconds"),
        "migration_note": (
            f"Auto-migrated from {len(logs)} v1 garden logs. "
            f"Suggestions with machine-verifiable checks were auto-resolved if they pass today. "
            f"Others are marked manual_only."
        ),
        "suggestions": [asdict(s) for s in suggestions],
    }

    if not dry_run:
        garden_dir.mkdir(exist_ok=True)
        if state_file.exists():
            bak = state_file.with_suffix(
                f".json.bak-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            )
            shutil.copy2(state_file, bak)
            if verbose:
                print(f"[info] Backup → {bak.name}")
        state_file.write_text(
            json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    # 4. Bootstrap frontmatter index
    exclude = ["_archive", ".git", ".obsidian", ".garden"]
    idx = build_frontmatter_index(vault, exclude)
    if not dry_run:
        index_file.write_text(
            json.dumps(idx, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    # 5. Append metrics
    if not dry_run and all_metrics:
        with metrics_file.open("a", encoding="utf-8") as f:
            for row in all_metrics:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

    # Summary
    total = len(suggestions)
    resolved = sum(1 for s in suggestions if s.resolved_at)
    escalated = sum(1 for s in suggestions if s.escalated)
    manual = sum(1 for s in suggestions if s.check.get("type") == "manual_only")
    print("=" * 60)
    print(f"Migration {'(dry-run)' if dry_run else 'COMPLETE'}")
    print(f"Logs scanned              : {len(logs)}")
    print(f"Unique suggestions found  : {total}")
    print(f"Auto-resolved today       : {resolved}")
    print(f"Escalated (run_count>=3)  : {escalated}")
    print(f"Manual-only (no check)    : {manual}")
    print(f"Frontmatter index size    : {len(idx)} notes")
    print(f"Metrics rows appended     : {len(all_metrics)}")
    if dry_run:
        print()
        print("Dry-run — no files written. Re-run without --dry-run to apply.")
    else:
        print()
        print(f"State:   {state_file.relative_to(vault)}")
        print(f"Index:   {index_file.relative_to(vault)}")
        print(f"Metrics: {metrics_file.relative_to(vault)}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Migrate cerebro-lyncis garden v1 → v2.")
    ap.add_argument("--vault", required=True, help="Absolute path to vault root")
    ap.add_argument("--dry-run", action="store_true", help="Print plan, write nothing")
    ap.add_argument("--verbose", action="store_true", help="Per-log logging")
    args = ap.parse_args()
    vault = Path(args.vault).resolve()
    if not vault.exists():
        print(f"[ERROR] vault path does not exist: {vault}", file=sys.stderr)
        return 2
    return migrate(vault, dry_run=args.dry_run, verbose=args.verbose)


if __name__ == "__main__":
    sys.exit(main())
