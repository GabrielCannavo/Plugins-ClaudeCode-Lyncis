# Architecture — cerebro-lyncis plugin

## Propósito

Este plugin substitui o `claude-obsidian` (plugin genérico de wiki) com skills hardcoded
para o vault pessoal Cérebro Lyncis de Gabriel. Todas as referências de path, estrutura de
pastas, frontmatter schema e wikilinks são específicos para este vault — não é um plugin
genérico e não deve ser submetido ao marketplace Anthropic.

## Vault alvo

```
C:/Users/gabri/OneDrive/Desktop/Cérebro Obsidian/Cérebro Lyncis/
```

## Mapa de absorção — de onde cada skill veio

| Skill nova | Fonte primária | Fonte secundária (absorção) |
|-----------|----------------|-----------------------------|
| `query` | `~/.claude/skills/cerebro-lyncis/SKILL.md` | `claude-obsidian/wiki-query` — modos quick/standard/deep |
| `distill` | `~/.claude/skills/session-distill/SKILL.md` | `claude-obsidian/save` — flag `--quick` |
| `garden` | `~/.claude/skills/vault-daily-garden/SKILL.md` | `claude-obsidian/wiki-lint` — 4 checks extras na Phase 1 |
| `ingest` | `claude-obsidian/wiki-ingest` (portado) | `claude-obsidian/defuddle` (embutido como utility) |
| `canvas` | `claude-obsidian/canvas` (portado) | — |
| `research` | `claude-obsidian/autoresearch` (portado) | — |
| `md-reference` | `claude-obsidian/obsidian-markdown` (cópia literal) | — |
| `bases` | `claude-obsidian/obsidian-bases` (cópia literal) | — |

## O que foi descartado e por quê

| Descartado | Razão |
|-----------|-------|
| `claude-obsidian/wiki` (bootstrap) | Vault já existe e está estruturado. Bootstrap não é necessário. |
| Paths genéricos do claude-obsidian | Substituídos por paths hardcoded do vault Lyncis. |
| Estrutura `wiki/` do claude-obsidian | Vault Lyncis usa estrutura própria (Projetos/, Base de Conhecimento/, etc.) |

## Decisões de design

- **Sem delegação circular entre skills**: `research` não chama `ingest` de forma recursiva.
  Menciona a skill como opção mas não a invoca automaticamente.
- **Sem agents, hooks, .mcp.json ou settings.json**: plugin contém apenas skills.
- **defuddle como utility embutida em ingest**: não é uma skill separada invocável.
- **garden mantém canvases automáticos (6b/6c) e bases (6d)**: não delega para as skills
  `canvas` e `bases` — essas cuidam apenas de canvas/bases ad-hoc criados pelo usuário.
- **md-reference e bases são cópias literais**: apenas o frontmatter `name:` foi atualizado.
  Conteúdo técnico de sintaxe não muda com o vault.

## Skills originais (antes do plugin)

Deletadas após validação empírica:
- `~/.claude/skills/cerebro-lyncis/` → absorvida em `skills/query/`
- `~/.claude/skills/session-distill/` → absorvida em `skills/distill/`
- `~/.claude/skills/vault-daily-garden/` → absorvida em `skills/garden/`
