---
name: ingest
description: Ingere PDFs, URLs, imagens e transcripts no vault Cérebro Lyncis. Faz delta tracking para evitar re-processamento, cross-referencia com vault existente, cria notas no formato Lyncis e atualiza _context.md e _hot-cache.md. Triggers on: ingest, processar fonte, adicionar ao vault, ler e arquivar, ingerir url, ingerir pdf, ingerir imagem, ingerir transcript.
---

# Ingest — Ingestão de Fontes Externas

Lê a fonte, extrai entidades e conceitos, cria notas no formato Lyncis, cross-referencia com o vault existente, e registra tudo. Uma fonte típica toca 3-8 páginas do vault.

**VAULT:** `C:/Users/gabri/OneDrive/Desktop/Cérebro Obsidian/Cérebro Lyncis`

---

## Destino por Tipo (HARDCODED)

| Tipo de fonte | Pasta de destino |
|---------------|-----------------|
| PDFs técnicos | `Base de Conhecimento/fontes-externas/pdfs/` |
| Artigos web | `Base de Conhecimento/fontes-externas/artigos/` |
| Transcripts (vídeos, podcasts, reuniões) | `Base de Conhecimento/fontes-externas/transcripts/` |
| Imagens (capturas, infográficos, diagramas) | `Base de Conhecimento/fontes-externas/imagens/` |

Criar as pastas se não existirem.

---

## Delta Tracking

Antes de ingerir qualquer fonte, verificar o manifest para evitar re-processamento.

**Manifest path:** `Base de Conhecimento/fontes-externas/.manifest.json`

**Formato:**
```json
{
  "sources": {
    "Base de Conhecimento/fontes-externas/artigos/artigo-slug-2026-04-08.md": {
      "hash": "abc123def456",
      "ingested_at": "2026-04-08",
      "pages_created": ["Base de Conhecimento/ferramentas/ferramenta-x.md"],
      "pages_updated": ["Base de Conhecimento/_inbox-aprendizados.md"]
    }
  }
}
```

**Fluxo de verificação:**
1. Verificar se `.manifest.json` existe: `[ -f "{VAULT}/Base de Conhecimento/fontes-externas/.manifest.json" ]`
2. Para fontes locais (arquivo): computar hash SHA256 — `sha256sum [arquivo] | cut -d' ' -f1` (Linux/Mac) ou `certutil -hashfile [arquivo] SHA256` (Windows)
3. Para URLs: usar a URL como chave, sem hash (conteúdo pode mudar)
4. Se hash/URL já existe no manifest → reportar "Já ingerido. Usar 'force' para re-ingerir." e parar
5. Se não existe → prosseguir

Pular delta checking se usuário diz "force ingest" ou "re-ingerir".

---

## Utility: defuddle (embutida)

Para limpeza de conteúdo web antes de ingerir URLs.

**Verificar se está instalado:**
```bash
which defuddle 2>/dev/null || echo "não instalado"
```

**Se não instalado — instruir o usuário:**
```bash
npm install -g defuddle-cli
# Verificar: defuddle --version
```

**Uso para limpar URL:**
```bash
defuddle https://exemplo.com/artigo
# Salvar saída:
defuddle https://exemplo.com/artigo > "/caminho/para/artigo-slug-$(date +%Y-%m-%d).md"
```

**Fallback:** Se defuddle não estiver instalado, usar WebFetch diretamente. O conteúdo será menos limpo mas funcional. Salvar 40-60% de tokens com defuddle quando disponível.

---

## Fluxo de Ingestão

### i. Detectar Tipo

| Entrada | Tipo detectado |
|---------|---------------|
| URL começando com `https://` | Artigo web |
| Arquivo `.pdf` | PDF técnico |
| Arquivo `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, `.svg`, `.avif` | Imagem |
| Arquivo `.md`, `.txt` ou conteúdo colado de vídeo/reunião | Transcript |

### ii. URLs — Fetch e Limpeza

1. Verificar defuddle disponível
2. Se disponível: `defuddle [url]` → conteúdo limpo
3. Se não disponível: WebFetch → conteúdo raw
4. Derivar slug da URL (último segmento do path, lowercase, espaços→hifens, remover query strings)
5. Salvar em `{VAULT}/Base de Conhecimento/fontes-externas/artigos/[slug]-[YYYY-MM-DD].md` com frontmatter:
```yaml
---
tipo: recurso
categoria: fonte-externa
subtipo: artigo
source_url: [url]
data-criacao: YYYY-MM-DD
data-atualizacao: YYYY-MM-DD
tags: [fonte-externa, artigo]
---
```

### iii. PDFs

1. Ler o arquivo PDF com Read tool
2. Extrair texto completo
3. Salvar em `{VAULT}/Base de Conhecimento/fontes-externas/pdfs/[slug]-[YYYY-MM-DD].md`
4. Copiar o PDF original para `{VAULT}/Base de Conhecimento/fontes-externas/pdfs/[slug].[ext]` se não estiver no vault

### iv. Imagens

1. Ler a imagem com Read tool (Claude processa imagens nativamente)
2. Descrever conteúdo: extrair todo texto (OCR), identificar conceitos, entidades, diagramas, dados visíveis
3. Salvar descrição em `{VAULT}/Base de Conhecimento/fontes-externas/imagens/[slug]-[YYYY-MM-DD].md`
4. Frontmatter inclui `subtipo: imagem` e `original_file: [path original]`

### v. Extrair Entidades e Conceitos

Para cada fonte, identificar:
- **Pessoas** (especialistas, autores, personagens relevantes)
- **Ferramentas e plataformas** (cruzar com `Base de Conhecimento/ferramentas/`)
- **Conceitos e frameworks** (cruzar com `Base de Conhecimento/frameworks/` e sínteses)
- **Dados e métricas** relevantes para Lyncis (tráfego pago, IA, automação)

Cross-reference com vault existente:
```bash
# Buscar entidade existente (ex: "n8n")
grep -r "n8n" "{VAULT}/Base de Conhecimento/" --include="*.md" -l
```

Ou via MCP: `obsidian_simple_search` com o nome da entidade.

### vi. Criar/Atualizar Notas no Vault

**Para cada entidade nova** — criar nota usando frontmatter Lyncis:
```yaml
---
titulo: [Nome da Entidade]
tipo: recurso
categoria: ferramenta | framework | conceito
tags: [recurso, fonte-externa]
data-criacao: YYYY-MM-DD
data-atualizacao: YYYY-MM-DD
---
```

**Para entidades existentes** — appendar nova informação sob seção datada:
```markdown
## [YYYY-MM-DD] — Via [slug da fonte]
[nova informação]
_Fonte: [[artigo-slug]]_
```

**NÃO sobrescrever conteúdo existente** — sempre appendar.

### vii. Contradições

Se nova informação conflita com afirmação existente numa nota do vault:
```markdown
> [!question] Possível conflito com [[nota-existente]]
> Esta fonte diz X. A nota [[nota-existente]] afirma Y.
> Verificar qual é mais recente e mais confiável antes de resolver.
```

Adicionar o callout tanto na nota nova quanto na nota existente. Não sobrescrever silenciosamente.

### viii. Appendar ao _inbox-aprendizados.md

Para aprendizados técnicos extraídos da fonte (máx 3 por ingestão para não sobrecarregar):

Path: `{VAULT}/Base de Conhecimento/_inbox-aprendizados.md`

```markdown
---
### [Título do Aprendizado] ^[slug]
<!-- meta: data=YYYY-MM-DD | origem=[[artigo-slug]] | confianca=provável | tags=tag1,tag2 -->

[Conteúdo — 2-4 frases]

**Quando usar:** [contexto]

**Conexões:** [[ferramenta-xxx]], [[conceito-yyy]]
```

**NÃO criar arquivos individuais `aprendizado-*.md`.**

### ix. Atualizar _context.md e _hot-cache.md

Após ingestão:
1. Atualizar `_context.md` da pasta de destino (adicionar entrada para a nova nota)
2. Atualizar `_hot-cache.md` na raiz do vault (appendar uma linha no bloco de ingestões recentes)

### x. Atualizar Manifest

Após processar com sucesso:
```json
{
  "path_ou_url": {
    "hash": "[sha256 ou url]",
    "ingested_at": "YYYY-MM-DD",
    "pages_created": ["lista das novas notas criadas"],
    "pages_updated": ["lista das notas atualizadas"]
  }
}
```

---

## Ingestão em Lote

Se o usuário passa múltiplos arquivos ou diz "ingerir todos":

1. Listar todas as fontes a processar. Confirmar com usuário antes de iniciar.
2. Processar cada fonte seguindo o fluxo acima. Deferir cross-referencing entre fontes para o passo 3.
3. Após todas: fazer um passe de cross-reference entre as fontes recém-ingeridas.
4. Atualizar `_context.md`, `_hot-cache.md` e manifest uma vez no final.
5. Reportar: "Processadas N fontes. Criadas X notas, atualizadas Y notas."

---

## O que NÃO fazer

- Não modificar fontes originais após salvar
- Não criar notas duplicadas — verificar vault antes de criar
- Não sobrescrever afirmações existentes — appendar e flaggar contradições
- Não assumir que defuddle está instalado — verificar e instruir instalação se necessário
- Não criar arquivos individuais `aprendizado-*.md` — usar o inbox
- Não ingerir sem atualizar o manifest no final
