# cerebro-lyncis

Plugin Claude Code pessoal para o vault Obsidian **Cérebro Lyncis** de Gabriel (Lyncis — gestão de tráfego pago + assistentes IA).

Substitui o plugin `claude-obsidian` com skills hardcoded para este vault específico.

## Skills disponíveis

| Skill | Invocação | Descrição |
|-------|-----------|-----------|
| query | `/cerebro-lyncis:query` | Consulta o vault com modos quick/standard/deep. Ponto de entrada padrão para qualquer pergunta Lyncis. |
| distill | `/cerebro-lyncis:distill` | Destila a sessão atual em unidades atômicas de conhecimento e grava no vault + memory. |
| garden | `/cerebro-lyncis:garden` | Manutenção diária do vault: audit, cleanup, integração de inbox, sínteses, visualização, hot cache. |
| ingest | `/cerebro-lyncis:ingest` | Ingere PDFs, URLs, imagens e transcripts no vault com delta tracking e cross-reference. |
| canvas | `/cerebro-lyncis:canvas` | Cria e edita canvas Obsidian ad-hoc para referência visual. |
| research | `/cerebro-lyncis:research` | Loop autônomo de pesquisa iterativa sobre um tópico, salvando tudo no vault. |
| md-reference | `/cerebro-lyncis:md-reference` | Referência de sintaxe Obsidian Flavored Markdown. |
| bases | `/cerebro-lyncis:bases` | Cria e edita arquivos `.base` para views dinâmicas no vault. |

## Desenvolvimento

```bash
# Testar localmente
claude --plugin-dir "C:/Users/gabri/OneDrive/Desktop/Projetos Antigravity/Plugins/cerebro-lyncis-plugin"

# Após mudanças nas skills
/reload-plugins
```

## Pré-requisitos

- Vault path: `C:/Users/gabri/OneDrive/Desktop/Cérebro Obsidian/Cérebro Lyncis/`
- MCP `obsidian-vault` configurado no Claude Code (já está)
- Obsidian aberto para operações de escrita via MCP
