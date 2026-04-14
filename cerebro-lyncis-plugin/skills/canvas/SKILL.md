---
name: canvas
description: Cria e edita canvas Obsidian ad-hoc no vault Cérebro Lyncis para referência visual. Suporta canvas new, add image/text/pdf/note, connect, zone, list. Integração com nanobanana para imagens geradas. NÃO toca canvases automáticos gerados pelo garden (Ecossistema, Mapa de Conhecimento). Triggers on: canvas new, canvas add, canvas connect, canvas zone, canvas list, criar canvas, adicionar ao canvas.
---

# Canvas — Referência Visual Ad-Hoc

Camada visual do vault Cérebro Lyncis. Canvas ad-hoc criados manualmente pelo usuário — para exploração, planejamento, mood boards, diagramas de cliente, etc.

**VAULT:** `C:/Users/gabri/OneDrive/Desktop/Cérebro Obsidian/Cérebro Lyncis`

**PASTA DE CANVASES (HARDCODED):**
- Canvas gerais: `{VAULT}/Canvases/`
- Canvas de projetos: `{VAULT}/Canvases/projetos/`
- Canvas de ecossistema (gerado pelo garden — NÃO tocar): `{VAULT}/Canvas — Ecossistema Lyncis.canvas`
- Canvas de conhecimento (gerado pelo garden — NÃO tocar): `{VAULT}/Base de Conhecimento/Canvas — Mapa de Conhecimento.canvas`

Um canvas é um arquivo JSON que o Obsidian renderiza como board visual infinito. Esta skill lê e escreve o JSON do canvas diretamente.

---

## Regra Importante

**NÃO modificar** os canvases automáticos gerados pelo `/cerebro-lyncis:garden`:
- `Canvas — Ecossistema Lyncis.canvas`
- `Base de Conhecimento/Canvas — Mapa de Conhecimento.canvas`

Esta skill manipula apenas canvases **ad-hoc** criados pelo usuário.

---

## Canvas padrão

`{VAULT}/Canvases/main.canvas`

Se não existir, criar:

```json
{
  "nodes": [
    {
      "id": "title",
      "type": "text",
      "text": "# Visual Reference\n\nDrop images, PDFs, and notes here.",
      "x": -400, "y": -300, "width": 400, "height": 120, "color": "6"
    },
    {
      "id": "zone-default",
      "type": "group",
      "label": "Geral",
      "x": -400, "y": -140, "width": 800, "height": 400, "color": "4"
    }
  ],
  "edges": []
}
```

---

## Operações

### status / open (`/cerebro-lyncis:canvas` sem args)

1. Verificar se `{VAULT}/Canvases/main.canvas` existe.
2. Se sim: ler, contar nodes por tipo, listar labels dos grupos (zonas).
   Reportar: "Canvas tem N nodes: X imagens, Y cards de texto, Z notas. Zonas: [lista]"
3. Se não: criar com estrutura acima.
4. Informar usuário: "Abra `Canvases/main.canvas` no Obsidian para visualizar."

---

### new (`canvas new [nome]`)

1. Slugificar o nome: lowercase, espaços→hifens, remover caracteres especiais.
2. Decidir pasta:
   - Sem contexto especial → `{VAULT}/Canvases/[slug].canvas`
   - Relacionado a projeto específico → `{VAULT}/Canvases/projetos/[slug].canvas`
3. Criar canvas com estrutura starter, título atualizado para `# [Nome]`.
4. Reportar: "Criado Canvases/[slug].canvas"

---

### add image (`canvas add image [path ou url]`)

**Resolver a imagem:**
- Se URL (começa com `http`): baixar com `curl -sL [url] -o "{VAULT}/_attachments/images/canvas/[filename]"`
  Derivar filename do path da URL, ou usar `img-[timestamp].jpg` se incerto.
- Se path local fora do vault: `cp [path] "{VAULT}/_attachments/images/canvas/"`
- Se já está no vault: usar como está.

Criar `{VAULT}/_attachments/images/canvas/` se não existir.

**Detectar proporção para dimensionar o node:**

```bash
python3 -c "from PIL import Image; img=Image.open('[path]'); print(img.width, img.height)"
# ou
identify -format '%w %h' [path]
```

Tamanhos canvas por proporção (aproximados):
- Quadrada (1:1) → 400×400
- Paisagem 4:3 → 400×300
- Retrato 3:4 → 300×400
- Wide 16:9 → 480×270
- Ultra-wide → 600×200
- Retrato 9:16 → 270×480

**Posicionar com auto-layout** (ver seção abaixo).

**Appendar node ao JSON do canvas e escrever.**

Reportar: "Adicionado [filename] na zona [zona] em ([x], [y])."

---

### add text (`canvas add text [conteúdo]`)

```json
{
  "id": "text-[timestamp]",
  "type": "text",
  "text": "[conteúdo]",
  "x": [auto], "y": [auto],
  "width": 300, "height": 120,
  "color": "4"
}
```

Posicionar com auto-layout. Escrever e reportar.

---

### add pdf (`canvas add pdf [path]`)

Mesmo fluxo de add image.
- Copiar para `{VAULT}/_attachments/pdfs/canvas/` se fora do vault.
- Tamanho fixo: width=400, height=520.

---

### add note (`canvas add note [nome-da-nota]`)

1. Buscar no vault arquivo correspondente ao nome (case-insensitive, match parcial ok).
2. Usar o path relativo ao vault como campo `file`.
3. `"type": "file"` para notas .md (NÃO usar `"type": "link"` — link é para URLs externas).
4. Tamanho: width=300, height=100.
5. Posicionar com auto-layout.

```json
{
  "id": "note-[timestamp]",
  "type": "file",
  "file": "Projetos/clientes/cliente-aly-adv.md",
  "x": [auto], "y": [auto],
  "width": 300, "height": 100
}
```

---

### zone (`canvas zone [nome] [cor]`)

1. Ler canvas JSON.
2. Calcular `max_y`: `max(node.y + node.height for all nodes) + 60`. Usar 280 se sem nodes.
3. Criar grupo:

```json
{
  "id": "zone-[slug]",
  "type": "group",
  "label": "[nome]",
  "x": -400,
  "y": [max_y],
  "width": 1000,
  "height": 400,
  "color": "[cor ou '3']"
}
```

Cores válidas: `"1"`=vermelho `"2"`=laranja `"3"`=amarelo `"4"`=verde `"5"`=ciano `"6"`=roxo

---

### connect (`canvas connect [canvas] [node-a] [node-b]`)

1. Ler canvas JSON.
2. Verificar que ambos os nodes existem (busca por ID ou por label/filename).
3. Criar edge:

```json
{
  "id": "edge-[timestamp]",
  "fromNode": "[id-de-a]",
  "fromSide": "right",
  "toNode": "[id-de-b]",
  "toSide": "left"
}
```

4. Appendar à lista `"edges"` e escrever.

---

### list (`canvas list`)

1. `Glob("{VAULT}/Canvases/**/*.canvas")` — excluir canvases do garden
2. Para cada canvas: ler JSON, contar nodes por tipo.
3. Reportar:

```
Canvases/main.canvas           14 nodes (8 imagens, 3 texto, 2 notas, 1 grupo)
Canvases/projetos/client-x.canvas  7 nodes (4 texto, 2 notas, 1 grupo)
```

---

## Auto-Posicionamento

```python
def next_position(canvas_nodes, target_zone_label, new_w, new_h):
    # Encontrar grupo-zona
    zone = next((n for n in canvas_nodes
                 if n.get('type') == 'group'
                 and n.get('label') == target_zone_label), None)

    if zone is None:
        # Sem zona: posicionar abaixo de todo conteúdo
        max_y = max((n['y'] + n.get('height', 0) for n in canvas_nodes), default=-140)
        return -400, max_y + 60

    zx, zy = zone['x'], zone['y']
    zw, zh = zone['width'], zone['height']

    # Nodes dentro desta zona
    inside = [n for n in canvas_nodes
              if n.get('type') != 'group'
              and zx <= n['x'] < zx + zw
              and zy <= n['y'] < zy + zh]

    if not inside:
        return zx + 20, zy + 20

    rightmost_x = max(n['x'] + n.get('width', 0) for n in inside)
    next_x = rightmost_x + 40

    if next_x + new_w > zx + zw:
        # Nova linha
        max_row_y = max(n['y'] + n.get('height', 0) for n in inside)
        return zx + 20, max_row_y + 20

    # Mesma linha: alinhar ao topo dos nodes existentes na zona
    current_row_y = min(n['y'] for n in inside)
    return next_x, current_row_y
```

---

## Geração de IDs

Ler o canvas, coletar todos os IDs existentes. Nunca reutilizar.

Padrão seguro: `[tipo]-[slug-conteudo]-[unix-timestamp-10-digitos]`

Exemplos: `img-cover-1744032823`, `text-nota-1744032845`, `zone-clientes-1744032901`

Se colisão detectada: appendar `-2`, `-3`, etc.

---

## Integração com nanobanana

Se o usuário gerou imagens com `/nanobanana` na mesma sessão e diz "adicionar ao canvas":
1. Verificar `{VAULT}/Canvases/.recent-images.txt` (log de imagens recentes da sessão)
2. Se não encontrar: buscar imagens recentes em `{VAULT}/_attachments/images/`
3. Apresentar lista e perguntar qual zona e canvas

Sugerir após qualquer geração de imagem: "Adicionar imagens geradas ao canvas? `/cerebro-lyncis:canvas from banana`"

---

## Regras JSON Canvas

- Sempre ler o canvas antes de escrever — parsear nodes existentes para evitar colisões de ID e calcular posições
- `"type": "file"` para notas .md e PDFs; `"type": "link"` apenas para URLs externas (`url:` field)
- `"type": "text"` para cards de texto (`text:` field)
- `"type": "group"` para zonas (`label:` field)
- Newlines em text nodes: usar `\n` (escape JSON), nunca `\\n` literal
- Path de arquivos: relativo ao vault, sem barra inicial
