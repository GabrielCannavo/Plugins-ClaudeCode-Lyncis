---
name: distill
description: Arquiteto de conhecimento de sessão. Analisa a conversa, granulariza conhecimento em unidades atômicas interconectadas, gera briefing para próxima sessão, mantém warnings por ferramenta e propõe regras para CLAUDE.md. Use quando o usuário diz /cerebro-lyncis:distill ou proativamente ao final de sessões substanciais. Flag --quick para salvar rapidamente sem processamento completo.
---

# Distill — Arquiteto de Conhecimento

Não é um extrator mecânico. É um arquiteto que decompõe a sessão em unidades atômicas de conhecimento, tece conexões no vault, projeta continuidade para o futuro e alimenta o circuito de injeção para que sessões futuras comecem com contexto relevante.

**Circuito completo:** Sessão → Extração → Obsidian + Memory + Briefing + Warnings → Próxima Sessão

---

## Modo Rápido (--quick)

Quando o usuário invoca com `--quick` ou diz "save this conversation as a note" / "salva essa conversa":

1. Pular as Fases 1–8 abaixo.
2. Executar apenas uma versão simplificada da **Fase 6 — Escrita no Obsidian, item 7.4** (Base de Conhecimento Inbox):
   - Criar uma única nota no inbox com slug + meta + conteúdo resumido da conversa.
   - Frontmatter mínimo: `tipo: inbox`, `gerado-por: session-distill`, data de hoje.
3. Não gerar briefing, não checar warnings, não propor CLAUDE.md, não criar nota no diário.

**Critério para usar --quick**: conversa pontual sem decisões/bugs/padrões novos — usuário só quer arquivar o conteúdo discutido.

---

## 1. Quando Rodar

**Manual:** `/cerebro-lyncis:distill`

**Proativo:** Sugerir antes de encerrar sessões substanciais:
> Esta sessão teve conteúdo relevante. Quer que eu rode /cerebro-lyncis:distill antes de encerrar?

**Critérios de sessão substancial** (2+ dos seguintes):
- Bug fixado ou encontrado
- Decisão técnica com trade-offs
- Usuário corrigiu abordagem ou revelou preferência
- Padrão ou técnica nova descoberta
- 10+ trocas substantivas
- Arquivos criados/modificados significativamente
- Ideia ou melhoria mencionada para o futuro
- Tarefa deixada incompleta ou adiada

---

## 2. Fase 1 — Triagem

Se menos de 2 critérios: `"Esta sessão não tem conteúdo suficiente para destilar."` e parar.

**Idempotência:** Se já existe `🧠 Sessão destilada` na nota de hoje, perguntar: "Já existe uma destilação. Complementar ou substituir?"

---

## 3. Fase 2 — Extração Inteligente

Revisar a conversa completa. Qualidade > quantidade. Aplicar as lentes de inteligência (seção 3.9) durante a extração.

### 3.1 Decisões
- título, contexto, alternativas, decisão final, razão

### 3.2 Bugs Resolvidos
- título, sintoma, causa raiz, solução, como evitar

### 3.3 Erros Cometidos (do Claude)
- título, o que tentei, por que falhou, abordagem correta, lição

### 3.4 Padrões Descobertos
- título, padrão, quando usar, exemplo

### 3.5 Preferências do Usuário
- título, preferência, contexto revelado

### 3.6 Conhecimento Técnico
- título, fato, fonte/contexto, aplicação

### 3.7 Ideias & Melhorias Futuras
- título, ideia, projeto relacionado, impacto (baixo/médio/alto), próximo passo concreto

### 3.8 Trabalho Pendente
- título, estado (incompleta/bloqueada/adiada), o que falta, bloqueador, prioridade

### 3.9 Lentes de Inteligência na Extração

Aplicar estas lentes a TODOS os itens extraídos acima:

**A. Anti-padrões recorrentes:** Se um bug ou erro é similar a algo que já apareceu em sessões anteriores (verificar memory e warnings.json), marcar como `recorrente: true` e propor regra para CLAUDE.md. Frase indicadora: "de novo", "outro bug de...", "sempre esqueço de...".

**B. Reversões de decisão:** Se uma decisão desta sessão contradiz uma anterior (verificar memories tipo `project`), registrar explicitamente: "Decisão X (sessão anterior) revertida para Y. Razão: [...]". Reversões são alto-valor para aprendizado.

**C. Lacunas de conhecimento:** Quando o usuário corrigiu o Claude ("não é assim", "errado", "na verdade..."), o item corrigido é uma lacuna. Marcar com `lacuna: true`. Lacunas são candidatas a regras de CLAUDE.md — o Claude não deveria errar isso de novo.

**D. Marcadores emocionais:** Detectar frustração ("pqp", "de novo", "não acredito"), alívio ("finalmente!", "era isso!"), surpresa ("não sabia!", "interesting"). Itens com carga emocional recebem peso maior na priorização. Não registrar a emoção em si — registrar o fato que a causou com mais detalhe.

**E. Complexidade por profundidade:** Se um problema consumiu >10 trocas, merece documentação detalhada (nota completa em aprendizados). Se foi resolvido em 2 trocas, basta uma linha no diário.

**F. Confiança do conhecimento:** Classificar cada fato técnico:
- `✅ confirmado` — testado e funcionando (em produção ou teste real)
- `⚠️ provável` — funciona localmente mas sem confirmação em produção
- `❓ hipótese` — acreditamos que é assim mas não verificamos

**G. Validade temporal:** Fatos vinculados a versão (`n8n 2.13.3`, `Claude 4.5`) devem ter tag `versão: X`. No futuro, se a versão mudar, esses fatos precisam ser re-verificados.

**H. Frequência de ferramentas:** Anotar quais ferramentas/nodes/APIs apareceram na sessão. Se uma ferramenta causa problemas em 3+ sessões (verificar warnings.json), propor nota dedicada de "armadilhas conhecidas".

---

## 4. Fase 3 — Granularização

Decompor cada item em **unidades atômicas** — cada uma independente, linkável, reutilizável.

**Princípio: um fato, uma nota.**

Para cada item, perguntar:
1. Tem componentes independentes? Um bug = (a) fato sobre API + (b) padrão de prevenção + (c) regra de config
2. É genérico ou projeto-específico? Pode ter versão genérica (Base Conhecimento) + instanciação local (memory)
3. Conecta a algo no vault? Complementa, contradiz ou estende nota existente?

Classificar cada unidade: `aprendizado | fato-tecnico | padrão | regra-projeto | ideia | warning`

---

## 5. Fase 4 — Roteamento

| Tipo de unidade | Diário | Memory | Base Conhecimento | Nota Projeto | Dia Seguinte | Warnings | CLAUDE.md |
|---|---|---|---|---|---|---|---|
| Decisão | Sempre | Se futuro | Não | Sempre | Não | Não | Não |
| Bug resolvido | Sempre | Se recorrente | Se genérico | Se do projeto | Não | Sempre | Se recorrente |
| Erro do Claude | Sempre | Sempre | Não | Não | Não | Sempre | Se lacuna |
| Padrão | Sempre | Se local | Sempre | Não | Não | Não | Se universal |
| Preferência | Resumo | Sempre | Não | Não | Não | Não | Não |
| Fato técnico | Sempre | Se tool/API | Sempre | Não | Não | Se gotcha | Se crítico |
| Ideia | Resumo | Não | Não | Sempre | Se acionável | Não | Não |
| Pendência | Resumo | Não | Não | Se relevante | Sempre | Não | Não |

**Nota de Projeto:** Ideias e decisões appendadas à nota do projeto em `Projetos/internos/proj-xxx.md` ou `Projetos/clientes/cliente-xxx.md`.

---

## 6. Fase 5 — Deduplicação

### Memory
1. `ls ~/.claude/projects/` → encontrar pasta do CWD atual
2. Ler `memory/MEMORY.md`
3. Se similar existe → atualizar, não duplicar

### Base de Conhecimento
1. Grep em `{VAULT}/Base de Conhecimento/_inbox-aprendizados.md` pelo slug
2. Grep em `{VAULT}/Base de Conhecimento/sinteses/` pelo título ou frase-chave
3. Se similar existe numa síntese → skip ou anotar "complementa [[sintese-xxx]]"
4. Se similar existe no inbox → atualizar entrada existente, não duplicar

### Warnings
1. Ler `{memory_dir}/warnings.json`
2. Se warning para mesma ferramenta/padrão existe → incrementar `count`, atualizar `last_seen`

---

## 7. Fase 6 — Escrita no Obsidian

**VAULT:** `C:/Users/gabri/OneDrive/Desktop/Cérebro Obsidian/Cérebro Lyncis`

### 7.1 Preencher Cabeçalho do Diário

Path: `{VAULT}/Diario/YYYY/MM/YYYY-MM-DD.md`

Usar Edit/patch para inserir DENTRO de cada seção. Se já tem conteúdo, appendar.

| Seção | Conteúdo |
|---|---|
| `## Foco do Dia` | 1-2 linhas do que a sessão abordou, com wikilinks |
| `## Tarefas` | `- [x]` concluídas, `- [ ]` pendentes (com wikilinks) |
| `## Decisões Tomadas` | 1 linha/decisão com wikilinks |
| `## Projetos Tocados Hoje` | Wikilinks: `[[proj-xxx]]`, `[[cliente-xxx]]` |
| `## Aprendizados` | 1 linha/aprendizado, link para nota detalhada |
| `## Amanhã` | Pendências + `Carregado para [[YYYY-MM-DD+1]]` |

**Frontmatter:** atualizar `projetos-mencionados` e `tags`.

### 7.2 Appendar Bloco Destilado

Formato (omitir categorias vazias):

```markdown

---
### 🧠 Sessão destilada — HH:MM

**Projeto(s):** [[proj-name]]

#### Decisões
- **[titulo]** — [decisão]. _Contexto:_ [breve]

#### Bugs Resolvidos
- **[titulo]** — Causa: [raiz]. Fix: [solução]. Confiança: [✅/⚠️/❓]

#### Erros & Lições
- **[titulo]** — [tentativa] falhou: [razão]. Lição: [lição]

#### Padrões Descobertos
- **[titulo]** — [padrão]

#### Conhecimento Técnico
- **[titulo]** — [fato]. Confiança: [✅/⚠️/❓]

#### Preferências
- [preferência]

#### 💡 Ideias
- **[titulo]** — [ideia]. Projeto: [[proj-xxx]]. Impacto: [alto/médio/baixo]

#### ⏳ Pendências
- **[titulo]** — [estado]. Falta: [o que]

```

### 7.3 Propagar para Notas de Projeto

Para cada projeto tocado, appendar em `Projetos/*/proj-xxx.md`:

```markdown

---
## [YYYY-MM-DD] — Insights da sessão
- [Decisão/ideia relevante]
- 💡 [Ideia capturada]
_Fonte: [[YYYY-MM-DD]]_
```

### 7.4 Base de Conhecimento — Inbox

Path: `{VAULT}/Base de Conhecimento/_inbox-aprendizados.md`

**Append** (nunca sobrescrever) um bloco por unidade atômica. Se o arquivo não existir, criar com header:

```markdown
---
tipo: inbox
gerado-por: session-distill
---
# Inbox de Aprendizados
```

Formato de cada entrada:

```markdown

---
### [Título] ^[slug]
<!-- meta: data=YYYY-MM-DD | origem=[[YYYY-MM-DD]] | confianca=confirmado|provável|hipótese | versao=se-aplicavel | tags=tag1,tag2 -->

[Conteúdo — 2-4 frases]

**Quando usar:** [contexto de aplicação]

**Conexões:** [[ferramenta-xxx]], [[proj-xxx]]
```

Naming do slug: kebab-case do título, max 60 chars. Exemplo: `^n8n-splitinbatches-output-invertido`

**NÃO criar arquivos individuais `aprendizado-*.md`.** Todo conhecimento vai para o inbox e será integrado nas sínteses pelo `/cerebro-lyncis:garden`.

### 7.5 Auto-Memory

Formato:
```markdown
---
name: [Título]
description: [Uma linha]
type: feedback | project | reference
---
[Conteúdo]
**Why:** [Importância]
**How to apply:** [Quando/como]
```
Naming: `{type}_{slug}.md`. Atualizar `MEMORY.md`.

---

## 8. Fase 7 — Continuidade Cross-Dia

### Criar/atualizar nota do dia seguinte quando:
- Tarefas com estado `incompleta` ou `adiada`
- Usuário mencionou "amanhã", "depois", "próxima sessão"
- Ideias acionáveis que precisam de follow-up

### Conteúdo no dia seguinte

Path: `{VAULT}/Diario/YYYY/MM/YYYY-MM-DD+1.md` (calcular com `python3 -c "from datetime import *; print((date.today()+timedelta(1)).isoformat())"`)

Criar nota com template padrão se não existir. Preencher:
```markdown
## Foco do Dia
Continuação de [[YYYY-MM-DD]]:
- [ ] [Pendência 1]
- [ ] [Pendência 2]
```

**Backlinks bidirecionais:** dia atual → `Carregado para [[YYYY-MM-DD+1]]` | dia seguinte → `Continuação de [[YYYY-MM-DD]]`

---

## 9. Fase 8 — Gerar Artefatos de Injeção *(circuito de feedback)*

**Esta fase é o que fecha o loop.** Os artefatos gerados aqui são lidos pelos hooks no início da próxima sessão.

### 9.1 Briefing para próxima sessão

**Path:** `{memory_dir}/briefing.md` (mesma pasta do MEMORY.md do projeto atual)

O briefing é um resumo compacto (~30 linhas) que o hook SessionStart injeta no início da conversa seguinte.

**Formato:**
```markdown
# Briefing — [Projeto] — [Data]

## Última sessão
[2-3 linhas: o que foi feito, resultado principal]

## Pendências ativas
- [ ] [Tarefa 1] — prioridade: [alta/média/baixa]
- [ ] [Tarefa 2]

## Decisões ativas
- [Decisão que afeta trabalho futuro]

## ⚠️ Warnings
- [Ferramenta/padrão]: [o que evitar e por quê]

## Contexto relevante
- Projeto: [[proj-xxx]] — [estado atual em 1 linha]
- Último workflow tocado: [nome/ID]
```

**Regra:** O briefing DEVE caber em ~1500 tokens. Se for maior, comprimir.

### 9.2 Warnings acumulativos

**Path:** `{memory_dir}/warnings.json`

```json
{
  "warnings": [
    {
      "tool": "Switch V3",
      "pattern": "Criar via API sem caseSensitive",
      "consequence": "Crash em runtime",
      "fix": "Sempre incluir caseSensitive: false em cada operator",
      "count": 3,
      "first_seen": "2026-04-05",
      "last_seen": "2026-04-11",
      "promoted_to_claude_md": false
    }
  ]
}
```

**Lógica:**
- Se warning já existe para a mesma ferramenta+padrão: incrementar `count`, atualizar `last_seen`
- Se `count >= 3` e `promoted_to_claude_md == false`: marcar para promoção (ver 9.3)

### 9.3 Propostas para CLAUDE.md

**Path:** `{memory_dir}/claude-md-proposals.md`

**Critérios para propor:**
- Warning com `count >= 3` (problema recorrente)
- Lacuna de conhecimento (Claude errou e foi corrigido)
- Padrão que se aplica a todos os projetos do CWD
- Preferência confirmada em 2+ sessões

**Ação:** Ao final da distilação, se há propostas pendentes, informar:
> Há N proposta(s) para CLAUDE.md. Quer revisar e aprovar?

Se aprovado, aplicar via Edit no CLAUDE.md do projeto.

---

## 10. Wikilinks e Conexões

**OBRIGATÓRIO em todo output.** Primeira menção vira link, subsequentes sem.

**Projetos:** `[[cliente-aly-adv]]`, `[[cliente-boccato]]`, `[[cliente-power-nutrifit]]`, `[[cliente-rambo-nutrifit]]`, `[[proj-atendente-ia-aly-adv]]`, `[[proj-atendente-ia-condominios]]`, `[[proj-autocutter]]`, `[[proj-lyncis-creative-plugin]]`, `[[proj-assistente-qualificacao]]`

**Ferramentas (com alias):** `[[ferramenta-n8n|n8n]]`, `[[ferramenta-chatwoot|Chatwoot]]`, `[[ferramenta-supabase|Supabase]]`, `[[ferramenta-uazapi|Uazapi]]`, `[[ferramenta-evolution-api|Evolution API]]`, `[[ferramenta-meta-ads|Meta Ads]]`

**Criar links mesmo para páginas inexistentes:** `[[Google Sheets]]`, `[[Redis]]`, `[[Claude API]]`, `[[Gemini]]`, `[[SplitInBatches]]`, `[[executeWorkflow]]`, `[[Switch]]`, `[[AI Agent node]]`, `[[Code node]]`, `[[defineBelow]]`, `[[autoMapInputData]]`, `[[toolWorkflow]]`

---

## 11. Notas Importantes

- **Contexto compactado:** Se houve compactação, mencionar: "Nota: contexto compactado — extração cobre apenas o visível."
- **Análise interna:** A skill roda DENTRO da sessão — analisa a própria conversa.
- **Descoberta do projeto memory:** `ls ~/.claude/projects/` → pasta cujo nome corresponde ao CWD.
- **Dia seguinte:** `python3 -c "from datetime import *; print((date.today()+timedelta(1)).isoformat())"`.
- **Budget:** Briefing ≤ 1500 tokens. Priorizar por impacto + recência.
- **Warnings.json:** Se o arquivo não existir, criar com `{"warnings": []}`.
- **Propostas CLAUDE.md:** Sempre pedir confirmação antes de editar o CLAUDE.md.
