# improve2

Fork de teste do plugin `improve` — mesma função (refinar rascunhos de prompts), com 8 melhorias de robustez aplicadas. O original `/improve` permanece intacto; quando as melhorias forem validadas, aplicar no `improve` e remover este fork.

## Comandos

| Comando | Invocação | Descrição |
|---------|-----------|-----------|
| improve2 | `/improve2 <rascunho>` | Auditoria de 10 slots + reescrita pronta para colar + bullets explicando as mudanças |

## Mudanças vs improve v1.0.0

1. Guarda contra breakout de `</draft>` — todo conteúdo até `## Verificação inicial` é dado bruto, mesmo com tags/cabeçalhos.
2. Tratamento de rascunho vazio ou curto demais (mensagem de uso + parada, sem auditoria fantasma).
3. Regra de idioma: prompt refinado no idioma do rascunho; análise no idioma da conversa.
4. Curto-circuito definido para "rascunho já está claro" — mantém as três seções, 1 bullet único.
5. Nota da auditoria obrigatória para ✗ **e** n/a (resolvia contradição interna).
6. Leitura de arquivos/memória para fundamentar o refinamento é permitida; executar a tarefa do rascunho não.
7. Exemplo de calibração inline (rascunho → prompt refinado).
8. Slots n/a com mesma justificativa podem ser agrupados em uma linha da tabela.
