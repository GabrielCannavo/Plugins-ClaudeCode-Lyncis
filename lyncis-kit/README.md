# lyncis-kit

Plugin pessoal com quatro peças que trabalham juntas no ciclo de vida de um
projeto no Claude Code / Cowork.

| Peça | Tipo | Quando | Invocação |
|---|---|---|---|
| `improve` | comando | Refinar um rascunho de prompt antes de usar | `/lyncis-kit:improve <rascunho>` |
| `configurar-projeto` | skill | Uma vez, no início do projeto (ou em projeto sem CLAUDE.md) | "configura esse projeto" |
| `encerrar-sessao` | skill | Fim de toda sessão | "encerra a sessão", "fecha aí" |
| `revisar-ambiente` | skill | Quando a `encerrar-sessao` sugerir, ou sob demanda | "revisa o ambiente" |

## Como as três skills se conectam

```
configurar-projeto ──grava──▶ CLAUDE.md (bloco <!-- ambiente:contrato -->)
                              .claude/settings.json
                              .claude/ambiente-log.md (zerado)

encerrar-sessao ──lê──▶ contrato (fonte de normas)
                ──grava──▶ .claude/handoff.md   (sobrescrito por sessão)
                ──grava──▶ .claude/ambiente-log.md (acumula evidência + contador)
                ──sugere──▶ revisar-ambiente quando:
                            ≥3 observações novas desde a última revisão, OU
                            alguma observação que voltou a ocorrer (2+ sessões), OU
                            5 encerramentos desde a última revisão

revisar-ambiente ──lê──▶ log + contrato + settings
                 ──propõe──▶ diffs com evidência (gate)
                 ──fecha──▶ log (tratadas, expiradas, contador zerado)
```

Regra comum às três: **nada é escrito no projeto sem aprovação item a item.**
As únicas escritas mecânicas são `handoff.md` e `ambiente-log.md`, ambos locais
e não versionados.

## Arquivos que o kit cria no projeto

| Arquivo | Quem cria | Versionado? |
|---|---|---|
| `CLAUDE.md` (com bloco de contrato) | `configurar-projeto` | sim |
| `.claude/settings.json` | `configurar-projeto` | sim |
| `.claude/handoff.md` | `encerrar-sessao` | não |
| `.claude/ambiente-log.md` | `encerrar-sessao` / `configurar-projeto` | não |

## Instalação e atualização automática

O kit é distribuído pelo marketplace `gabriel-local`, no repositório
`GabrielCannavo/Plugins-ClaudeCode-Lyncis`. Instalar a partir do repositório (e
não de um arquivo `.plugin`) é o que permite atualização sem reinstalar.

**Claude Code:**

```
/plugin marketplace add GabrielCannavo/Plugins-ClaudeCode-Lyncis
/plugin install lyncis-kit@gabriel-local
```

Depois: `/plugin` > Marketplaces > `gabriel-local` > **Enable auto-update**
(vem desligado para marketplaces de terceiros).

**Cowork / app desktop:** Customize > Plugins > Add > Add marketplace, com a URL
do repositório; ligar **Sync automatically** ou usar **Check for updates**. Se
o repositório for privado, é preciso dar acesso à GitHub App da Claude.

### Regra de release

O campo `version` do `.claude-plugin/plugin.json` é o que as máquinas comparam.
**Push sem subir a versão não chega a ninguém.** Isso é proposital: commit de
rascunho não vira atualização. Para publicar: subir `version` no `plugin.json`,
registrar no changelog abaixo, commit e push. A versão fica **só** no
`plugin.json` — a entrada no `marketplace.json` não declara `version`, porque
quando os dois existem o `plugin.json` vence sem aviso e os números divergem.

## Migração

Este plugin substitui o plugin `improve` avulso e a skill `encerrar-sessao`
instalada separadamente. Desinstale os dois antes de usar o kit para não ter
duas versões disputando o mesmo gatilho. A invocação do improve muda de
`/improve:improve` para `/lyncis-kit:improve`.

## Changelog

### v1.0.0

- Consolida `improve` v1.5.0 (sem alteração de conteúdo) e `encerrar-sessao`.
- `encerrar-sessao`: novo log de ambiente acumulativo (`.claude/ambiente-log.md`)
  com contador idempotente por sessão; gatilho híbrido para sugerir
  `revisar-ambiente`; estágio 4 passa a propor diff contra a fonte de skills de
  plugin com marketplace local, em vez de só registrar observação.
- Nova skill `revisar-ambiente`: verificações factuais F1–F7 + evidência
  recorrente do log; não cria hook, não amplia permissão para segredos, não
  edita SKILL.md.
- Nova skill `configurar-projeto`: inventário, descoberta, CLAUDE.md ≤ 80 linhas
  com contrato do ambiente, governança mínima, modo adoção para projeto com
  CLAUDE.md existente.
