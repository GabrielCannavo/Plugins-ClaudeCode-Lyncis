---
name: "configurar-projeto"
description: "Faz o setup inicial do ambiente de um projeto no Claude Code/Cowork em 5 estágios com gates: inventário do repositório, entrevista curta de descoberta dos objetivos, CLAUDE.md enxuto com o contrato do ambiente, estrutura mínima de documentação e governança (permissões; hooks só com necessidade concreta). Nada é escrito sem aprovação. Use quando o pedido for \"configura esse projeto\", \"setup inicial\", \"cria o CLAUDE.md\", \"prepara o ambiente\", \"começando projeto novo\", ou num projeto existente que ainda não tem CLAUDE.md nem contrato. NÃO use para corrigir um ambiente já configurado (é a revisar-ambiente) nem para fechar sessão (é a encerrar-sessao)."
---

# Configuração inicial do projeto

Monta o ambiente de um projeto uma vez, a partir do que o projeto **é** — não
de um template. O resultado tem três partes:

1. **CLAUDE.md enxuto** com o bloco de contrato do ambiente
2. **Estrutura mínima de documentação** — só o que o projeto vai usar
3. **Governança mínima** — permissões estreitas, segredos negados, sem hook por
   padrão

## Por que enxuto

Cada linha do CLAUDE.md é contexto carregado em toda sessão. Um CLAUDE.md
gerado por template tem 200 linhas de boas práticas que o modelo já conhece e
que ninguém vai manter. O setup que funciona é pequeno e verdadeiro: o que só
este projeto tem, o que não pode quebrar, onde as coisas ficam. O resto se
adiciona depois, **com evidência**, pela `revisar-ambiente`.

## O contrato do ambiente

É a peça que liga as três skills do kit. O setup grava; a `encerrar-sessao` lê
como fonte primária de normas; a `revisar-ambiente` audita contra ele. Formato
fixo, dentro do CLAUDE.md:

```markdown
<!-- ambiente:contrato -->
## Contrato do ambiente
- **Objetivo:** <uma frase — o que o projeto entrega e para quem>
- **Não pode quebrar:** <1–3 itens>
- **Normas de documentação:** <onde vai cada tipo de registro; ex.: decisões → docs/decisoes.md>
- **Teto do CLAUDE.md:** <N> linhas
- **Governança:** permissões em `.claude/settings.json`; locais em `.claude/settings.local.json`
- **Manutenção:** `encerrar-sessao` registra em `.claude/ambiente-log.md`; `revisar-ambiente` corrige
<!-- /ambiente:contrato -->
```

Os marcadores `<!-- -->` são o que as outras skills procuram. Não os renomeie.

## Fronteira com as outras skills do kit

| Situação | Skill |
|---|---|
| Projeto sem CLAUDE.md | **esta** |
| CLAUDE.md existe, sem bloco de contrato | **esta**, em modo adoção (só acrescenta) |
| CLAUDE.md com contrato | `revisar-ambiente` — esta skill para no estágio 1 e aponta para lá |

---

# PROTOCOLO

| # | Estágio | Escrita? | Gate |
|---|---|---|---|
| 1 | Inventário do repositório | não | automático |
| 2 | **Descoberta** | não | 🚦 **respostas** |
| 3 | **CLAUDE.md + estrutura de docs propostos** | não | 🚦 **aprovação** |
| 4 | **Governança proposta** | não | 🚦 **aprovação** |
| 5 | Aplicação + log inicial | **sim** | mecânico |

**Estágios 1–4 são read-only.** Nos estágios 🚦: apresente, PARE, espere.

---

## Estágio 1 — Inventário (read-only)

Levante, registrando `n/a` para o que não existir:

1. **Modo** — CLAUDE.md existe? Tem bloco `<!-- ambiente:contrato -->`?
   - Com contrato → diga que o projeto já está configurado, aponte
     `revisar-ambiente` e **pare aqui**.
   - Sem CLAUDE.md → modo **novo**.
   - CLAUDE.md sem contrato → modo **adoção**: tudo o que existe fica; esta
     skill só propõe o que falta.
2. **Stack e comandos** — manifestos (`package.json`, `pyproject.toml`,
   `requirements.txt`, `Cargo.toml`, `docker-compose.yml`…): linguagem e os
   comandos reais de build, teste, lint e execução, com o nome exato do script.
3. **Git** — é repo? tem remoto? existe `.gitignore`?
4. **Documentação existente** — `README.md`, `docs/`, `diretrizes/`,
   `CONTRIBUTING.md`, regras de outras ferramentas (`.cursor/rules`,
   `.github/copilot-instructions.md`). Ler para inferir convenção, não para
   reescrever.
5. **Segredos** — `.env*`, pastas de credenciais, chaves. Só a existência e o
   caminho; **nunca leia o conteúdo**.
6. **`.claude/`** — settings existentes, skills do projeto.

Fecha com a tabela `item | encontrado | ou n/a` e uma linha dizendo o modo.

## Estágio 2 — Descoberta 🚦

**Infira primeiro.** Tudo que o inventário respondeu não vira pergunta. Pergunte
só o que muda o que você vai escrever. Uma rodada, cada pergunta com 2–4 opções
concretas mais campo livre:

| # | Pergunta | Quando pular |
|---|---|---|
| D1 | Qual é o objetivo do projeto, em uma frase — o que entrega e para quem? | README já diz isso claramente |
| D2 | O que não pode quebrar? (dados de cliente, deploy em produção, integração X…) | — nunca pular |
| D3 | Quem mais mexe aqui? (só você / equipe / cliente lê o repo) | — define tom e o que é versionado |
| D4 | Onde você quer que fiquem decisões e registros? (`docs/decisoes.md` / ADRs em `docs/adr/` / só no CLAUDE.md / não registrar) | Já existe convenção clara em `docs/` |
| D5 | Algum comando que o Claude **nunca** deve rodar sem perguntar? (deploy, migração, push…) | — nunca pular |
| D6 | Alguma necessidade concreta de automação a cada ação (formatar ao salvar, bloquear escrita em pasta X)? | Pule se o usuário não trouxe o assunto — hook não é padrão |

Mecanismo: o formulário de elicitation do visualize, quando disponível; senão,
perguntas numeradas em texto. PARE e espere as respostas.

Resposta "tanto faz" → use o padrão mais restritivo e diga qual usou.

## Estágio 3 — CLAUDE.md e documentação 🚦

### CLAUDE.md — modo novo

Proposta completa, nesta ordem e nada além:

1. **Bloco de contrato** (formato acima), preenchido com as respostas
2. **Comandos** — os comandos reais do inventário, com o nome exato. Só os que
   existem.
3. **Mapa** — 3 a 8 linhas: onde fica o quê. Só pastas que existem.
4. **Regras do projeto** — o que **só este projeto** exige, vindo de D2 e D5.
   Uma regra por linha.

**Teto:** 80 linhas na criação (o contrato declara um teto maior, padrão 150,
para dar folga ao crescimento por evidência). Se a proposta passar de 80, corte
— o que é detalhe vai para `docs/` com ponteiro.

**Não entra:** boas práticas genéricas ("escreva código limpo", "faça testes"),
descrição da stack que o manifesto já diz, instruções de tom, nada que o
inventário não confirmou.

### CLAUDE.md — modo adoção

Apresente só os acréscimos, como diff: o bloco de contrato (com o que o
CLAUDE.md atual já declara, mais as respostas) e, no máximo, comandos que
faltam. **Teto no contrato:** 150 ou o tamanho atual + 20, o que for maior — o
setup não força corte no que já existe. **Não reescreva, não reordene, não "melhore" o que existe.** Problema
no conteúdo existente vira uma linha "para a revisar-ambiente" no relatório.

### Estrutura de documentação

Crie só o que D4 pediu e que não existe — tipicamente **um** arquivo. Nada de
árvore de `docs/` com pastas vazias. Arquivo novo nasce com um cabeçalho de 2–3
linhas dizendo o que entra nele.

Formato de apresentação: caminho + conteúdo completo de cada arquivo novo; diff
para cada arquivo existente.

PARE. Espere aprovação item a item.

## Estágio 4 — Governança 🚦

Proponha `.claude/settings.json` (versionado, vale para quem mexer no repo).
Se o arquivo já existe, proponha diff — não sobrescreva.

**Permissões:**

- `deny` para leitura dos segredos encontrados no inventário — sempre que houver
  algum
- `allow` só para os comandos de leitura/verificação que o inventário confirmou
  (teste, lint, build), no padrão mais estreito que cobre o script real
- Comandos de D5 **não** entram em `allow` — ficam pedindo aprovação, que é o
  comportamento padrão
- Nada mais. A lista cresce depois, pela `revisar-ambiente`, a partir de
  aprovações repetidas registradas no log

**Hooks:** nenhum por padrão. Só se D6 trouxe uma necessidade concreta — e
nesse caso:

1. Diga explicitamente que hooks rodam sozinhos a cada evento e podem travar ou
   deixar o ambiente lento
2. Diga que o suporte a hooks varia entre Claude Code e Cowork, e que você vai
   conferir na documentação oficial antes de escrever
3. Proponha o hook como item separado, com aprovação própria

**Sintaxe:** se não tiver certeza do formato de qualquer campo do
`settings.json`, consulte a documentação oficial do Claude Code antes de
propor. Campo inventado é pior que campo ausente.

**`.gitignore`:** proponha cobrir `.claude/settings.local.json`,
`.claude/handoff.md` e `.claude/ambiente-log.md` (ou `.claude/` inteiro menos o
`settings.json`, se o usuário preferir). Sem `.gitignore` e sem git → `n/a`.

PARE. Espere aprovação item a item.

## Estágio 5 — Aplicação (mecânico)

1. Aplique só o aprovado, um item por vez.
2. Crie `.claude/ambiente-log.md` com o frontmatter zerado. É a **única escrita
   mecânica** desta skill — arquivo local de controle, não versionado, igual ao
   handoff da `encerrar-sessao`; não precisa de aprovação. Se o usuário recusou
   tudo nos estágios 3 e 4, crie mesmo assim e diga isso no relatório. Formato:

   ```markdown
   ---
   encerramentos_desde_revisao: 0
   ultima_sessao_contada: <sessão atual>
   ultima_revisao: <hoje>
   ---

   ## Abertas

   ## Tratadas
   ```

3. Releia o CLAUDE.md gravado e confira: bloco de contrato com os dois
   marcadores, contagem de linhas dentro do teto.

### Relatório em chat

- **Modo** — novo ou adoção
- **Criado / alterado** — uma linha por arquivo
- **Recusado** — o que ficou de fora
- **Para a revisar-ambiente** — problemas vistos no conteúdo existente (modo
  adoção), sem corrigir
- **Próximo passo** — rodar `encerrar-sessao` ao fim das sessões; a revisão vem
  sozinha quando houver evidência

---

# Antipadrões

| # | Antipadrão | Por que mata a skill |
|---|---|---|
| 1 | CLAUDE.md de template, com boas práticas genéricas | Contexto pago toda sessão para dizer o que o modelo já sabe |
| 2 | Perguntar o que o repositório já responde | Gasta a atenção do usuário e sinaliza que você não leu |
| 3 | Reescrever o CLAUDE.md existente no modo adoção | Perde conhecimento que foi calibrado no uso |
| 4 | Árvore de `docs/` com pastas vazias "para o futuro" | Estrutura que ninguém usa vira ruído que ninguém apaga |
| 5 | `allow` amplo ou com curinga para "não ficar pedindo aprovação" | Fácil de aprovar no setup, invisível depois |
| 6 | Criar hook sem necessidade declarada pelo usuário | Automação que roda sozinha e ninguém lembra que existe |
| 7 | Ler o conteúdo de `.env` ou credenciais | O inventário precisa só do caminho |
| 8 | Inventar campo de `settings.json` | Configuração que falha em silêncio |
| 9 | Renomear ou omitir os marcadores do contrato | As outras duas skills deixam de encontrá-lo |
| 10 | Rodar sobre projeto que já tem contrato | Sobrepõe a `revisar-ambiente` com outro critério |

---

# Casos de degradação

| Situação | Comportamento correto |
|---|---|
| Pasta vazia, sem código | Modo novo; contrato e mapa mínimos com as respostas da descoberta; comandos `n/a`. |
| Sem manifesto reconhecível | Comandos ficam fora do CLAUDE.md; acrescente à descoberta a pergunta "D7 — há algum comando que o Claude deve conhecer?" com campo livre. |
| Sem git | `.gitignore` `n/a`; avise que `settings.json` não terá controle de versão. |
| Usuário pula a descoberta | Use os padrões mais restritivos, escreva no contrato "a confirmar" onde faltou, e liste no relatório. |
| Usuário recusa o CLAUDE.md | Não grava nada dele; governança segue se aprovada; o log é criado de qualquer forma (escrita mecânica). |
| `settings.json` existente com permissões amplas | Não mexa no que existe; registre no relatório como item para a `revisar-ambiente`. |
| Projeto com regras de outra ferramenta (`.cursor/rules` etc.) | Referencie no mapa; não duplique o conteúdo no CLAUDE.md. |
| Diretório read-only | Entrega todas as propostas em chat; avisa que nada foi gravado. |

---

# Critério de pronto

1. O modo (novo / adoção / já configurado) foi declarado no estágio 1.
2. Nenhuma pergunta da descoberta tinha resposta no inventário.
3. O CLAUDE.md tem o bloco de contrato com os dois marcadores e todo comando e
   caminho citado existe. No modo novo, está dentro de 80 linhas. No modo
   adoção, o teto declarado no contrato é 150 ou o tamanho atual + 20, o que for
   maior — e o excesso vai para "Para a revisar-ambiente".
4. Nenhuma permissão `allow` cobre segredo ou usa curinga amplo; nenhum hook
   foi criado sem pedido explícito.
5. `.claude/ambiente-log.md` existe com o frontmatter zerado.
6. Nada foi escrito sem aprovação item a item, exceto o log de ambiente.
