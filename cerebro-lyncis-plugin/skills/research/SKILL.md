---
name: research
description: Loop autônomo de pesquisa iterativa sobre um tópico. Faz buscas na web, busca fontes, sintetiza achados e salva tudo no vault Cérebro Lyncis como páginas estruturadas. Baseado no padrão autoresearch de Karpathy. Triggers on: research, pesquisar, deep dive, investigar, encontrar tudo sobre, pesquisa autônoma, build a wiki on.
---

# Research — Loop Autônomo de Pesquisa

Você é um agente de pesquisa. Pega um tópico, roda buscas iterativas na web, sintetiza achados, e arquiva tudo no vault. O usuário recebe páginas no vault, não respostas no chat.

Baseado no padrão autoresearch de Karpathy: um programa configurável define seus objetivos. Você roda o loop até atingir a profundidade ou o orçamento de iterações.

**VAULT:** `C:/Users/gabri/OneDrive/Desktop/Cérebro Obsidian/Cérebro Lyncis`

**PASTA BASE (HARDCODED):** `{VAULT}/Base de Conhecimento/pesquisas-autonomas/`

---

## Estrutura de Cada Pesquisa

Para cada pesquisa, criar pasta `{VAULT}/Base de Conhecimento/pesquisas-autonomas/[topico-slug]/`:

```
pesquisas-autonomas/[topico-slug]/
├── program.md          — objetivo, constraints, budget de iterações, domínios preferidos
├── log.md              — histórico das iterações
├── fontes/             — páginas de fontes ingeridas
├── conceitos/          — páginas de conceitos extraídos
├── entidades/          — páginas de pessoas, ferramentas, organizações
└── sintese.md          — resumo final + perguntas abertas
```

---

## program.md — Configuração da Pesquisa

Criar antes de iniciar o loop:

```markdown
---
tipo: research-program
topico: [slug]
data-criacao: YYYY-MM-DD
---

# Programa de Pesquisa — [Tópico]

## Objetivo
[O que queremos descobrir? Qual é a pergunta central?]

## Constraints
- Budget de iterações: [padrão: 5]
- Domínios fonte preferidos: [ex: artigos técnicos, documentação oficial, estudos de caso]
- Domínios a evitar: [ex: conteúdo de baixa qualidade, sites de spam]
- Escopo de relevância: [ex: apenas aplicações práticas para tráfego pago/IA]

## Critério de Convergência
Parar quando: nenhuma entidade ou conceito genuinamente novo nas últimas 2 iterações, OU budget atingido.

## Perguntas Iniciais
- [Pergunta 1 — ângulo de busca]
- [Pergunta 2 — ângulo complementar]
- [Pergunta 3 — ângulo de casos de uso]
```

---

## Loop de Pesquisa

### Iteração 1 — Busca Ampla

1. Decompor o tópico em 3-5 ângulos de busca distintos
2. Para cada ângulo: rodar 2-3 queries (via Perplexity skill se disponível, fallback: WebSearch)
3. Para os top 2-3 resultados por ângulo: WebFetch da página
4. Se defuddle disponível: limpar o conteúdo antes de processar (ver `/cerebro-lyncis:ingest` para instruções de instalação)
5. Extrair de cada fonte: afirmações-chave, entidades, conceitos, perguntas abertas

### Iteração 2 — Preencher Lacunas

5. Identificar o que está faltando ou contraditório da Iteração 1
6. Rodar buscas targetadas para cada lacuna (máx 5 queries)
7. Buscar top resultados para cada lacuna

### Iteração 3+ — Verificação de Síntese (opcional)

8. Se contradições maiores ou lacunas importantes ainda existem: mais uma passagem targetada
9. Caso contrário: prosseguir para arquivamento

**Parada automática quando:**
- Budget de iterações atingido (padrão: 5)
- Convergência: nenhuma entidade/conceito novo nas últimas 2 iterações
- Usuário para manualmente

---

## Arquivamento dos Resultados

### Fontes (`fontes/`)

Uma página por referência principal encontrada:

```markdown
---
tipo: recurso
categoria: fonte-externa
subtipo: artigo
titulo: "[Título da Fonte]"
source_url: [url]
author: [autor se disponível]
date_published: [data se disponível]
data-criacao: YYYY-MM-DD
data-atualizacao: YYYY-MM-DD
tags: [pesquisa, topico-slug]
confidence: high | medium | low
---

# [Título]

## Principais Afirmações
- [Afirmação 1]
- [Afirmação 2]

## O que contribui para a pesquisa
[1-2 frases: qual é o valor único desta fonte para o tópico]

## Conexões
[[conceito-extraido]], [[entidade-mencionada]]
```

### Conceitos (`conceitos/`)

Uma página por conceito significativo extraído:

```markdown
---
tipo: recurso
categoria: conceito
titulo: "[Nome do Conceito]"
data-criacao: YYYY-MM-DD
data-atualizacao: YYYY-MM-DD
tags: [conceito, topico-slug]
---

# [Nome do Conceito]

[Definição em 2-3 frases]

## Relevância para Lyncis
[Como isso se aplica ao contexto de tráfego pago / assistentes IA]

## Fontes
[[fonte-slug-1]], [[fonte-slug-2]]
```

Verificar vault antes de criar — se já existe nota de conceito similar, atualizar a existente em vez de criar duplicata.

### Entidades (`entidades/`)

Uma página por pessoa, ferramenta ou organização identificada:

```markdown
---
tipo: recurso
categoria: entidade
titulo: "[Nome]"
data-criacao: YYYY-MM-DD
data-atualizacao: YYYY-MM-DD
tags: [entidade, topico-slug]
---

# [Nome]

**Tipo:** pessoa | ferramenta | organização

[Descrição em 2-3 frases: quem/o que é e por que é relevante para este tópico]

## Fontes
[[fonte-slug]]
```

Verificar vault antes de criar — se já existe `ferramenta-[nome].md` ou similar, appendar informação em vez de criar duplicata.

### Síntese (`sintese.md`)

Página mestre onde tudo converge:

```markdown
---
tipo: recurso
categoria: sintese
titulo: "Research: [Tópico]"
data-criacao: YYYY-MM-DD
data-atualizacao: YYYY-MM-DD
gerado-por: cerebro-lyncis:research
tags: [pesquisa, topico-slug]
iteracoes: N
fontes-total: N
---

# Research: [Tópico]

## Visão Geral
[2-3 frases resumindo o que foi encontrado]

## Achados Principais
- [Achado 1] (Fonte: [[fonte-slug]])
- [Achado 2] (Fonte: [[fonte-slug]])

## Entidades Relevantes
- [[nome-entidade]]: papel/significância

## Conceitos-Chave
- [[nome-conceito]]: definição em uma linha

## Contradições
- [[fonte-a]] diz X. [[fonte-b]] diz Y. [Nota sobre qual é mais confiável e por quê]

## Perguntas Abertas
- [Pergunta que a pesquisa não respondeu completamente]
- [Lacuna que precisaria de mais fontes]

## Fontes
- [[fonte-slug-1]]: autor, data
- [[fonte-slug-2]]: autor, data
```

---

## log.md — Histórico de Iterações

Appendar ao final de cada iteração:

```markdown
## Iteração N — YYYY-MM-DD HH:MM

### Queries rodadas
- "[query 1]" → [N resultados, top: título]
- "[query 2]" → [N resultados, top: título]

### Fontes processadas
- [[fonte-slug-1]] — [1 linha: o que contribuiu]
- [[fonte-slug-2]] — [1 linha: o que contribuiu]

### Novidades desta iteração
- Entidades novas: [lista]
- Conceitos novos: [lista]
- Contradições encontradas: [lista ou "nenhuma"]

### Lacunas identificadas
- [O que ainda não foi respondido]
```

---

## Após Finalizar

1. Atualizar `Base de Conhecimento/_context.md` — adicionar entrada para a nova pasta de pesquisa
2. Atualizar `_hot-cache.md` na raiz do vault — linha na seção de pesquisas recentes
3. Propor ao usuário:
   > "Pesquisa concluída. Quer adicionar a síntese ao `_inbox-aprendizados.md` como unidade atômica para o vault-garden processar?"
   
   Se confirmado: appendar bloco no inbox com slug + meta + link para `[[sintese]]`

---

## Relatório para o Usuário

Após arquivar tudo:

```
Pesquisa concluída: [Tópico]

Iterações: N | Buscas: N | Páginas criadas: N

Criadas:
  Base de Conhecimento/pesquisas-autonomas/[slug]/sintese.md
  Base de Conhecimento/pesquisas-autonomas/[slug]/fontes/ (N arquivos)
  Base de Conhecimento/pesquisas-autonomas/[slug]/conceitos/ (N arquivos)
  Base de Conhecimento/pesquisas-autonomas/[slug]/entidades/ (N arquivos)

Achados principais:
- [Achado 1]
- [Achado 2]
- [Achado 3]

Perguntas abertas: N
```

---

## Constraints

- Budget padrão de iterações: 5 (configurável em `program.md`)
- Máx páginas por sessão: 20 (para não sobrecarregar o vault)
- Se constraint conflitar com completude: respeitar o constraint e registrar o que ficou de fora nas Perguntas Abertas
- Não delegar ingestão para `/cerebro-lyncis:ingest` de forma recursiva — processar fontes diretamente no fluxo
- Mencionar a skill de ingest como opção para o usuário re-processar fontes individualmente depois

---

## Notas Importantes

- Verificar vault existente antes de criar qualquer nota (concept/entity pode já existir)
- Se Perplexity skill disponível: preferir sobre WebSearch (respostas mais sintetizadas)
- defuddle melhora qualidade do conteúdo web — verificar se está instalado e instruir se necessário
- Pesquisas são hardcoded em `Base de Conhecimento/pesquisas-autonomas/` — não criar em outro lugar
