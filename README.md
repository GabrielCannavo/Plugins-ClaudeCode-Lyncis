# gabriel-local — marketplace de plugins

Marketplace do Claude Code (repositório GitHub
`GabrielCannavo/Plugins-ClaudeCode-Lyncis`) com um único plugin: **lyncis-kit**.
O kit reúne `improve` (refinador de rascunhos de prompts), `encerrar-sessao`,
`revisar-ambiente` e `configurar-projeto` — detalhes em
[`lyncis-kit/README.md`](lyncis-kit/README.md).

## Estrutura

```
Plugins/
├── .claude-plugin/
│   └── marketplace.json          # manifesto do marketplace (gabriel-local)
└── lyncis-kit/                   # o plugin
    ├── .claude-plugin/plugin.json
    ├── commands/improve.md
    ├── skills/
    └── README.md
```

## Instalar

```
/plugin marketplace add GabrielCannavo/Plugins-ClaudeCode-Lyncis
/plugin install lyncis-kit@gabriel-local
```

Uso do improve: `/lyncis-kit:improve <rascunho do prompt>`.

Para atualizar depois de um push: `claude plugin marketplace update gabriel-local`
e `claude plugin update lyncis-kit@gabriel-local` (o `install` não faz upgrade).

## Histórico do improve

> A v1.1.0 consolidou as melhorias de robustez validadas no fork de teste
> `improve2` (aposentado). A v1.2.0 adicionou as seções Anti-padrões e Skills
> sugeridas. A v1.3.0 consolidou o segundo fork `improve2` (discovery
> condicional). A v1.4.0 adicionou o §1.7 (verificação de validade do que foi
> inferido de arquivos do projeto). A v1.5.0 tornou o discovery o caminho padrão.
> A v1.5.1 fixou a sequência de chamada do formulário e a nova tentativa quando
> ele não aparece. A partir da v1.5.1 o improve vive só no `lyncis-kit`; o
> plugin avulso `improve-plugin/` e os instaladores por arquivo
> (`instalar-*-improve.md`) foram removidos.
