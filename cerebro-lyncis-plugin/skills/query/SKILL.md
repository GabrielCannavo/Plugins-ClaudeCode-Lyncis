---
name: query
description: Use when working in the Cérebro Lyncis Obsidian vault, answering questions about clients, projects, resources, or daily notes. Supports quick, standard, and deep modes for token-efficient vault queries. Triggers on any Lyncis-related question, "query quick:", "query deep:", or session start mentioning Lyncis work.
---

# Cérebro Lyncis — Vault Query

The vault at `C:/Users/gabri/OneDrive/Desktop/Cérebro Obsidian/Cérebro Lyncis/` is a second brain for Gabriel (owner of Lyncis, which sells paid traffic and AI assistants). Use it for context before working on anything Lyncis-related.

---

## Modos de Query

Escolha a profundidade com base na complexidade da pergunta.

| Modo | Trigger | Leituras | Custo tokens | Melhor para |
|------|---------|----------|--------------|-------------|
| **Quick** | `query quick: ...` ou pergunta factual simples | só `_hot-cache.md` | ~1.500 | "Qual o status de X?", datas, fatos rápidos |
| **Standard** | padrão (sem flag) | hot cache + `_context.md` relevante + 3-5 páginas | ~3.000 | A maioria das perguntas |
| **Deep** | `query deep: ...` ou "completo", "abrangente", "síntese cruzada" | varredura ampla do vault | ~8.000+ | Comparações, sínteses entre áreas, análise de lacunas |

---

## Modo Quick

Use quando a resposta provavelmente está no hot cache.

1. Ler `_hot-cache.md`. Se responde a pergunta, responder imediatamente.
2. Se não encontrou, dizer: "Não está no quick cache. Rodar como consulta standard?"

Não abrir páginas individuais no modo quick.

---

## Query Protocol (Modo Standard)

**Sempre ler `_hot-cache.md` PRIMEIRO** — snapshot token-otimizado com vault stats, projetos quentes, pendências e tabela de navegação rápida. Atualizado diariamente pelo `/cerebro-lyncis:garden`.

Se hot cache não existe ou está desatualizado, usar `_context.md` como fallback.

```
Tipo de pergunta          → Ler primeiro
─────────────────────────────────────────────────
QUALQUER pergunta         → _hot-cache.md (sempre, 1 leitura)
Status/info de cliente    → Projetos/_context.md → clientes/
Projeto ativo             → Projetos/_context.md → internos/
Ferramenta / framework / prompt → Base de Conhecimento/_context.md → subfolder
Padrão / best practice    → Base de Conhecimento/sinteses/_registro-padroes.md
Trabalho recente / decisões → Diario/_context.md → nota mais recente
Visão geral de área       → Responsabilidades/_context.md → subfolder
```

Seguir wikilinks até profundidade 2 para entidades-chave. Não mais fundo.

---

## Modo Deep

Use para sínteses, comparações ou "me conta tudo sobre X".

1. Ler `_hot-cache.md` e `_context.md` de todas as áreas relevantes.
2. Identificar todas as seções relevantes (projetos, sínteses, ferramentas, diário recente).
3. Ler cada página relevante. Não pular.
4. Se cobertura do vault for rasa, oferecer suplementar com web search.
5. Sintetizar resposta abrangente com citações via wikilinks.
6. Considerar salvar resposta de volta ao vault (propor ao usuário).

---

## MCP vs File Tools

| Situação | Usar |
|---|---|
| Obsidian aberto (uso normal) | `obsidian-vault` MCP tools |
| Obsidian fechado | Read / Glob / Grep |
| Criando ou editando nota | `obsidian-vault` MCP (escreve via app ativo) |
| Busca por frontmatter em bulk | `mcp__obsidian-vault__obsidian_complex_search` |
| Leitura rápida de path conhecido | `mcp__obsidian-vault__obsidian_get_file_contents` |

Sempre preferir MCP quando Obsidian está aberto — reflete estado atual incluindo edições não salvas. Se MCP falhar na primeira chamada, usar Read/Glob para o resto da execução.

---

## Session Start

Quando o usuário inicia sessão mencionando trabalho relacionado a Lyncis, carregar proativamente:
1. `Diario/_context.md` + nota diária mais recente
2. `_context.md` da pasta mais relevante ao trabalho mencionado

NÃO carregar todos os `_context.md` de uma vez — apenas o relevante para a tarefa.

---

## Write-Back Protocol

Atualizar o vault quando:
- Status de cliente muda (editar campo `status` no frontmatter)
- Decisão tomada na sessão (appendar em nota de hoje sob `## Decisões Tomadas`)
- Nova ferramenta, prompt ou aprendizado emerge (criar nota em `Base de Conhecimento/`)
- Trabalho em projeto avança (atualizar `## Status Atual` e `## Próximos Passos`)

Sempre atualizar `data-atualizacao` no frontmatter para hoje ao editar qualquer nota.

NÃO fazer write-back para conversa geral ou exploração — apenas mudanças substantivas.

---

## Frontmatter Quick Reference

```yaml
# Filtrar clientes por:   tipo: cliente    status: ativo | pausado | concluido
# Filtrar projetos por:   tipo: projeto-interno    status: em-desenvolvimento | ideia
# Filtrar recursos por:   tipo: recurso    categoria: ferramenta | prompt | aprendizado | framework
# Notas diárias:          tipo: diario     data: YYYY-MM-DD
```

---

## Naming Conventions

- Arquivos: sem acentos, sem espaços, apenas hifens — `cliente-academia-exemplo.md`
- Notas diárias: `Diario/YYYY/MM/YYYY-MM-DD.md`
- Clientes: `cliente-[nome].md` | Internos: `proj-[nome].md` | Recursos: `[categoria]-[nome].md`

---

## Erros Comuns

| Erro | Fix |
|---|---|
| Ler todos os arquivos de uma pasta para achar um cliente | Ler `_context.md` primeiro, depois targetar o arquivo específico |
| Usar Read/Glob quando Obsidian está aberto | Usar `obsidian-vault` MCP — reflete estado ao vivo |
| Escrever notas sem frontmatter | Toda nota precisa de frontmatter — usar template de `Modelos/` |
| Tags fora do vocabulário controlado | Tags vêm dos `_context.md` files |
| Abrir páginas individuais no modo quick | Modo quick = só hot cache |
