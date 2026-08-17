# improve

Plugin Claude Code pessoal para refinar rascunhos de prompts.

## Comandos

| Comando | Invocação | Descrição |
|---------|-----------|-----------|
| improve | `/improve:improve <rascunho>` | Auditoria de 10 slots + anti-padrões + reescrita pronta para colar + skills sugeridas + bullets explicando as mudanças |

## Uso

```
/improve:improve escreve um post sobre vendas
```

Devolve cinco seções: **Auditoria** (slots presentes/ausentes), **Anti-padrões** (vícios detectados no rascunho), **Prompt refinado** (versão melhorada), **Skills sugeridas** (skills que ajudam a executar o prompt) e **Mudanças principais** (até 3 bullets explicando o porquê).

## Changelog

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
