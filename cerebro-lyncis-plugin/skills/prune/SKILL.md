---
name: prune
description: Use when looking for structurally-dead notes in the Cérebro Lyncis vault — notes with zero backlinks, zero citations in syntheses, and 90+ days without edit. REPORT-ONLY; never moves or deletes without explicit user approval. Triggers on /cerebro-lyncis:prune, "notas esquecidas", "limpeza estrutural", "vault pruning", "o que posso arquivar".
---

# Prune — Dead Note Detector

Identifies notes that are structurally orphaned (no backlinks, no citations in syntheses, long-untouched) and proposes them as archive candidates. This is **not** garden's job — garden is daily maintenance, prune is occasional deep cleanup.

## When to Use

- Vault feels cluttered and hard to navigate
- You're about to create a synthesis and want to know what raw notes are orphaned
- Before a major reorganization
- When `cerebro-lyncis:garden` has run clean for weeks but vault keeps growing

## When NOT to Use

- For daily maintenance → use `cerebro-lyncis:garden`
- To find notes with dead wikilinks → garden Phase 1b
- To clean up the inbox → use `cerebro-lyncis:distill` or manual inbox processing
- For root-level orphans → garden Phase 1a

## Hard Invariants

These cannot be violated regardless of flags or phases:

1. **Never modify `_archive/` or `Arquivo/`.** Both are already-archive folders — prune's output destination is `Arquivo/_pruned/`, never modify what's already in Arquivo.
2. **Never scan `.garden/` or `.obsidian/`.** Garden artifacts and Obsidian config are not pruneable content.
3. **Never move/delete without explicit user `y` confirmation per file.** Batch moves require batch confirmation.
4. **Never touch files with `tipo: cliente`, `tipo: projeto-interno` with `status: ativo`, any file in `Modelos/`, or any file with `categoria: sintese`.** Syntheses are consolidated knowledge — even unreferenced, they're library-of-record.
5. **Never touch daily notes** (`Diario/`). Historical state, even empty ones.
6. **Never touch `sintese-geral.md`** — it's garden's junk drawer by design (Phase 4a fallback route). Pruning it breaks garden.
7. **Report-only is the default mode.** Moves happen only if user types `prune --move` and confirms each candidate.

## Scoring Heuristic

For each candidate file, compute `prune_score`:

| Signal | Weight |
|--------|--------|
| `data-atualizacao` or mtime > 90 days ago | +2 |
| Zero inbound wikilinks (grep `[[filename]]` and `[[filename\|` across vault, excluding `_archive/`) | +3 |
| Not listed in any `## Membros` or `## Sínteses Relacionadas` section | +1 |
| Not referenced in `Painel Lyncis.md` or `_hot-cache.md` | +1 |
| File size < 500 bytes (stub-like, no consolidated content) | +1 |
| `tipo: aprendizado` in frontmatter | -1 (aprendizados are expected to migrate to _archive via distill) |
| `categoria: prompt` in frontmatter | -2 (reference material — keep unless user explicitly wants pruning of prompts) |
| `tipo: cliente` or `projeto-interno` with `status: ativo` | auto-skip |
| `categoria: sintese` | auto-skip (consolidated knowledge) |
| `sintese-geral.md` (by filename) | auto-skip (garden junk drawer) |
| In `Modelos/`, `Diario/`, `_archive/`, `Arquivo/`, `.garden/`, `.obsidian/` | auto-skip |
| Filename starts with `_` (context/cache/index) | auto-skip |

**Classification:**
- `score >= 5` → **strong candidate** (archive suggested)
- `score 3-4` → **weak candidate** (review suggested)
- `score < 3` → skip (probably still alive)

## Phases

### Phase 1: GATHER
Scan all `.md` files in the vault, excluding:
- `_archive/` (already archived)
- `Modelos/` (templates)
- `Diario/` (historical)
- Files starting with `_` (index / context / cache artifacts — `_context.md`, `_hot-cache.md`, `_registro-padroes.md`, `_inbox-*`)
- `Painel Lyncis.md` (top-level MOC)

For each: read frontmatter, compute file size, read mtime.

### Phase 2: BACKLINK COUNT

Build a single in-memory index of all wikilinks across the vault:
```python
# one pass over every .md
for each .md file:
    for each wikilink match [[target|?alias?]]:
        increment_count(target)
```

O(N) — not O(N²). Avoid re-grepping per candidate.

### Phase 3: SCORE

Apply scoring table. Auto-skip files that match the skip criteria.

### Phase 4: GROUP + REPORT

Output a markdown report:

```markdown
# Prune Report — YYYY-MM-DD

## Summary
- Scanned: X non-archived notes
- Strong candidates (score ≥ 5): A
- Weak candidates (score 3-4): B
- Skipped (protected): C

## Strong Candidates — archive suggested

### Score 7
- [[filename]] — size 200B, mtime 150d ago, zero backlinks, zero citations
  - Preview: (first 200 chars of content)
  - Suggested destination: `Arquivo/[folder]/<filename>`

### Score 6
- ...

## Weak Candidates — manual review

### Score 4
- [[filename]] — 1 backlink but stale 120 days
  - Preview: ...

## Protected / Skipped

- N files in Modelos/, K files with tipo: cliente (active), ...
```

Output format: always write to `.garden/prune-report-YYYY-MM-DD-HHMMSS.md` AND emit a summary in the chat response.

### Phase 5: ACTION (opt-in only)

Only if user explicitly runs `/cerebro-lyncis:prune --move`:

1. Read the latest prune-report.
2. For each strong candidate, prompt interactively: `Archive [[filename]]? (y/n/skip)`
3. On `y`: move to `Arquivo/_pruned/YYYY-MM-DD/<original-path-preserved>/`
4. Log each move to `.garden/prune-actions.jsonl` with `{from, to, timestamp, user_approved: true}`
5. Never auto-approve. Never batch-approve more than 10 at once (force pauses every 10 for user to sanity-check).

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Running without dry-run first | Default mode IS report-only. Explicit flag required for moves. |
| Scoring `aprendizado` files same as others | Aprendizados have `-1` weight because they're expected to migrate to `_archive` via distill. |
| Counting `[[filename]]` only | Also count `[[filename\|alias]]` and `[[path/filename]]` forms. |
| Forgetting to skip active clients | Hard invariant #3 — check `status: ativo` before scoring. |
| Deleting instead of moving | NEVER delete. Always move to `Arquivo/_pruned/<date>/`. User can undo by moving back. |

## Escape Hatch — Exclusion List

Notes you never want prune to consider can be marked via frontmatter:

```yaml
---
prune-exclude: true
prune-exclude-reason: "reference material kept for future project"
---
```

Phase 1 GATHER skips any note with `prune-exclude: true`.

## Relationship to Garden

Garden and prune are complementary:

| Detects | Garden | Prune |
|---------|:------:|:-----:|
| Root-level orphan files | ✓ | — |
| Dead wikilinks | ✓ | — |
| Stale active notes | ✓ | — |
| Structurally-orphaned notes | — | ✓ |
| Long-untouched notes with no citations | — | ✓ |
| Stubs that never got content | — | ✓ |

Never duplicate logic. If both phases want to detect the same thing, one must win (prefer garden for daily ops).

## First Run — Expectations (calibrated 2026-04-23 on 760-note vault)

Dry-run on the Cérebro Lyncis vault at v2 baseline:
- ~717 files auto-skipped (mostly `_archive/`)
- ~47 actively scored
- 0 strong candidates
- 1 weak candidate (`framework-meta-ads.md` — 0 backlinks, likely forgotten)

This suggests: **well-maintained vaults produce few candidates.** If first-run produces 30+ strong candidates, something is wrong (either the vault actually needs major cleanup, OR scoring is too aggressive). Check against the Protected lists before acting.

Note: garden-created stubs would only score high if they remain unreferenced for 90+ days. Today's stubs (docx/elementtree/settings) reference each other via `## Referências` and sínteses, so they don't trip prune.

## Edge Cases

- **Note recently renamed:** old path has no backlinks (they all point to new path). Score will be high. Detect via: if file has been renamed (git history or mtime vs ctime delta is zero), skip for 30 days.
- **Note that is the TARGET of many wikilinks but has NO CONTENT:** high inbound, small size. Don't prune — the link graph says it's a hub even if empty. Leave alone.
- **Note with only self-references:** `ferramenta-X.md` mentioning `[[ferramenta-X]]` in its own body. Count excluded from backlink total.

## Safety Test

Before running prune for the first time, test on a fresh backup of the vault. If `--move` is used on the wrong file, `Arquivo/_pruned/` preserves it — but `_pruned/` is still within the vault. A git commit or full OS backup before first `--move` run is recommended.
