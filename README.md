# gabriel-local — marketplace de plugins

Marketplace local do Claude Code com o plugin **improve**: um refinador de
rascunhos de prompts. Devolve cinco seções — auditoria de 10 slots, anti-padrões
detectados, prompt refinado pronto para colar, skills sugeridas e as mudanças
principais. Por padrão faz antes uma rodada de discovery e só então refina; pula
as perguntas apenas quando o rascunho não tem lacuna relevante nem ambiguidade.

## Estrutura

```
Plugins/
├── .claude-plugin/
│   └── marketplace.json          # manifesto do marketplace (gabriel-local)
├── improve-plugin/               # o plugin improve (v1.5.0)
│   ├── .claude-plugin/plugin.json
│   ├── commands/improve.md
│   └── README.md
├── instalar-skill-improve.md     # arquivo distribuível — formato Skill
└── instalar-comando-improve.md   # arquivo distribuível — formato comando/plugin
```

> Histórico: o `improve` v1.1.0 consolidou as melhorias de robustez que foram
> validadas no fork de teste `improve2` (aposentado). A v1.2.0 adicionou as seções
> Anti-padrões e Skills sugeridas. A v1.3.0 consolidou o segundo fork `improve2`
> (discovery condicional), também aposentado. A v1.4.0 adicionou o §1.7 (verificação de validade do que foi inferido de arquivos do projeto). A v1.5.0 tornou o discovery o caminho padrão. A v1.5.1 (instaladores e `lyncis-kit`) fixa a sequência de chamada do formulário e tenta renderizar de novo quando ele não aparece.

## Instalar localmente (Claude Code)

```
/plugin marketplace add <caminho-desta-pasta>
/plugin install improve@gabriel-local
```

Uso: `/improve <rascunho do prompt>`
(ex.: `/improve escreve um post sobre vendas`).

## Distribuir para outras pessoas

Há dois arquivos prontos para enviar. A pessoa **anexa o arquivo no Claude dela e
diz "instale essa skill para mim"** — o Claude segue as instruções de instalação
embutidas no próprio arquivo. Escolha **um** formato conforme o Claude que a
pessoa usa:

| Enviar este arquivo | Quando | Como fica o disparo |
|---------------------|--------|---------------------|
| `instalar-skill-improve.md` | Claude com **Skills** (Cowork / app desktop) | Automático — ativa quando a pessoa pede para "melhorar/refinar um prompt" |
| `instalar-comando-improve.md` | **Claude Code** (suporte a plugin/slash command) | Explícito — a pessoa chama `/improve <rascunho>` |

Não precisa enviar os dois; cada um instala a mesma lógica de forma independente.

### Limites honestos da distribuição por arquivo

- No **claude.ai comum (chat web sem Skills)** não há onde instalar de forma
  persistente. Nesse caso o próprio arquivo instrui o Claude a adotar o
  comportamento **apenas naquela conversa** (não fica salvo).
- Para distribuição persistente e versionada de verdade, o caminho mais robusto é
  publicar este marketplace num repositório Git (ex.: GitHub) e a pessoa rodar
  `/plugin marketplace add <url-do-repo>` + `/plugin install improve@gabriel-local`.

## Versão

`improve` **v1.5.0** — resposta em cinco seções (Auditoria → Anti-padrões →
Prompt refinado → Skills sugeridas → Mudanças principais), precedida por padrão de
uma rodada de **discovery**: perguntas objetivas (widget de formulário quando
disponível, senão texto numerado), sem teto fixo, só as que mudam o resultado. Pula
o discovery apenas com zero slots ✗ relevantes e zero ambiguidade de interpretação.
Inclui, desde a v1.1.0,
guarda contra injection (breakout de `</draft>`), tratamento de rascunho vazio,
regra de idioma, curto-circuito para "rascunho já está claro", exemplo de
calibração inline e agrupamento de slots n/a.
