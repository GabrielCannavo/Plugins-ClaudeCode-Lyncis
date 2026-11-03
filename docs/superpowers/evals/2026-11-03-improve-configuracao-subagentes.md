# Eval — improve v1.7.0 (Configuração sugerida, slot Subagentes)

Data: 2026-11-03 · Método: subagentes (Sonnet) simulam o comando sem visualize, discovery tratado como pulado, sobre rascunhos fixos fora dos exemplos da skill. Ambiente simulado: Claude Code com Opus/Sonnet/Haiku 5.5 e lista fixa de subagentes instalados (casos 1-3); Codex sem lista de modelos nem de subagentes (caso 4). Os subagentes não conheciam os critérios.

| # | Rascunho | Configuração sugerida | Subagentes | Critério | Resultado |
|---|----------|-----------------------|------------|----------|-----------|
| 1 | E-mail de follow-up já especificado | `Haiku 5.5 · esforço baixo` | n/a | prompt não incha; config fora do prompt | ✓ |
| 2 | Comparar 6 sites de concorrentes | `Sonnet 5.5 · esforço médio`, diz quando subir | sim — `web-fetch`, um por site | só subagentes instalados; justifica médio com subagentes | ✓ |
| 3 | Agente WhatsApp não responde áudio (produção) | `Opus 5.5 · esforço alto` | sim — `n8n-workflow-auditor` como segundo olhar | alto com armadilhas; subagente real e justificado | ✓ |
| 4 | Refatorar módulo de comissão, rodando no Codex | "modelo depende do host" · esforço médio | não | nenhum modelo Claude; não inventa subagente | ✓ |

Em todos os casos a resposta teve seis seções e a Configuração sugerida não vazou para dentro do prompt refinado.

## Ressalvas

- Caso 2: a justificativa para esforço médio com subagentes foi "leituras paralelas simples" — aceitável pela regra, mas mostra que a régua (subagentes → alto) é só tendência.
- A régua de esforço segue sendo heurística do usuário, não validada contra a documentação do esforço.
- Eval qualitativa, uma execução por caso, sem o formulário real do discovery; não mede variância.
