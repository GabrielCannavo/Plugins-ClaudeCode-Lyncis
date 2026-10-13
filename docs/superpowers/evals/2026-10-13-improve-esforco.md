# Eval — improve v1.6.0 (Esforço, Postura, correção de rumo)

Data: 2026-10-13 · Método: subagentes simulam o comando (sem visualize) sobre rascunhos fixos; o antigo (v1.5.1) serve de linha de base. Os subagentes não conheciam os critérios.

| # | Rascunho | v1.5.1 (base) | v1.6.0 | Critério | Resultado |
|---|----------|---------------|--------|----------|-----------|
| 1 | E-mail de follow-up, 5 dias, máx 120 palavras | prompt com ~110 palavras | Esforço e Postura `n/a`, nenhuma armadilha, prompt **menor** que a base | não inchar | ✓ |
| 2 | Renomear `x` → `totalPedidos` | — | `baixo`, só "Não altere outra lógica." | ≤ 1 linha | ✓ |
| 3 | Webhook Chatwoot duplicando (produção) | já investigativo, sem bloco de esforço | `alto`, 3 armadilhas específicas, postura comportamental | 1-3 armadilhas específicas | ✓ (ressalva abaixo) |
| 4 | 3 ganchos de carrossel, advogada previdenciária | — | `médio`, postura "descreva a cena antes do gancho", 2 armadilhas | postura como comportamento | ✓ |
| 5 | Correção de rumo com histórico (copy) | discovery genérico, ignorou os ganchos entregues | **1ª rodada: ✗** (discovery sem citar o X). Após correção: discovery abre citando os 3 ganchos e só pergunta o que o histórico não responde | X citado do histórico | ✓ após correção |
| 5' | Correção de rumo com histórico (debug n8n, caso novo) | — | discovery pulado; "Pare de propor correção a partir de uma única execução… Passe a investigar a causa"; esforço recalibrado para alto; Papel `n/a` | contraste com X real | ✓ |
| 5b | Correção de rumo sem histórico | — | perguntou "O que a versão atual está fazendo de errado?" | não inventar X | ✓ |

## Correção feita durante a eval

A falha do caso 5 vinha da ordem: o discovery (§1.5) roda antes da reescrita, e a regra de correção de rumo só estava em §2.1. Foi acrescentado em §1.5 que, com histórico, a correção de rumo é decidida antes do discovery: o histórico conta como inferência, o "pare X" nunca vira pergunta, e as perguntas restantes abrem citando o X identificado.

## Ressalvas

- O caso 3 é igual ao exemplo de calibração da skill (§6), então mostra aderência ao exemplo, não generalização. O caso 5' (debug n8n, fora dos exemplos) cobre a generalização.
- No caso 3 o ganho sobre a base é modesto: a v1.5.1 já produzia um prompt investigativo. O ganho claro da v1.6.0 está na correção de rumo (casos 5 e 5').
- Eval qualitativa, uma execução por caso; não mede variância.
