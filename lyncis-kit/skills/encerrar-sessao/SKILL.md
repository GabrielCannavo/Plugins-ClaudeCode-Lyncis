---
name: "encerrar-sessao"
description: "Encerra uma sessão de trabalho do Claude Code/Cowork em 6 estágios com gates: coleta sinais, checa conformidade com as normas de documentação do projeto, propõe diffs, propõe melhorias nas skills com base no atrito real da sessão, grava um handoff para a próxima sessão e registra no log de ambiente o que só uma revisão periódica resolve — sugerindo a skill revisar-ambiente quando a evidência acumula. Nada é escrito no projeto sem aprovação explícita. Use quando o pedido for encerrar/fechar a sessão, \"terminar por hoje\", \"wrap up\", \"fecha aí\", \"documenta o que fizemos\", ou antes de trocar de projeto."
---

# Encerramento de sessão

Protocolo de fechamento. **Não é um resumo de conversa** — é uma passagem de
estado: o que mudou no projeto, o que a documentação exige, o que a próxima
sessão precisa saber, e onde as ferramentas falharam.

Funciona em qualquer projeto. Não presume git, não presume estrutura de pastas,
não presume que exista documentação. Cada ausência vira uma linha `n/a` no
relatório — **nunca um erro que interrompe o encerramento**.

## Por que existe protocolo

Encerramento sem gate degrada de dois jeitos, e os dois são silenciosos:

1. **Vira teatro.** Se a skill "precisa" propor melhoria toda sessão, ela
   inventa melhoria. Depois de cinco sugestões genéricas o usuário para de ler —
   e perde a sexta, que era real.
2. **Vira escrita automática.** "É só um CHANGELOG" é como começa a poluição do
   repo com arquivos que ninguém pediu e ninguém lê.

Os gates existem para o usuário reprovar uma tabela de 4 linhas, não um commit.

## Divisão de trabalho com as outras skills do kit

| Skill | Escopo | Relação com esta |
|---|---|---|
| `encerrar-sessao` | **Esta sessão.** O que aconteceu aqui e o que a próxima precisa saber. | — |
| `revisar-ambiente` | **O projeto ao longo do tempo.** CLAUDE.md, docs, permissões, a partir da evidência acumulada. | Esta skill **escreve** o log que ela lê, e **sugere** quando rodá-la. Nunca a executa sem o usuário pedir. |
| `configurar-projeto` | **Setup inicial.** Cria CLAUDE.md, contrato do ambiente e governança. | Esta skill não cria CLAUDE.md; se o projeto não tem normas, no máximo menciona que `configurar-projeto` existe. |

---

# PARTE 0 — PROTOCOLO

| # | Estágio | Escrita? | Gate |
|---|---|---|---|
| 1 | Coleta de sinais | não | automático |
| 2 | Descoberta de normas + conformidade | não | automático |
| 3 | **Diffs de documentação propostos** | não | 🚦 **aprovação** |
| 4 | **Melhorias de skill propostas** | não | 🚦 **aprovação** |
| 5 | Aplicação do que foi aprovado | **sim** | mecânico |
| 6 | Handoff + log de ambiente + relatório | **sim** (só `.claude/`) | mecânico |

**Estágios 1–4 são read-only. Nenhuma ferramenta de escrita pode ser chamada
antes do estágio 5.** Se você se pegar prestes a editar algo no estágio 2, pare:
aquilo é conteúdo do estágio 3.

**Nos estágios 🚦: apresente, PARE, espere.** Não emende o próximo estágio na
mesma resposta. Aprovação parcial é normal — aplique só os itens aprovados,
item a item, nunca em bloco.

---

## Estágio 1 — Coleta de sinais (read-only)

Colete, na ordem, o que existir. Registre a ausência; não a contorne.

1. **Estado do repositório** — `git status --porcelain`, `git diff --stat`,
   `git log --oneline` desde o início da sessão. Sem repo git → `n/a`, e o
   estágio passa a depender só dos itens 2–5.
2. **Transcript da sessão** — o que foi pedido, o que foi entregue, e
   principalmente **onde houve atrito**: correção manual do usuário, instrução
   repetida, retrabalho, ferramenta que errou o formato, permissão aprovada
   várias vezes para o mesmo comando. Isso é o insumo dos estágios 4 e 6 — sem
   isso, os dois saem vazios.
3. **Tarefas** — `TASKS.md` ou equivalente na raiz do projeto, se existir.
   Leia; não crie.
4. **Skills invocadas** — quais SKILL.md foram carregados nesta sessão e em que
   ponto exigiram correção. Nenhuma skill usada → estágio 4 sai vazio.
5. **Log de ambiente** — `.claude/ambiente-log.md`, se existir. Leia o
   frontmatter (contador) e as observações abertas: o estágio 6 vai precisar
   delas para detectar recorrência. Ausente → `n/a`; o estágio 6 o cria se
   houver algo a registrar.

Fecha com uma linha por sinal: `sinal | encontrado em | ou n/a`.

## Estágio 2 — Normas de documentação (read-only)

**Descubra as normas em runtime.** Procure nesta ordem de precedência e pare na
primeira que existir — mas registre todas as que encontrou:

1. `CLAUDE.md` (raiz, depois `.claude/CLAUDE.md`) — se tiver o bloco
   `<!-- ambiente:contrato -->`, ele é a fonte primária de normas
2. `diretrizes/` ou `docs/CONTRIBUTING.md` / `CONTRIBUTING.md`
3. `docs/` — convenção inferida dos arquivos existentes
4. `README.md` — só a seção que fala de documentação, se houver
5. `.cursor/rules`, `.github/copilot-instructions.md` e similares

**Se nada for encontrado:** o projeto não tem normas. Escreva isso no relatório
e **passe direto ao estágio 3 sem propor nada de documentação**. Não invente
uma norma, não sugira criar um CLAUDE.md — a não ser que o usuário peça. Uma
linha no relatório pode mencionar que a skill `configurar-projeto` existe; não
mais que isso.

Monte a tabela de conformidade. Uma linha por norma que se aplica ao que foi
feito nesta sessão. Normas que não foram tocadas não entram na tabela.

| Norma | Onde está escrita | Status | Ação proposta |
|---|---|---|---|
| ex.: "toda decisão de arquitetura vira ADR" | `CLAUDE.md §4` | violada | criar `docs/adr/007-...md` |

Status: `ok` / `violada` / `n/a`. Só isso.

## Estágio 3 — Diffs de documentação 🚦

Para cada linha `violada` do estágio 2, apresente **o diff literal** — arquivo,
trecho antes, trecho depois. Não descreva a mudança em prosa; mostre.

Se a tabela não tem nenhuma linha `violada`: diga "nenhum diff de documentação
proposto" e siga. **Isso é um resultado bom, não uma falha da skill.**

PARE. Espere aprovação item a item.

## Estágio 4 — Melhoria contínua das skills 🚦

Escopo: skills do usuário (`~/.claude/skills/`), do projeto (`.claude/skills/`)
e **skills de plugin cuja fonte é editável**.

**Skills de plugin.** O arquivo carregado é cache read-only — editar ali não
persiste. Antes de descartar, procure a fonte:

1. O plugin vem de um marketplace local (um `marketplace.json` com `source`
   apontando para uma pasta que você consegue ler)? → o diff é proposto **contra
   o arquivo-fonte**, com caminho completo, e a proposta avisa que o plugin
   precisa de bump de versão e reinstalação para valer.
2. Não achou a fonte, ou não tem acesso a ela? → registre como observação no
   handoff e no log de ambiente (tipo `lacuna-skill`), não como diff.

Nunca edite o cache achando que é a fonte.

### Regra de admissão

**O padrão desta tabela é vazia.** Uma proposta só entra se passar nos **quatro**
testes abaixo. Falhou em um, está fora — não "está fraca", está fora.

| Teste | O que exige | Como se verifica |
|---|---|---|
| **T1 — Citação literal** | Trecho copiado do transcript, entre aspas, com quem disse. Paráfrase não vale. | Se você não consegue copiar as palavras, você não tem o caso |
| **T2 — Linha de origem** | A linha ou seção do SKILL.md que produziu o comportamento, citada literalmente | Se nenhuma linha da skill causou o problema, o problema não é da skill |
| **T3 — Custo consumado** | O atrito **já aconteceu** nesta sessão: correção à mão, instrução repetida, retrabalho, saída descartada | Risco hipotético e "poderia acontecer" reprovam |
| **T4 — Diff fecha a lacuna** | Aplicando o diff a T2, o caso de T1 não se repetiria | Se o diff só melhora a redação, reprova |

**Formato obrigatório de cada proposta.** Sem os campos preenchidos com material
literal, a proposta não é apresentada:

```
Skill:        <nome>  (fonte: <caminho do arquivo que será editado>)
T1 evidência: "<citação literal do transcript>" — <quem>
T2 origem:    <arquivo> · "<linha citada literalmente>"
T3 custo:     <o que precisou ser refeito, em uma frase factual>
T4 diff:      - <linha removida>
              + <linha adicionada>
Custo de não aplicar: <o que se repete na próxima sessão>
```

Máximo 3 propostas. Se mais de 3 passarem nos quatro testes, apresente as 3 de
maior T3 e diga quantas ficaram de fora.

### Reprovações típicas — leia antes de propor

| Tentativa | Veredito |
|---|---|
| "A skill poderia ser mais clara sobre X" | **Reprova T1 e T3** — sem citação, sem custo consumado |
| "Boa prática seria adicionar uma checagem de Y" | **Reprova T1, T2 e T3** — vem do seu treino, não da sessão |
| "O usuário corrigiu o tom duas vezes, mas a skill não fala de tom" | **Reprova T2** — nenhuma linha causou; é lacuna, e lacuna vira observação no handoff e no log, não diff |
| "Notei inconsistência de formatação entre duas skills" | **Reprova T3** — não custou nada nesta sessão |
| "O usuário disse 'não, o arquivo vai em docs/, não na raiz' e a skill manda 'salve na raiz do projeto'" | **Passa** — citação, linha de origem, retrabalho e diff que fecha |

**Sessão sem atrito → zero propostas.** Escreva "nenhuma melhoria proposta —
nenhum caso passou na regra de admissão" e siga. Preencher essa tabela por
preencher é a falha mais provável desta skill: uma proposta fraca custa mais
credibilidade do que dez encerramentos silenciosos custam de oportunidade.

**Auto-checagem antes de apresentar:** se a única razão pela qual você está
propondo algo é que a tabela parece vazia demais, apague e escreva a linha de
"nenhuma proposta".

Antes de propor, verifique a seção `## Descartadas` do handoff (estágio 6): se
uma proposta equivalente já foi recusada antes, **não reproponha**.

PARE. Espere aprovação item a item.

## Estágio 5 — Aplicação (mecânico)

Aplique **apenas** o que foi aprovado, um item por vez. Nada aprovado → nada
escrito, e o estágio se resume a uma linha no relatório.

Ao editar um SKILL.md, use a skill `skill-creator` se ela estiver disponível —
ela conhece o formato do frontmatter e a validação de `description`. Se não
estiver, edite direto, preservando o frontmatter intacto. Se editou a fonte de
um plugin, diga no relatório qual versão precisa subir e que é preciso
reinstalar.

## Estágio 6 — Handoff, log de ambiente e relatório (mecânico)

### 6a. Handoff

**Destino:** `.claude/handoff.md` na raiz do projeto — arquivo local, não
versionado. Se `.gitignore` existir e não cobrir `.claude/handoff.md` e
`.claude/ambiente-log.md`, **proponha** essas duas linhas — não `.claude/`
inteiro, porque `.claude/settings.json` é versionado (é uma escrita: precisa de
aprovação). Se o usuário recusar, grave assim mesmo e avise que vai aparecer no
diff.

**Idempotência.** O arquivo tem esta forma:

```markdown
---
sessao: <id ou data-hora do início>
atualizado: <AAAA-MM-DD HH:MM>
---

## Estado
## Pendências
## Descartadas
```

Ao rodar: se `sessao` no arquivo **for a mesma** desta execução, **substitua** o
bloco — não anexe. Rodar duas vezes na mesma sessão produz o mesmo arquivo.
Se `sessao` for **diferente** e as pendências anteriores não aparecem no estado
atual, **o handoff anterior não foi consumido**: mostre o que vai ser perdido e
pergunte antes de sobrescrever.

`## Descartadas` acumula, uma linha por proposta recusada, para que a skill não
insista em execuções futuras. **É a única seção preservada** quando o handoff é
substituído: copie as linhas existentes para o arquivo novo antes de
acrescentar as desta sessão.

### 6b. Log de ambiente

O handoff é sobrescrito a cada sessão (menos `## Descartadas`); o log **acumula**. É a única memória que
a `revisar-ambiente` tem entre sessões — sem ele, ela audita de memória de
treino.

**Destino:** `.claude/ambiente-log.md` — local, não versionado (a proposta de
`.gitignore` do 6a já o cobre). Formato:

```markdown
---
encerramentos_desde_revisao: <inteiro>
ultima_sessao_contada: <id da sessão>
ultima_revisao: <AAAA-MM-DD | nunca>
---

## Abertas
- [AAAA-MM-DD · <sessao>] <tipo> · <destino> · <chave> — <descrição em uma linha> · evidência: "<citação ou fato verificável>"

## Tratadas
- [AAAA-MM-DD] <chave> → aplicada | descartada | resolvida | expirada — <motivo curto>
```

**O que registrar** — só o que esta sessão produziu e que um encerramento não
resolve sozinho:

| Tipo | Quando entra | Destino típico |
|---|---|---|
| `lacuna-skill` | Atrito real que reprovou em T2 (nenhuma linha causou), ou skill de plugin sem fonte acessível | `skill:<nome>` |
| `norma-violada` | Linha `violada` do estágio 2 cujo diff **não** foi aplicado | `claude-md` ou `docs` |
| `instrucao-repetida` | O usuário repetiu na sessão uma instrução que não está escrita em lugar nenhum do projeto | `claude-md` |
| `permissao-repetida` | O mesmo comando ou ferramenta pediu aprovação 2+ vezes na sessão (quando visível no transcript) | `permissoes` |
| `claude-md-desatualizado` | O CLAUDE.md afirma algo que a sessão provou falso (comando, caminho, convenção) | `claude-md` |

**Toda linha precisa de evidência literal** — citação do transcript ou fato
verificável ("CLAUDE.md §3 manda `npm test`, o projeto não tem `package.json`").
Opinião sua não entra no log.

**`chave`** é um slug curto e estável que identifica o mesmo problema entre
sessões (ex.: `docs-adr-ausente`, `permissao-npm-test`). Antes de criar uma
linha, procure a mesma `chave` em `## Abertas`: se já existe, **não duplique** —
anexe a data/sessão nova à linha existente. Uma chave com 2+ sessões é
**recorrente**.

**Contador.** Se `ultima_sessao_contada` ≠ sessão atual, incremente
`encerramentos_desde_revisao` e grave a sessão atual. Se for igual (segunda
execução na mesma sessão), não incremente.

**Criação.** Log ausente → crie sempre o esqueleto completo (frontmatter, `##
Abertas`, `## Tratadas`) com `encerramentos_desde_revisao: 1`, a sessão atual em
`ultima_sessao_contada` e `ultima_revisao: nunca`; depois acrescente as linhas
desta sessão, se houver. O arquivo é local e de controle; não precisa de
aprovação, como o handoff.

### 6c. Gatilho da revisar-ambiente

Depois de gravar o log, avalie — **qualquer uma** dispara a sugestão:

1. `## Abertas` tem **3 ou mais** linhas **novas** — criadas ou com ocorrência
   anexada depois de `ultima_revisao`
2. Alguma chave em `## Abertas` ficou **recorrente** (2+ sessões) com pelo
   menos uma dessas ocorrências depois de `ultima_revisao`
3. `encerramentos_desde_revisao` chegou a **5**

Linhas que a última revisão deixou abertas de propósito (únicas aguardando
recorrência, lacunas de skill aguardando decisão) **não contam** até ganharem
ocorrência nova — senão todo encerramento sugere uma revisão que dá zero
propostas.

Disparou → a última linha do relatório é:

> **Ambiente:** <N> observações novas (<R> recorrentes), <C> encerramentos desde a última revisão. Rodar `revisar-ambiente` agora?

E PARE. Se o usuário aceitar, invoque a skill `revisar-ambiente`. Se recusar,
não insista nesta sessão — o próximo encerramento avalia de novo.

Não disparou → nenhuma linha sobre ambiente no relatório. Silêncio é o
comportamento correto.

### Relatório em chat

Markdown, factual, sem adjetivo de auto-avaliação:

- **Feito nesta sessão** — máx. 5 bullets, no passado, verificáveis
- **Pendências abertas** — item · arquivo/local · próximo passo concreto
- **Conformidade documental** — a tabela do estágio 2
- **Melhorias de skill** — a tabela do estágio 4, ou "nenhuma proposta"
- **Handoff** — um parágrafo. Contexto suficiente para a próxima sessão começar
  sem reler esta. Estado e decisão, não narrativa.
- **Ambiente** — só se o gatilho 6c disparou

---

# Antipadrões

Cada item abaixo é **falha de aceite**, não preferência de estilo.

| # | Antipadrão | Por que mata a skill |
|---|---|---|
| 1 | Escrita silenciosa — criar/alterar arquivo "óbvio" sem diff aprovado | Uma vez que o usuário não confia no que ela grava, ele para de rodá-la |
| 2 | Sugestão que não passa nos testes T1–T4 do estágio 4 | Boas práticas genéricas o usuário já conhece; o valor está no que falhou aqui |
| 3 | Melhoria performática — propor algo toda sessão | Ruído recorrente treina o usuário a pular a seção inteira |
| 4 | Vazar nome de cliente, caminho ou convenção de outro projeto | Quebra a premissa de portabilidade |
| 5 | Reescrever SKILL.md que funcionou, a pretexto de padronizar | Introduz regressão em algo já calibrado |
| 6 | Handoff que narra a conversa | A próxima sessão precisa de estado, não de ata |
| 7 | Criar README/docs/ que o projeto não pediu | Conformidade é seguir a norma existente, não expandi-la |
| 8 | Falhar por artefato ausente | Ausência é `n/a`; encerramento não pode travar |
| 9 | Sobrescrever handoff anterior não consumido | Perde a pendência exatamente quando ela importava |
| 10 | Auto-elogio no relatório ("sessão produtiva") | Ocupa espaço que era do próximo passo |
| 11 | Registrar no log opinião em vez de evidência ("CLAUDE.md poderia ser mais organizado") | O log vira lixão e a `revisar-ambiente` passa a propor teatro |
| 12 | Duplicar no log uma chave que já está aberta | Esconde a recorrência, que é justamente o sinal que o gatilho procura |
| 13 | Executar a `revisar-ambiente` sem o usuário aceitar | Transforma um encerramento de 2 minutos em uma auditoria que ninguém pediu |
| 14 | Editar o cache de um plugin achando que é a fonte | A edição some na próxima atualização e o usuário acha que foi aplicada |

---

# Casos de degradação

| Situação | Comportamento correto |
|---|---|
| Projeto sem git | Estágio 1 marca `n/a`; "Feito nesta sessão" vem do transcript. Não sugerir `git init`. |
| Projeto sem normas de documentação | Estágio 2 reporta "sem normas"; estágio 3 sai vazio. Não propor criar CLAUDE.md sem o usuário pedir. |
| Sessão sem skill invocada | Estágio 4 sai vazio, com a razão explícita. |
| Sessão sem atrito | Estágio 4 sai vazio e o log só recebe o contador. Resultado esperado, não erro. |
| Atrito real, mas nenhuma linha da skill o causou (reprova T2) | Vira observação no handoff e linha `lacuna-skill` no log — nunca diff. Lacuna é decisão de escopo do usuário, não sua. |
| Atrito veio de instrução ambígua do usuário, não da skill | Nada a propor. Registrar como observação, se relevante para a próxima sessão. |
| Sem `TASKS.md` | Pendências vêm do transcript e do handoff anterior. Não criar `TASKS.md`. |
| Diretório read-only / sem permissão de escrita | Entrega o relatório completo em chat e informa que handoff e log não foram gravados. |
| `.claude/handoff.md` anterior não consumido | Mostra o conteúdo em risco e pergunta antes de sobrescrever. |
| Atrito veio de skill de plugin com fonte acessível | Diff proposto contra a fonte, com aviso de bump de versão e reinstalação. |
| Atrito veio de skill de plugin sem fonte acessível | Observação no handoff e `lacuna-skill` no log, não diff. |
| Segunda execução na mesma sessão | Substitui o bloco do handoff; não incrementa o contador; não duplica linhas no log; não repropõe o que já foi recusado. |
| Log com formato corrompido ou editado à mão | Não reescreva o que não entende: anexe as linhas novas ao fim de `## Abertas` e avise no relatório. |

---

# Critério de pronto

O encerramento está completo quando:

1. Todo sinal do estágio 1 tem `encontrado` ou `n/a` explícito.
2. Nenhum arquivo do projeto foi escrito sem aprovação nomeada (handoff e log em
   `.claude/` são a exceção mecânica).
3. O handoff cabe em um parágrafo e não cita nada que não esteja no projeto.
4. Toda proposta do estágio 4 exibe T1–T4 preenchidos com material literal —
   citação do transcript e linha citada do SKILL.md. Proposta sem os quatro
   campos não deveria ter chegado ao usuário.
5. Numa sessão limpa, o relatório diz "nenhuma melhoria proposta" — e não
   inventa uma para parecer útil.
6. Toda linha nova do log tem evidência literal e uma chave que não duplica uma
   aberta; o contador subiu no máximo uma vez nesta sessão.
7. A sugestão de `revisar-ambiente` aparece só quando o gatilho 6c dispara.
