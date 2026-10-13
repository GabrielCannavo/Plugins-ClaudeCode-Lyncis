# improve v1.6.0 — Esforço e Postura Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Adicionar ao improve o slot 11 (Esforço + armadilhas), o slot 12 (Postura) e a regra de correção de rumo.

**Architecture:** Mudança só de texto no prompt da skill (`lyncis-kit/commands/improve.md`). Sem código. A validação é uma eval qualitativa: subagentes rodam o prompt antigo e o novo sobre 5 rascunhos fixos e comparam com critérios objetivos.

**Tech Stack:** Markdown (comando de plugin do Claude Code), git, `claude plugin`.

**Spec:** `docs/superpowers/specs/2026-10-09-improve-esforco-design.md`

## Global Constraints

- Continuam **cinco** seções de resposta; armadilhas vão **dentro** do prompt refinado.
- Nome "armadilhas", nunca "anti-padrões", para os riscos da tarefa.
- Slot 1 (Papel/persona) não muda de texto. Postura é slot 12; Esforço é slot 11.
- Esforço baixo: no máximo uma linha; normalmente nada.
- Postura sempre como comportamento verificável, nunca adjetivo.
- Na correção de rumo, o "pare X" cita algo visível na conversa; sem histórico, pergunta no discovery.
- Versões: improve v1.6.0; `lyncis-kit` 1.0.1 → 1.1.0.
- Não mexer em §1.7, verificação inicial nem na guarda contra injection.

## Review Focus

- E-mail curto sem risco → prompt não pode crescer (Esforço e Postura `n/a`, agrupáveis numa linha).
- Discovery disparando só por causa dos slots novos → Esforço/Postura inferíveis não podem virar pergunta.
- Armadilha genérica ("verifique bem") → reprovar.
- Correção de rumo sem histórico na conversa → deve perguntar, não inventar o X.
- Rascunho que mistura tarefa nova e correção → tratar como correção só se referir à entrega atual.

---

### Task 1: Editar `lyncis-kit/commands/improve.md`

**Files:**
- Modify: `lyncis-kit/commands/improve.md` (tabela §1 linhas 27-38; §1.5 linha 56; §2 linhas 101-105; §3 linhas 107-112; §4 linha 116; §6 linhas 122-130; formato linhas 138-146)

- [ ] **Step 1:** Adicionar à tabela do §1 as linhas 11 e 12 e, abaixo da tabela, a escala de esforço (4 fatores × baixo/médio/alto) e a regra de status (`✓` explícito / `✗ → <nível>` inferido / `n/a` geração simples).
- [ ] **Step 2:** §1.5 — acrescentar à ordem de prioridade que Esforço e Postura só viram pergunta quando não são inferíveis e mudam o prompt; em correção de rumo sem histórico, perguntar o que o executor está fazendo de errado.
- [ ] **Step 3:** §2 — regra de armadilhas por nível e subseção "Correção de rumo" (sinais, 4 passos, limite).
- [ ] **Step 4:** §3 — princípio "Postura = comportamento verificável" com exemplos ✗/✓.
- [ ] **Step 5:** §4 — uma linha: armadilhas da tarefa não entram aqui.
- [ ] **Step 6:** §6 — segundo exemplo (esforço alto, webhook) e contraexemplo baixo.
- [ ] **Step 7:** Formato — mencionar 12 slots e agrupamento n/a.
- [ ] **Step 8:** `git diff --stat` e conferir que §1.7, verificação inicial e regra absoluta ficaram intactos (`git diff` não mostra essas linhas).
- [ ] **Step 9:** Commit `improve v1.6.0: slots Esforço e Postura, correção de rumo`.

### Task 2: Eval antes/depois

**Files:**
- Create: `docs/superpowers/evals/2026-10-13-improve-esforco.md` (resultado)

Rascunhos fixos (o subagente pula o discovery e assume respostas razoáveis, porque é eval):
1. "escreve um e-mail de follow-up pro cliente que recebeu a proposta há 5 dias, cordial, máx 120 palavras, CTA agendar call"
2. "renomeia a variável x para totalPedidos no calc.js"
3. "o webhook do Chatwoot tá duplicando mensagem em produção, corrige"
4. "cria 3 ganchos de carrossel pra uma advogada previdenciária, estilo Light Copy, linguagem do dia a dia do aposentado"
5. Correção de rumo, com histórico simulado: o executor entregou 3 ganchos abstratos ("Mais tranquilidade na aposentadoria", "Seu direito garantido", "Menos burocracia") e o rascunho é "tá muito genérico isso, quero algo que pareça a vida real do cliente"
5b. O mesmo rascunho do caso 5, sem histórico.

- [ ] **Step 1:** Rodar o prompt **antigo** (`git show HEAD~1:lyncis-kit/commands/improve.md`) nos casos 1, 3 e 5 (linha de base).
- [ ] **Step 2:** Rodar o prompt **novo** nos casos 1-5b.
- [ ] **Step 3:** Conferir os critérios: (1) Esforço e Postura `n/a`, sem armadilhas, prompt ±10% do baseline; (2) `baixo`, ≤1 linha; (3) `alto`, 1-3 armadilhas específicas + Postura comportamental; (4) postura de estilo como comportamento; (5) Papel `n/a`, "Pare X / Passe a Y" com X citando os ganchos reais; (5b) não inventa X, pergunta.
- [ ] **Step 4:** Se algum critério falhar, ajustar o texto da Task 1 e repetir só o caso que falhou.
- [ ] **Step 5:** Registrar o resultado no arquivo de eval e commitar.

### Task 3: Release

**Files:**
- Modify: `lyncis-kit/.claude-plugin/plugin.json` (version), `README.md` (histórico), `lyncis-kit/README.md` (se descrever slots)

- [ ] **Step 1:** `version` → `1.1.0`; acrescentar v1.6.0 ao histórico do README raiz.
- [ ] **Step 2:** Commit, `git push origin main`, `claude plugin marketplace update gabriel-local`.
- [ ] **Step 3:** Se `lyncis-kit@gabriel-local` estiver instalado localmente, `claude plugin update lyncis-kit@gabriel-local`; senão, avisar que a versão do claude.ai precisa ser sincronizada pelo Gabriel.
