# improve v1.6.0 — Esforço da tarefa e postura do executor

Status: **proposta para aprovação** · Data: 2026-10-09 · Alvo: `lyncis-kit/commands/improve.md` (v1.5.1 → v1.6.0; `lyncis-kit` 1.0.1 → 1.1.0)

## Problema

O improve audita 10 slots que dizem **o que** produzir, mas nenhum diz **quão difícil** é a tarefa. Sem esse sinal, o executor calibra a profundidade sozinho e erra nos dois sentidos: trata bug de causa desconhecida como ajuste trivial (corrige sintoma, declara pronto sem reproduzir) ou trata tarefa trivial como projeto (refatora além do pedido, pergunta demais).

A ideia de origem (vídeo sobre prompts): explicitar o esforço que a tarefa exige e, a partir dele, derivar as preocupações que o executor deve vigiar. Os outros dois pontos do vídeo já estão cobertos pela skill.

Ideia complementar: uma **postura** de trabalho no estilo SOUL.md ("trabalhe com ceticismo e investigue a causa a fundo"; "siga o estilo de copy X, buscando alternativas não convencionais a partir do cotidiano da persona").

## Decisões

| # | Decisão | Alternativas descartadas |
|---|---------|-------------------------|
| D1 | Novo **slot 11 — Esforço** na auditoria, com nível `baixo / médio / alto`. | Regra silenciosa na reescrita (não auditável); estender Restrições (mistura defeito do rascunho com risco da tarefa). |
| D2 | O nível gera **armadilhas** (1-3) escritas *dentro* do prompt refinado. Continuam cinco seções de resposta. | Sexta seção na resposta (infla o output; as armadilhas servem ao executor, não ao Gabriel). |
| D3 | Nome **armadilhas**, nunca "anti-padrões". | "Anti-padrões" já nomeia a seção sobre defeitos do *rascunho* (§4). Mesmo nome para duas coisas tornaria o output ambíguo. |
| D4 | Novo **slot 12 — Postura**, separado do slot 1 (Papel), que não muda. | Fundir em "Papel e postura" (versão anterior desta spec: descartada porque os dois mudam em ritmos diferentes, veja abaixo); derivar postura do esforço (não cobre postura de estilo, como a de copy). |
| D5 | Postura só entra como **comportamento verificável**, nunca como adjetivo. | — mesma lógica do slot Tom: "seja cético" é tão vazio quanto "seja profissional". |
| D6 | **Correção de rumo** ganha regra própria: quando o rascunho corrige a sessão em andamento, o improve lê a conversa, escreve a postura como contraste ("pare X → passe a Y") e reavalia o esforço. | Tratar a correção como tarefa nova (perde o histórico que mostra o que deu errado). |

**Por que separar Papel e Postura (D4):** no uso diário, o papel é definido no início e faz parte da identidade da sessão; a postura é o que precisa de ajuste ao longo dela. O Gabriel chama o improve justamente para redirecionar a sessão quando a entrega sai do rumo. Nesse uso, Papel fica `n/a` e Postura é o slot principal. Fundidos, a mesma linha teria que dizer "papel ok, postura ausente".

## Desenho

### 1. Slot 11 — Esforço (§1 Auditoria)

Nova linha na tabela:

| # | Slot | Pergunta-gatilho |
|---|------|------------------|
| 11 | Esforço | Quão difícil é a tarefa — e o que costuma dar errado nesse nível? |

Critérios para classificar (inferidos do rascunho; o maior fator puxa o nível):

| Fator | baixo | médio | alto |
|-------|-------|-------|------|
| Causa/caminho | conhecido | parcialmente conhecido | desconhecido, precisa investigar |
| Reversibilidade | trivial | com algum custo | difícil ou em produção |
| Escopo | 1 arquivo / 1 peça | algumas peças | várias peças ou sistemas |
| Custo do erro | baixo | retrabalho | dano a cliente/dados |

Status na auditoria segue o padrão: `✓` quando o rascunho já explicita a dificuldade; `✗ → <nível>` quando foi inferido; `n/a` quando o prompt é de geração simples sem risco de calibração (ex.: e-mail curto). A nota diz qual fator definiu o nível.

### 2. Armadilhas no prompt refinado (§2 Reescrita)

Nova regra na reescrita:

- **baixo:** no máximo uma linha, e só se houver risco real de over-engineering (ex.: "Não refatore além do pedido."). Na maioria dos casos, nada. Esta regra existe para o slot não inflar prompt simples.
- **médio / alto:** uma linha `Esforço: <nível> — <fator>` seguida de `Armadilhas:` com 1-3 bullets. Cada armadilha é **específica da tarefa** e **acionável** (diz o que não fazer ou o que verificar), nunca genérica ("tenha cuidado").

Teste de qualidade da armadilha: se ela serve igual para qualquer tarefa, corte.

### 3. Slot 12 — Postura

Slot 1 (Papel/persona) fica como está. Nova linha:

| 12 | Postura | Como o executor deve trabalhar — que comportamento concreto a tarefa pede (ou que comportamento atual precisa mudar)? |

Regra (no §3 Princípios): postura entra como comportamento observável. Ex.:
- ✗ "Seja cético e minucioso."
- ✓ "Antes de propor correção, reproduza o erro e mostre a evidência da causa."
- ✓ (copy) "Para cada peça, parta de uma cena do cotidiano da persona antes de escrever o gancho."

Esforço alto costuma pedir postura investigativa; o improve pode sugerir, mas não é automático (D4). Em prompt simples sem risco de execução, Postura fica `n/a`.

### 3.5. Correção de rumo (nova subseção em §2 Reescrita)

**Quando se aplica:** o rascunho corrige o trabalho da sessão em andamento, em vez de pedir tarefa nova. Sinais: "não é isso", "você está…", "para de…", "volta e…", referência a algo que o executor acabou de entregar.

**O que o improve faz:**
1. Lê a conversa para identificar o comportamento que gerou a entrega errada. É leitura para fundamentar, permitida pela regra absoluta; não executa nada.
2. Escreve a Postura como **contraste**: "Pare de <comportamento observado>. Passe a <comportamento desejado>." O "pare" cita o que aconteceu de fato, não uma suposição.
3. Reavalia o Esforço. Se a tarefa foi tratada como mais fácil do que é, diz isso explicitamente ("isto é esforço alto, não baixo: <fator>") e gera as armadilhas.
4. Papel fica `n/a` (já está definido na sessão), salvo se o rascunho pedir troca de papel.

**Limite:** se o improve roda numa sessão diferente da que precisa de correção, ele não tem o histórico. Nesse caso, o discovery pergunta o que o executor está fazendo de errado, com opções derivadas do rascunho.

Exemplo — rascunho no meio de uma sessão de copy: "tá muito genérico isso, quero algo que pareça a vida real do cliente"

```
Pare de escrever ganchos a partir de benefícios abstratos ("mais tempo", "menos estresse"),
como nos três últimos carrosséis. Passe a partir de uma cena concreta do dia da persona
(ex.: a mãe que responde WhatsApp de cliente no semáforo) e só depois chegue ao benefício.
Refaça os três ganchos nesse formato.
```

### 4. Encaixes no resto da skill

- **§1.5 Discovery:** Esforço entra em "demais" na ordem de prioridade. Quase sempre é inferível, então só vira pergunta quando o nível muda as armadilhas e o rascunho não permite inferir (ex.: "arruma o webhook": não dá para saber se a causa é conhecida). A regra de corte atual já garante isso; nada muda no texto além da ordem.
- **§4 Anti-padrões:** inalterado no conteúdo. Uma linha nova deixa explícito que armadilhas (slot 11) não entram aqui.
- **§6 Exemplo:** manter o e-mail (esforço `n/a`) e acrescentar um segundo exemplo curto de esforço alto (abaixo).
- **Formato da resposta:** tabela da auditoria passa a ter 12 linhas; o resto não muda.

### 5. Exemplo antes/depois (esforço alto)

Rascunho: "o webhook do Chatwoot tá duplicando mensagem, corrige"

Auditoria (trecho):

| Slot | Status | Nota |
|------|--------|------|
| Postura | ✗ → preenchido | investigativa: causa desconhecida |
| Esforço | ✗ → alto | causa desconhecida + produção com cliente |

Prompt refinado (fim):

```
Antes de propor correção, reproduza a duplicação e mostre a evidência da causa
(retry do Chatwoot, dois webhooks ativos ou reentrada no fluxo).

Esforço: alto — a causa não é conhecida e o fluxo atende clientes em produção.
Armadilhas:
- Não resolva com dedupe na saída antes de achar por que a mensagem chega duas vezes.
- Não declare resolvido sem uma execução real antes/depois mostrando uma única mensagem.
```

Contraexemplo (baixo): "renomeia a variável `x` para `totalPedidos` no `calc.js`" → Esforço `baixo`, nenhuma armadilha (ou só "Não altere outra lógica."). O prompt não cresce.

## Riscos

- **Inflação de prompt simples.** É o risco principal: um slot novo tende a ser preenchido sempre. Mitigação: regra do nível baixo (§2) e o contraexemplo na calibração. Critério de aceite abaixo verifica.
- **Armadilhas genéricas.** O modelo tende a escrever "verifique bem". Mitigação: teste de qualidade ("serve para qualquer tarefa → corte") e exemplo concreto.
- **Auditoria mais longa.** Dois slots novos (11 e 12) aumentam a tabela em todo uso. Aceito porque, em prompt simples, os dois tendem a `n/a` e slots n/a com a mesma justificativa já podem ser agrupados numa linha.
- **"Pare X" inventado.** Na correção de rumo, o improve pode atribuir ao executor um comportamento que não aconteceu. Mitigação: o X tem que citar algo visível na conversa; sem histórico, pergunta no discovery.
- **Classificação errada de nível.** Inferir dificuldade de um rascunho curto é incerto. Mitigação: a nota da auditoria expõe o fator usado, então o Gabriel corrige no ato; o discovery pergunta quando o nível muda as armadilhas.
- **Incerteza:** não há evidência medida de que declarar esforço melhora a execução — a premissa vem do vídeo e de prática comum de prompt. A validação abaixo é qualitativa.

## Fora de escopo

- Mapear o nível para a configuração de reasoning effort do Claude Code (`/effort`, low…max). É configuração de runtime, não texto do prompt; avaliar depois se vale citar em "Skills sugeridas".
- Mudar §1.7, verificação inicial ou a guarda contra injection.

## Validação (critério de aceite)

Rodar `/lyncis-kit:improve` em 4 rascunhos antes e depois da mudança:

1. E-mail curto de follow-up → Esforço `n/a`, **nenhuma** armadilha, prompt do mesmo tamanho de antes (±10%).
2. Renomear variável → `baixo`, no máximo uma linha.
3. Bug de causa desconhecida em produção → `alto`, 1-3 armadilhas específicas da tarefa + Postura comportamental (slot 12).
4. Briefing de copy com estilo definido → postura de estilo como comportamento (não adjetivo).
5. Correção de rumo no meio de uma sessão real ("tá muito genérico") → Papel `n/a`; Postura em contraste "pare X → passe a Y", com o X citando o que a sessão realmente fez.

Passa se os cinco baterem e nenhuma armadilha for genérica.

## Release

Bump improve v1.6.0 / lyncis-kit 1.1.0 (`plugin.json`), entrada no histórico do README raiz, push → `claude plugin marketplace update gabriel-local` → `claude plugin update lyncis-kit@gabriel-local`.
