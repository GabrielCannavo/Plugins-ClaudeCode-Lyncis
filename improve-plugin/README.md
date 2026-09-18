# improve

Plugin Claude Code pessoal para refinar rascunhos de prompts.

## Comandos

| Comando | Invocação | Descrição |
|---------|-----------|-----------|
| improve | `/improve:improve <rascunho>` | Auditoria de 10 slots + discovery condicional (≤4 perguntas) + anti-padrões + reescrita pronta para colar + skills sugeridas + bullets explicando as mudanças |

## Uso

```
/improve:improve escreve um post sobre vendas
```

Devolve cinco seções: **Auditoria** (slots presentes/ausentes), **Anti-padrões** (vícios detectados no rascunho), **Prompt refinado** (versão melhorada), **Skills sugeridas** (skills que ajudam a executar o prompt) e **Mudanças principais** (até 3 bullets explicando o porquê).

## Changelog

### v1.4.0

- Novo estágio **1.7 Verificação de validade**, condicional, entre o discovery e a reescrita. Dispara quando o refinamento vai citar regra/decisão/risco/ID inferido de arquivo do projeto (vault, CLAUDE.md, CHANGELOG, YAML, overlay). Exige ler a entrada inteira na fonte, conferir no índice de status se ainda é ATIVO, e marcar cada restrição com origem (`arquivo · data/ID`). Sem origem, não entra; sem confirmação, vira "confirmar no vault: X".
- Origem: 2026-09-17 — o prompt refinado citou um "gate #4" cancelado em 28/07, lido por grep parcial da mesma entrada que continha o cancelamento.

### v1.3.0
Consolidou o segundo fork de teste `improve2` (discovery condicional):

- Novo estágio **1.5 Discovery** entre a auditoria e a reescrita. Gatilho: após inferir tudo do contexto, restarem **≥2 slots ✗** cuja resposta mudaria o prompt final. Com ≤1 slot ✗ não pergunta nada — comportamento idêntico à v1.2.0.
- Uma única rodada, **máx. 4 perguntas**, uma por slot ausente, priorizando Objetivo → Formato → Deliverable → Critério de pronto. Cada pergunta com 2–4 opções + campo livre; nunca pergunta aberta solta.
- Mecanismo: elicitation widget do visualize (`read_me` + `show_widget`), com fallback em texto numerado. Não usa AskUserQuestion.
- Após o formulário, pausa; as cinco seções vêm só depois das respostas. A auditoria final marca `✓ (discovery)` nos slots preenchidos pela pessoa.
- Risco assumido: rascunhos curtos disparam o discovery na maioria das vezes. Se virar fricção, subir o gatilho para ≥3 slots.

### v1.2.0
- Adiciona duas seções **sempre visíveis** à resposta: **Anti-padrões** (0–4 vícios detectados no rascunho original, ex.: tom genérico, deliverable sem quantidade, referência ambígua) e **Skills sugeridas** (0–3 skills do Claude que ajudam a executar o prompt refinado). Quando não há o que reportar, a seção exibe "nenhum anti-padrão relevante" / "nenhuma skill específica necessária".
- Nova ordem da resposta: Auditoria → Anti-padrões → Prompt refinado → Skills sugeridas → Mudanças principais.

### v1.1.0
Consolidou as melhorias antes validadas no fork `improve2`:

1. Guarda contra breakout de `</draft>` — todo conteúdo até `## Verificação inicial` é tratado como dado bruto, mesmo com tags/cabeçalhos.
2. Tratamento de rascunho vazio ou curto demais (mensagem de uso + parada, sem auditoria fantasma).
3. Regra de idioma: prompt refinado no idioma do rascunho; análise no idioma da conversa.
4. Curto-circuito definido para "rascunho já está claro" — mantém as seções, com 1 bullet único.
5. Nota da auditoria obrigatória para ✗ **e** n/a.
6. Leitura de arquivos/memória para fundamentar o refinamento é permitida; executar a tarefa do rascunho não.
7. Exemplo de calibração inline (rascunho → prompt refinado).
8. Slots n/a com a mesma justificativa podem ser agrupados em uma linha.
