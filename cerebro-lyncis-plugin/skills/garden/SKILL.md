---
name: garden
description: Use when maintaining the Cérebro Lyncis Obsidian vault — daily cleanup, knowledge integration, synthesis generation, visual organization, and hot cache updates. Triggers on /cerebro-lyncis:garden, "limpar vault", "manutenção diária", "garden", "vault health".
---

# Vault Daily Garden

Daily maintenance pipeline for the Cérebro Lyncis vault. Cleans up orphans, fixes frontmatter, processes the aprendizados inbox, updates synthesis notes, builds visual navigation (MOC, canvases, Bases), and updates the hot cache for Claude Code queries.

> **v2 changes:** see `## Changelog` at the end. This version adds (a) persistent suggestions state with escalation, (b) canvas read-diff-merge, (c) sentinel comments on Painel Lyncis, (d) `--dry-run` mode, and (e) removes false-positive suggestion loops.

## Pre-Checks

Before starting, check idempotency and mode:

```
VAULT       = C:/Users/gabri/OneDrive/Desktop/Cérebro Obsidian/Cérebro Lyncis
TODAY       = YYYY-MM-DD (current date)
GARDEN_LOG  = Diario/YYYY/MM/YYYY-MM-DD-garden.md
STATE_FILE  = .garden/suggestions_state.json
DRY_RUN     = (flag --dry-run → write nothing, emit report only)
FORCE_PHASE = (flag --phase <name> → run only that phase)
```

1. Check if `GARDEN_LOG` exists via Glob.
2. If `DRY_RUN` is set → proceed anyway; suppress all writes, collect planned actions, emit a diff report at the end.
3. If `GARDEN_LOG` exists AND has `## Phase 7` section → **do NOT skip blindly**. Run the new Phase 0 (Suggestions Re-check). Only skip remaining phases if Phase 0 confirms zero pending suggestions AND no new inbox entries.
4. If `FORCE_PHASE` is set → run only that phase (after Phase 0).
5. Prefer `obsidian-vault` MCP tools. If MCP fails on first call, log a warning in the garden report (`> [!warning] Fallback to filesystem — Obsidian may have unsaved edits not reflected`) and fall back to Read/Glob/Grep for the rest of the run.

## Phase 0: SUGGESTIONS RE-CHECK (NEW in v2)

Persistent suggestions state breaks the "stale loop" where manual suggestions reappeared every run regardless of external resolution.

**State file:** `.garden/suggestions_state.json` (at vault root). Schema:

```json
{
  "suggestions": [
    {
      "id": "archive-exclude-from-graph",
      "first_seen": "2026-04-11",
      "last_seen": "2026-04-23",
      "run_count": 8,
      "category": "config",
      "check": {
        "type": "json_path_contains",
        "file": ".obsidian/app.json",
        "path": "userIgnoreFilters",
        "contains": "Base de Conhecimento/aprendizados/_archive/"
      },
      "resolved_at": null,
      "escalated": false
    }
  ]
}
```

Each suggestion MUST declare a machine-verifiable `check`. Supported check types:

| Type | Description |
|------|-------------|
| `file_exists` | pass if `file` exists |
| `file_not_exists` | pass if `file` does NOT exist (e.g., "docs/superpowers moved") |
| `json_path_contains` | read JSON, verify path contains substring |
| `frontmatter_field_value` | note's frontmatter field matches regex |
| `grep_absent` | pattern NOT found in any file under `path` |
| `manual_only` | no auto-check — requires human action; still track `run_count` |

**Algorithm:**

1. Load `STATE_FILE`. If missing, create empty.
2. For each suggestion with `resolved_at == null`:
   - Execute `check`. If passes → mark `resolved_at = TODAY`, log `Auto-resolved: <id>`.
3. For each still-open suggestion:
   - Increment `run_count`. Update `last_seen = TODAY`.
   - If `run_count >= 3` AND NOT `escalated` → set `escalated = true`, promote to "urgent" in the garden log and in the daily note annotation (Phase 7c).
4. If all suggestions are resolved AND no unprocessed inbox entries AND GARDEN_LOG exists for today → emit "Nothing to do, all suggestions resolved" and exit.

**Critical invariant:** no suggestion is emitted by later phases without also writing an entry to `STATE_FILE` with a `check`. If a phase wants to emit a suggestion that has no machine-verifiable check, mark `check.type = "manual_only"` — explicit acknowledgment that the loop will not self-resolve.

## Phase 1: AUDIT (read-only)

**Token budget: < 5K tokens of reads.** Achieved via frontmatter index.

Collect problems into a structured list. Do NOT modify anything.

### 1.0 Frontmatter Index (NEW in v2)

Instead of `head -10` on every file (which overruns budget on 500+ note vaults):

1. Check if `.garden/frontmatter-index.json` exists and has `last_built` ≤ today's oldest note mtime.
2. If stale: rebuild by reading ONLY the YAML block (`---` to `---`) of each `.md`.
3. Emit: `path → {tipo, status, data-atualizacao, membros, tags}`.

All subsequent 1a–1i checks query this index, not the filesystem directly.

### 1a. Orphan Detection
- `Glob("*.md", path=VAULT)` at root level only (depth 1)
- Any .md at root = misplaced. Exclude `Painel Lyncis.md` and `_hot-cache.md` (garden artifacts)

### 1b. Dead Wikilinks
- Build `filename → path` lookup from the index (O(1) lookups)
- Grep all `\[\[([^\]|#]+)` patterns → extract unique targets
- For each target, lookup case-insensitive: 0 matches = dead link

### 1c. Frontmatter Validation
Per tipo, validate required fields:

| tipo | Required | Should have |
|------|----------|-------------|
| recurso (sintese) | tipo, categoria, tags, cluster-id, membros | data-atualizacao |
| cliente | tipo, status, servico, valor-mensal, data-inicio | data-atualizacao |
| projeto-interno | tipo, status, tecnologias, data-criacao | data-atualizacao |
| diario | tipo, data, projetos-mencionados | — |

**v2 exceptions** (do NOT flag):
- Meta-aggregators like `_registro-padroes.md` — validate only `tipo` and `data-atualizacao`. They are not clusters.
- Any file whose filename starts with `_` (convention for index/context notes) — apply relaxed validation (tipo and data-atualizacao only).
- `_context.md` files — by design have no tipo (see Phase 2 existing rule).

### 1d. Stale Content
- Notes with `status: ativo` AND `data-atualizacao` older than 60 days from today
- Daily note stubs: files in Diario/ smaller than 200 bytes (template-only)

### 1e. Stats
- Count files per top-level folder
- Compare to last garden log's stats (if exists)
- **v2:** also append one JSON line to `.garden/metrics.jsonl` with date, counts, deltas for longitudinal analysis

### 1f. Stale Claims
- Notas com `confianca: confirmado` E `data-atualizacao` > 90 dias → marcar para revisão manual

### 1g. Missing Cross-References (REFINED in v2)
- Sínteses que mencionam `[[ferramenta-X]]` **em seção `## Entradas`** (contexto de uso) mas a nota `ferramenta-X.md` não tem backlink de volta
- **Exclude** mentions in `## Anti-Padrões`, `## Não use`, or `## Problemas conhecidos` — não injetar backlinks de contextos negativos
- Reportar: lista de pares (síntese → ferramenta sem backlink)
- Corrigidos na Phase 4b

### 1h. Empty Sections
- Pattern: `^## .+\n^## ` (regex multiline)
- Reportar para review manual

### 1i. Stale Index Entries
- `_context.md` files mencionando arquivos que não existem mais → auto-corrigir na Phase 3

### 1j. Overwrite-Protected Files (NEW in v2)
- Any file edited outside garden runs (mtime > last garden run mtime) that garden is about to touch in Phase 6 → flag for manual review, do NOT overwrite
- Applies to: `Painel Lyncis.md`, all `.canvas` files, all `.base` files

### 1k. Alias Collision Detection (NEW in v2 — REFINED after dry-run)
Filename Levenshtein alone is too narrow (`ferramenta-docx` vs `ferramenta-python-docx` has distance 7). Use multi-signal scoring:

For each pair of notes in the same folder, compute `alias_score`:
- +3 if one filename is a substring of the other (≥5 char overlap)
- +2 if Levenshtein distance ≤ 3
- +2 if outgoing wikilink overlap ≥ 70% of shorter note's outgoing count
- +3 if either note's content mentions the other as a redirect/alias (regex: `alias|redirect|mesma ferramenta|consolidar`)
- +1 if shared `## Sínteses Relacionadas` entries > 50%

Flag if `alias_score >= 5`.

Example that the refined heuristic catches: `ferramenta-docx` vs `ferramenta-python-docx` — substring match (+3) + redirect language in python-docx stub (+3) = 6 → flagged.

Classification: `suggest: manual consolidation` with check `file_not_exists` pointing to the redirect-role note.

**Output:** Store audit results as internal variables for Phase 2. Print summary:
`Audit: X orphans, Y dead links, Z frontmatter gaps, W stale notes, V stale claims, U missing xrefs, T empty sections, S stale index entries, R overwrite conflicts, Q alias collisions`

## Phase 2: TRIAGE

Classify each problem from Phase 1:

| Problem | Classification |
|---------|---------------|
| Empty root orphan that duplicates a note in Projetos/ | `auto-fix: delete` |
| Empty root orphan that is a concept | `auto-fix: move + stub` |
| Missing `data-atualizacao` in synthesis notes | `auto-fix: set to today` |
| Stale active notes (60+ days) | `suggest: add warning callout` (with check `frontmatter_field_value`) |
| Dead wikilinks to nonexistent notes | `suggest: create stub or fix link` (with check `file_exists`) |
| Merge candidates (near-duplicate filenames — 1k) | `suggest: manual consolidation` (check `manual_only`) |
| Template-only Diario stubs | `skip` |
| _context.md files lacking tipo | `skip: by design` |
| Stale claims (1f) | `suggest: manual review` (check `frontmatter_field_value` for data-atualizacao update) |
| Missing cross-references (1g) | `auto-fix: inject backlinks in Phase 4b` |
| Empty sections (1h) | `suggest: manual review` |
| Stale index entries (1i) | `auto-fix: remove from _context.md in Phase 3` |
| Overwrite conflicts (1j) | `skip + warn: user modified file between runs` |

**Critical v2 rule:** every `suggest:` item MUST register a check in `STATE_FILE` on first emission. No more ghost suggestions.

Print triage summary: `Triage: X auto-fix, Y suggestions (Z escalated from prior runs), W skipped`

## Phase 3: CLEANUP

Execute `auto-fix` items from Phase 2. For each action, log what was done.

If `DRY_RUN` → log the intended action to `planned_actions[]` but do not write.

### 3a. Delete Orphan Duplicates
(same as v1)

### 3b. Move Concept Stubs
(same as v1, plus: log `moved_from → moved_to` so user can audit later)

### 3c. Batch Frontmatter Fix
- Synthesis notes missing `data-atualizacao`: set to today
- **v2:** use `ruamel.yaml` with `preserve_quotes=True`, NOT string replacement. String replacement was corruption risk for multiline values, quoted keys, nested lists.

### 3d. Stale Warning Injection
(same as v1)

### 3e. Stale Index Entry Removal
(same as v1)

## Phase 4: INTEGRATE

### 4a. Process Inbox (REFINED in v2)

Inbox at `Base de Conhecimento/_inbox-aprendizados.md`. Each entry is `### [Title] ^[slug]` with `<!-- meta: ... -->`.

**v2 scoring** (replaces OR-chain first-match-wins):

For each inbox entry, compute score against every synthesis note:
```
score = (tag_overlap_count × 3)
      + (5 if slug_prefix matches cluster-id else 0)
      + (wikilink_overlap_count × 2)
```

- If `max_score >= 6` → assign to that synthesis
- If `max_score < 6` but shared-theme count ≥ 3 among unassigned → propose new synthesis (flag for Phase 5)
- If `max_score < 6` AND no theme → leave in inbox with comment `<!-- unclear-cluster: YYYY-MM-DD -->`; garden will NOT auto-route to `sintese-geral.md` anymore (junk drawer pattern)
- Ties (two or more syntheses with equal `max_score`): leave in inbox with `<!-- ambiguous-cluster: [id1, id2] -->`

After processing:
- Clear successfully routed entries from inbox
- Update `membros` count in each touched synthesis (via ruamel, not string replacement)
- Update `data-atualizacao` to today

**v2 addition — `sintese-geral.md` graduation check:** if `sintese-geral` exists and has N+ entries sharing a tag, emit suggestion `graduate-cluster-{tag}` with `manual_only` check.

### 4b. Inject Backlinks

Only for syntheses→ferramenta pairs identified in 1g (which already excludes anti-pattern contexts).

Section format:
```markdown
## Sínteses Relacionadas
<!-- garden:section:start id=sinteses-relacionadas -->
<!-- gerado por vault-daily-garden — não editar manualmente -->
- [[sintese-n8n-general]] — n8n Geral (53 entradas)
<!-- garden:section:end id=sinteses-relacionadas -->
```

Garden only replaces content between sentinels. Anything outside is preserved.

### 4c. Update `_context.md` Files
(same as v1, with ruamel for YAML-ish stats)

## Phase 5: UPDATE SYNTHESES (REFINED in v2)

For each synthesis that received new entries in Phase 4a:

**v2 deterministic regeneration rule** (replaces "genuinely new pattern" subjective check):

Regenerate `## Padrão Principal` and `## Regras de Ouro` ONLY IF:
- (a) ≥5 new entries accumulated since last regeneration (tracked in `last_regen` frontmatter field), OR
- (b) any new entry's content triggers a contradiction-score ≥ 7/10 against existing rules (LLM call with explicit rubric), OR
- (c) `--force-regen` flag is passed

Otherwise: only bump `membros` count in frontmatter and add new entries to `## Entradas` section.

Phase 5 writes `last_regen` field in frontmatter on regeneration.

If no new inbox entries processed → skip entirely.

## Phase 6: VISUALIZE (REWRITTEN in v2)

### 6a. Root MOC — `Painel Lyncis.md` (SENTINEL-BASED)

**v2 critical change:** garden only edits content between sentinel comments. Anything outside is user territory.

Structure:
```markdown
---
titulo: Painel Lyncis
tipo: moc
data-atualizacao: YYYY-MM-DD
gerado-por: vault-daily-garden
---

# Painel Lyncis

<!-- garden:section:start id=header -->
> [!tip] Última atualização do jardim: YYYY-MM-DD
<!-- garden:section:end id=header -->

<!-- garden:section:start id=projetos-ativos -->
## Projetos Ativos
[rows from frontmatter]
<!-- garden:section:end id=projetos-ativos -->

<!-- garden:section:start id=conhecimento-destilado -->
## Conhecimento Destilado
[wikilinks to top syntheses]
<!-- garden:section:end id=conhecimento-destilado -->

<!-- garden:section:start id=atividade-recente -->
## Atividade Recente
[last 7 daily notes]
<!-- garden:section:end id=atividade-recente -->

<!-- garden:section:start id=saude-vault -->
## Saúde do Vault
[Phase 2 suggestions, flagged with `run_count` escalation]
<!-- garden:section:end id=saude-vault -->

<!-- User-added sections here are PRESERVED across garden runs -->
```

**Algorithm:**
1. Read existing Painel.
2. For each sentinel pair, replace content inside with freshly computed block.
3. If a sentinel pair is missing → append at end (not beginning — preserve user content above).
4. Anything outside sentinels: untouched.
5. If `Painel Lyncis.md` mtime > garden last-run mtime AND no sentinels present → treat as user-authored, emit warning, do NOT overwrite.

### 6b. Ecosystem Canvas — `Canvas — Ecossistema Lyncis.canvas` (READ-DIFF-MERGE)

**v2 critical change:** NEVER rewrite canvas from scratch. Instead:

1. Read existing canvas JSON. Build `node_id → node` map.
2. Compute desired nodes from vault state (clients, projects, tools).
3. For each desired node:
   - If `node_id` exists in current canvas → preserve `x`, `y`, `width`, `height`, `color`, only update `file` or `text` if changed
   - If `node_id` missing → add new node at a default position (right of existing cluster, y-offset by counter)
4. For each current node NOT in desired set → keep it (user may have added manual nodes); don't auto-delete
5. Edges: same logic — preserve existing by `from+to+label`, add new, don't auto-delete

Result: garden maintains canvas structure without destroying manual layout adjustments.

### 6c. Knowledge Canvas — `Base de Conhecimento/Canvas — Mapa de Conhecimento.canvas`

Same read-diff-merge algorithm as 6b.

### 6d. Bases Views (NON-DESTRUCTIVE in v2)

**v2 critical change:** if `.base` file exists and has user-modified views (`mtime > last garden run mtime`), DO NOT rewrite. Instead:

1. Read existing `.base` as YAML.
2. Validate schema against expected structure (filters, formulas, properties, views).
3. If schema valid → leave file alone, log "preserved".
4. If schema broken → emit suggestion `base-schema-broken-{filename}` with `manual_only` check. Do not auto-fix base files.

Base files are user-tuned infrastructure; garden's job is to create them once, then step back.

## Phase 7: REPORT

### 7a. Garden Log

Write to `Diario/YYYY/MM/YYYY-MM-DD-garden.md`:

```markdown
---
tipo: garden-log
data: YYYY-MM-DD
gerado-por: vault-daily-garden
garden-version: 2.0
dry-run: false
---

# Garden Log — YYYY-MM-DD

## Resumo
- Auditadas: N notas
- Auto-resolvidas (Phase 0 re-check): K sugestões
- Problemas encontrados: X
- Corrigidos automaticamente: Y
- Sugestões para revisão manual: Z (W escalonadas, run_count >= 3)
- Overwrite conflicts skipped: V

## Ações Realizadas
### Phase 0 Re-check
- [x] Auto-resolvidas: [list with id and reason]

### Cleanup
- [x] [action descriptions]

### Integração
- [x] Inbox: N entradas routed, M unclear, P ambiguous
- [x] Sínteses tocadas: [list]
- [x] Backlinks injetados: N (excluindo M em contextos negativos)
- [x] _context.md atualizados: N

### Visualização
- [x] Painel Lyncis — N sentinels atualizados, M seções de usuário preservadas
- [x] Canvas Ecossistema — N nodes adicionados, M preservados, K edges novos
- [x] Hot cache regenerado

## Sugestões Ativas (STATE_FILE)
| ID | run_count | Escalonada | Check type |
|----|-----------|-----------|-----------|
| stub-ferramenta-docx | 1 | não | file_exists |

## Sugestões Resolvidas (desde último run)
- [auto] archive-exclude-from-graph — json_path_contains passou
```

### 7b. Hot Cache
(same as v1, plus: include `garden-version` in frontmatter for backward compat tracking)

### 7c. Daily Note Annotation
Append to today's daily note:
```markdown
- Garden: X fixes, Y insights, Z suggestions (W escalonadas) — [[YYYY-MM-DD-garden|ver log]]
```

If any suggestion is escalated (run_count >= 3), add an explicit warning:
```markdown
> [!warning] N sugestões do garden estão escalonadas (3+ runs sem resolução) — ver log
```

### 7d. Metrics Append (NEW in v2)

One JSONL line to `.garden/metrics.jsonl`:
```json
{"date":"2026-04-23","total_notes":760,"auto_fixed":9,"suggestions_open":3,"suggestions_escalated":0,"inbox_routed":2,"inbox_unclear":0,"syntheses_touched":1,"run_mode":"full","duration_s":47}
```

Enables 30/60/90-day trend charts without re-parsing garden logs.

## Dry-Run Mode (NEW in v2)

Invoke: `/cerebro-lyncis:garden --dry-run`

Behavior:
- Runs Phases 0–6 normally but collects `planned_actions[]` instead of executing writes.
- Phase 7 outputs a "dry-run report" to stdout AND writes a temporary file at `.garden/dry-run-YYYY-MM-DD-HHMMSS.md`.
- Temporary file includes full diff-style output per file touched (before/after snippets).
- Exits without modifying vault.

Recommended usage: run `--dry-run` before any `--force-regen` or first run after upgrading the skill.

## Common Mistakes (UPDATED for v2)

| Mistake | Fix |
|---------|-----|
| Running Phase 5 without Phase 4 | Use `--phase` for individual re-runs only after a full run has completed at least once. |
| Creating individual aprendizado files | Aprendizados go to the inbox buffer. `/cerebro-lyncis:distill` appends to `_inbox-aprendizados.md`. |
| Using string replacement for frontmatter | **Use `ruamel.yaml` with `preserve_quotes=True`.** String replacement corrupts multiline values and nested YAML. |
| Auto-changing `status` on stale notes | Only add warning callout. Status changes are user decisions. |
| Regenerating synthesis when no new entries | Phase 5 regeneration rule is deterministic (≥5 entries OR contradiction ≥7/10 OR --force-regen). |
| Writing canvas with literal `\\n` | Use `\n` for JSON newlines in text nodes. |
| Re-emitting resolved suggestions | **v2:** every suggestion has a machine-verifiable `check`; Phase 0 resolves automatically. |
| Overwriting user-edited Painel | **v2:** sentinel comments protect user sections. |
| Rewriting canvases from scratch | **v2:** read-diff-merge preserves manual layout. |

## When NOT to Use

- For one-off vault queries → `/cerebro-lyncis:query`
- For ingesting new sources → `/cerebro-lyncis:ingest`
- For writing new notes or bases ad-hoc → `/cerebro-lyncis:canvas` or `/cerebro-lyncis:bases`
- This skill is for **daily maintenance**, not ad-hoc exploration

## Changelog

### v2.0.1 (2026-04-23 — dry-run feedback)
- **1c frontmatter validation:** added exception for meta-aggregators (`_registro-padroes.md`) and `_`-prefix index notes. Dry-run caught false positive.
- **1k alias collision:** replaced single-signal Levenshtein with multi-signal scoring. Original heuristic missed the real-world `ferramenta-docx` vs `ferramenta-python-docx` case (Levenshtein = 7).

### v2.0 (2026-04-23)
**Critical fixes (based on field observation at 756-note vault):**
- **Phase 0 Suggestions Re-check** — state file `.garden/suggestions_state.json` with machine-verifiable checks per suggestion. Breaks the "stale loop" where the same manual suggestions reappeared every run (observed: `_archive/` exclusion was already in `app.json`, still suggested 8+ times).
- **Phase 6a Painel sentinels** — garden only edits between `<!-- garden:section:start -->` / `<!-- garden:section:end -->` comments. User-added sections preserved across runs.
- **Phase 6b/6c Canvas read-diff-merge** — never rewrite `.canvas` from scratch. Preserve manual node positions.
- **Phase 6d Bases non-destructive** — never rewrite user-tuned `.base` files; validate schema only.
- **`--dry-run` mode** — safe rehearsal of all phases without writes.
- **Phase 1g backlink context filtering** — do not inject backlinks from anti-pattern sections.
- **Phase 4a scoring** — replaces OR-chain first-match-wins with explicit scoring + threshold.
- **Phase 5 deterministic regeneration** — replaces subjective "genuinely new pattern" with 3 explicit triggers.
- **`ruamel.yaml` for all frontmatter edits** — replaces fragile string replacement.
- **`.garden/metrics.jsonl`** — machine-readable telemetry for trend analysis.
- **Phase 1j overwrite protection** — detect files modified outside garden runs and skip to avoid clobbering user work.
- **Phase 1k alias collision detection** — flag near-duplicate notes (Levenshtein + wikilink overlap).
- **Phase 1.0 frontmatter index** — `.garden/frontmatter-index.json` eliminates the "<5K token" budget violation on large vaults.

### v1.0 (baseline, pre-2026-04-23)
Original version.

## v3 Candidates (backlog — NOT implemented)

Documented 2026-04-23 during v2 bring-up. Do NOT implement without first validating v2 for ≥2 weeks in production. These are hypotheses, not requirements.

1. **Tail-verify after Write** — pattern for robustness against async filesystem syncs (observed in OneDrive): after any Write > 1KB, auto-run a Read on the last 10 lines to confirm persistence. Retry once before failing.
2. **`user_snoozed_until` in suggestion state** — escape hatch for `manual_only` suggestions that accumulate forever. User edits the field to silence a suggestion for N days. Phase 0 respects it.
3. **`sintese-geral` graduation algorithm** — when N+ entries in `sintese-geral.md` share a tag, propose splitting into a new cluster. Criterion: TF-IDF score > threshold, or explicit tag overlap ≥ 70% in ≥5 entries.
4. **Dead-note detector** → moved to separate skill `cerebro-lyncis:prune` (do NOT add to garden; violates "When NOT to Use"). Garden detects root orphans; prune detects structural orphans (zero backlinks, zero citations, 90+ days untouched).
5. **`_context.md` reverse-lint (Phase 1l)** — new phase checking files present in folder BUT not mentioned in `_context.md`. Complements existing 1i (stale index entries).
6. **Structured telemetry for dashboard** — emit `garden-status.json` with canonical counters (open_suggestions, escalated, vault_size_trend_30d) in a fixed schema. Enables Bases dashboard without parsing garden logs.
7. **Per-synthesis regen threshold** — replace hardcoded "≥5 new entries" with frontmatter field `regen-threshold: N` per synthesis. Different clusters have different saturation behavior.
8. **Self-test fixture vault** — minimal vault with known issues for CI-style validation of all 7 phases. Prevents regressions.
9. **Incremental migration mode** — `--since YYYY-MM-DD` flag on migration script for partial re-imports when garden logs are added/edited retroactively.

### Decision rule for promoting candidates to v3

A candidate should graduate only when ALL of:
- Real production failure observed that this candidate would prevent (not hypothetical)
- Alternative workarounds within v2 have been tried and failed
- Implementation cost fits in a single focused session (≤3h)

If a candidate is still a "maybe" after 1 month of v2 usage, drop it — it's speculative.
