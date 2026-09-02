# improve2 — fork de teste (discovery condicional)

Fork do `improve` v1.2.0 para validar um estágio de **discovery** antes da reescrita.

**O que muda:** após a auditoria de slots, se restarem ≥2 slots ✗ não inferíveis,
o comando faz **uma** rodada de até 4 perguntas (elicitation widget; fallback em
texto numerado), pausa, e só produz as cinco seções depois das respostas.
Com ≤1 slot ✗ o comportamento é idêntico ao `improve`.

**Risco assumido (decisão 2026-09-02):** rascunhos curtos quase sempre têm 3-4 ✗,
então o discovery vai disparar na maioria das invocações. Se virar fricção, subir
o gatilho para ≥3 ou restringir aos 4 slots prioritários.

Uso: `/improve2 <rascunho do prompt>`

Ao validar (5-6 usos reais): copiar `commands/improve2.md` sobre
`improve-plugin/commands/improve.md` (trocando `/improve2` → `/improve` e o
prefixo `(TESTE)` da description), bump para 1.3.0, remover este plugin.
