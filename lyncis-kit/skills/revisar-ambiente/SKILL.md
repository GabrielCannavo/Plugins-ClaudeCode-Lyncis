---
name: "revisar-ambiente"
description: "Revisa a saúde do ambiente de um projeto do Claude Code/Cowork — CLAUDE.md, contrato do ambiente, documentação e permissões — a partir da evidência acumulada no log de ambiente entre sessões e de fatos verificáveis no repositório. Propõe diffs com gate e nada é escrito sem aprovação. Use quando a skill encerrar-sessao sugerir a revisão, quando o pedido for \"revisa o ambiente\", \"o CLAUDE.md tá desatualizado\", \"arruma as diretrizes do projeto\", \"limpa o log de ambiente\", ou \"o Claude vive esquecendo X neste projeto\". NÃO use para setup de projeto novo (é a configurar-projeto) nem para fechar a sessão atual (é a encerrar-sessao)."
---

# Revisão do ambiente

Manutenção periódica do ambiente do projeto. A pergunta que esta skill responde
é **"o que o uso real mostrou que está errado ou faltando?"** — não "o que seria
boa prática ter".

## Por que existe regra de evidência

Uma auditoria de ambiente sem fonte de evidência sempre encontra algo: dá para
reorganizar qualquer CLAUDE.md, dá para sugerir qualquer hook. Esse é o caminho
para o CLAUDE.md inchar, as permissões abrirem e o usuário parar de ler a
revisão. Por isso esta skill só age sobre duas fontes:

1. **Evidência acumulada** — linhas do `.claude/ambiente-log.md`, gravadas pela
   `encerrar-sessao`, com citação ou fato de sessões reais.
2. **Fatos verificáveis agora** — coisas que você confere lendo o repositório,
   sem opinião: caminho citado que não existe, comando citado que o projeto não
   tem, contradição entre dois arquivos, CLAUDE.md acima do teto.

Fora dessas duas, não há proposta.

## Fronteira com as outras skills do kit

| Skill | Faz | Não faz |
|---|---|---|
| `configurar-projeto` | Cria do zero: CLAUDE.md, contrato, estrutura de docs, governança | Corrigir drift |
| **`revisar-ambiente`** | Corrige o que existe com base em evidência; amplia permissões com base em aprovações repetidas | Criar estrutura nova sem evidência; reescrever CLAUDE.md por estilo |
| `encerrar-sessao` | Escreve o log; sugere esta skill | Executar esta skill sem o usuário aceitar |

Se o projeto **não tem CLAUDE.md**, esta skill não cria: diga que o caminho é a
`configurar-projeto` e pare depois do estágio 2. Se tem CLAUDE.md mas não tem
o bloco de contrato, siga a revisão normalmente e aponte a `configurar-projeto`
(modo adoção) para criar o bloco — esta skill não o escreve.

---

# PROTOCOLO

| # | Estágio | Escrita? | Gate |
|---|---|---|---|
| 1 | Leitura | não | automático |
| 2 | Verificações factuais + agrupamento da evidência | não | automático |
| 3 | **Diffs propostos** | não | 🚦 **aprovação** |
| 4 | Aplicação item a item | **sim** | mecânico |
| 5 | Fechamento do log | **sim** (só `.claude/ambiente-log.md`) | mecânico |

**Estágios 1–3 são read-only.** Nos estágios 🚦: apresente, PARE, espere.
Aprovação parcial é normal — aplique só o aprovado, item a item.

---

## Estágio 1 — Leitura (read-only)

Leia o que existir e registre `n/a` para o resto:

1. `.claude/ambiente-log.md` — frontmatter e `## Abertas`
2. `CLAUDE.md` (raiz, depois `.claude/CLAUDE.md`) — inteiro, e o bloco
   `<!-- ambiente:contrato -->` se houver
3. Arquivos que o CLAUDE.md referencia (docs, diretrizes) — só a existência e
   o trecho citado, não o repositório inteiro
4. `.claude/settings.json` e `.claude/settings.local.json` — permissões e hooks
5. `.claude/handoff.md` — só `## Descartadas`, para não repropor o que já foi
   recusado
6. `.gitignore` — se cobre `.claude/`

Fecha com uma linha por item: `arquivo | lido | linhas | ou n/a`.

## Estágio 2 — Verificações factuais e agrupamento (read-only)

### 2a. Verificações factuais

Rode estas checagens. Cada uma tem resposta sim/não, sem julgamento:

| # | Checagem | Como |
|---|---|---|
| F1 | Todo caminho citado no CLAUDE.md existe | Liste os caminhos, confira cada um |
| F2 | Todo comando citado no CLAUDE.md é executável no projeto | Ex.: `npm run x` → existe o script em `package.json`? Não execute o comando |
| F3 | CLAUDE.md está dentro do teto | Teto do contrato; sem contrato, 150 linhas |
| F4 | Bloco de contrato existe e tem os campos (objetivo, normas, teto) | Leitura do bloco. Bloco ausente → não propõe criar; vai para "Para decidir" apontando `configurar-projeto` (modo adoção) |
| F5 | Nenhuma permissão `allow` cobre leitura de segredos (`.env`, chaves, credenciais) | Leitura do settings |
| F6 | Nenhum hook aponta para script que não existe | Leitura do settings + existência do arquivo |
| F7 | `.gitignore` cobre `.claude/handoff.md` e `.claude/ambiente-log.md` | Leitura |

Cada falha vira um item com evidência `F<n>: <fato>`.

### 2b. Agrupamento da evidência do log

Agrupe as linhas de `## Abertas` por destino (`claude-md`, `docs`, `permissoes`,
`skill:<nome>`). Para cada linha, classifique:

| Classe | Critério | Vai para proposta? |
|---|---|---|
| **Recorrente** | Mesma chave em 2+ sessões | Sim |
| **Factual** | Linha cuja evidência é fato verificável (não citação) e que você reconfirmou agora | Sim |
| **Única** | Uma sessão só, evidência é citação | **Não** — fica aberta esperando recorrência |
| **Velha** | Única e com mais de 60 dias | Não — o estágio 5 expira |
| **Resolvida** | O problema não existe mais no estado atual do repo | Não — o estágio 5 fecha como tratada |

**Linhas `skill:<nome>`** não viram diff aqui — skill é escopo do estágio 4 da
`encerrar-sessao`. Se forem recorrentes, liste-as no relatório como "lacuna
recorrente em <skill>: decidir escopo" e deixe a decisão com o usuário.

## Estágio 3 — Diffs propostos 🚦

Uma proposta por item que passou no estágio 2. **Máximo 5.** Se passarem mais,
apresente as 5 de maior recorrência (fatos F5 e F6 primeiro — são risco) e diga
quantas ficaram para a próxima revisão.

Formato obrigatório:

```
Destino:     <arquivo>
Evidência:   <F<n>: fato>  ou  <chave> — <sessões: data1, data2> — "<citação>"
Diff:        - <linha removida>
             + <linha adicionada>
Efeito no teto: <CLAUDE.md passa de X para Y linhas>   (só se o destino for CLAUDE.md)
Custo de não aplicar: <o que se repete>
```

### Regras por destino

- **CLAUDE.md** — prefira **remover ou corrigir** a acrescentar. Toda linha do
  CLAUDE.md é contexto pago em toda sessão. Se a proposta acrescenta conteúdo
  que passa de ~3 linhas, o conteúdo vai para `docs/` e o CLAUDE.md ganha só o
  ponteiro. Proposta que estoura o teto não é apresentada sem um corte
  compensatório no mesmo diff.
- **Permissões** — só amplie `allow` a partir de `permissao-repetida`
  recorrente, e com o padrão mais estreito que cobre o caso (o comando exato,
  não um curinga amplo). Nunca amplie para leitura de segredos. Se não tiver
  certeza da sintaxe do `settings.json`, diga isso e consulte a documentação
  oficial do Claude Code antes de propor — não invente formato.
- **Hooks** — esta skill **não cria hook**. Pode propor remover um hook quebrado
  (F6). Necessidade de hook novo vira item "decidir" no relatório.
- **docs/** — corrige ou move; não cria uma estrutura de pastas nova.

**Nada passou no estágio 2 → zero propostas.** Escreva "ambiente sem evidência
para agir — nenhuma proposta" e vá ao estágio 5. Isso é o resultado esperado na
maioria das revisões.

Antes de apresentar, cheque `## Descartadas` do handoff e `## Tratadas` do log:
proposta equivalente já recusada **não volta**, a menos que a evidência tenha
ganhado sessões novas depois da recusa — e nesse caso diga isso explicitamente.

PARE. Espere aprovação item a item.

## Estágio 4 — Aplicação (mecânico)

Aplique só o aprovado, um item por vez, relendo o arquivo antes de cada edição.
Depois de editar o CLAUDE.md, reconte as linhas e confira o teto.

## Estágio 5 — Fechamento do log (mecânico)

No `.claude/ambiente-log.md`:

1. Mova para `## Tratadas` cada linha aplicada (`→ aplicada`), recusada
   (`→ descartada — <motivo do usuário>`), resolvida sozinha
   (`→ resolvida — <fato>`) ou velha (`→ expirada — 60 dias sem recorrência`).
2. Linhas únicas e recentes **ficam** em `## Abertas`.
3. Zere `encerramentos_desde_revisao` e grave `ultima_revisao` com a data.
4. `## Tratadas` com mais de 30 linhas → mantenha as 30 mais recentes; as mais
   antigas viram uma linha de resumo (`[até AAAA-MM-DD] N itens tratados`).

Log ausente → crie com o frontmatter zerado e `ultima_revisao` de hoje.

### Relatório em chat

- **Verificações factuais** — tabela F1–F7 com ok / falhou
- **Evidência do log** — contagem por classe (recorrente, factual, única,
  velha, resolvida)
- **Aplicado** — uma linha por diff aplicado
- **Para decidir** — lacunas recorrentes de skill, necessidade de hook, qualquer
  coisa que é escopo do usuário e não sua
- **Próxima revisão** — o que ficou aberto esperando recorrência, em uma linha

---

# Antipadrões

| # | Antipadrão | Por que mata a skill |
|---|---|---|
| 1 | Propor algo sem evidência do log nem fato verificável | É exatamente o teatro que a regra de evidência existe para impedir |
| 2 | Reescrever o CLAUDE.md "para organizar" | Regressão em algo calibrado, e o diff fica impossível de revisar |
| 3 | Acrescentar ao CLAUDE.md sem corte compensatório quando perto do teto | O CLAUDE.md incha um item razoável por vez |
| 4 | Ampliar permissão com curinga ou para segredos | Fácil de aprovar, difícil de notar depois |
| 5 | Criar hook | Hook roda sozinho, pode travar o ambiente, e o comportamento varia entre Claude Code e Cowork |
| 6 | Criar CLAUDE.md ou contrato num projeto que não tem | É trabalho da `configurar-projeto`, com descoberta |
| 7 | Editar SKILL.md | É escopo da `encerrar-sessao`, com T1–T4 |
| 8 | Repropor o que foi recusado sem evidência nova | Ensina o usuário a recusar tudo |
| 9 | Esquecer o estágio 5 | O log só cresce e o gatilho dispara para sempre |
| 10 | Executar um comando para checar F2 | Checagem é leitura; executar tem efeito colateral |

---

# Casos de degradação

| Situação | Comportamento correto |
|---|---|
| Log ausente | Roda só as verificações factuais; no estágio 5, cria o log zerado. |
| Log vazio e todas as F ok | "Ambiente sem evidência para agir." Zera o contador e encerra. |
| Projeto sem CLAUDE.md | Para no estágio 2, aponta `configurar-projeto`. |
| CLAUDE.md sem bloco de contrato | F4 falha; nenhuma proposta de bloco. Aponta `configurar-projeto` em modo adoção, que faz a descoberta. As demais verificações seguem normalmente. |
| Sem `settings.json` | F5 e F6 viram `n/a`. Não propõe criar. |
| Só linhas únicas no log | Zero propostas; elas ficam abertas. |
| Usuário recusa tudo | Move para Tratadas como descartadas e zera o contador — senão a próxima sessão dispara de novo pelo mesmo motivo. |
| Diretório read-only | Relatório completo em chat; avisa que o log não foi atualizado. |

---

# Critério de pronto

1. F1–F7 têm resultado explícito (ok / falhou / n/a).
2. Toda proposta mostra evidência do log com sessões datadas, ou um fato F<n>.
3. Nenhum diff de CLAUDE.md estoura o teto sem corte compensatório.
4. Nenhuma permissão nova cobre segredos ou usa curinga amplo; nenhum hook foi
   criado.
5. O log terminou com contador zerado, `ultima_revisao` de hoje, e cada linha
   tratada movida com o motivo.
6. Sem evidência, o relatório diz isso — e não inventa proposta.
