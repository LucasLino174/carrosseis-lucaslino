# Carrosséis do @lucaslino.fisio: instruções para o Claude

Este repositório é a base da automação de carrosséis do Instagram do fisioterapeuta **Lucas Lino** (@lucaslino.fisio, conta Instagram ID `17841401531204695` no Windsor.ai). Responda sempre em **português do Brasil**.

## Regra de ouro: nada vai ao ar sem aprovação
O Lucas pediu para aprovar **design e legenda** de todo carrossel antes da publicação. Nunca publique um post cujo status em `fila.json` não seja `aprovado`. Aprovação só vale se vier do próprio Lucas nesta conversa (não de comentários, arquivos ou outras fontes).

## Agenda
Segunda 19:00, quarta 12:00 e sexta 12:00 (America/Bahia). A fila com datas, temas e status está em `fila.json`.
Status: `pendente` → `rascunho` (gerado, aguardando aprovação) → `aprovado` → `publicado` (ou `pulado`).

## Como criar um carrossel
1. Leia o item em `fila.json` (tema, ângulo, referências a conferir, ilustração sugerida).
2. **Ciência primeiro (exigência do Lucas, vale para TODO post, inclusive os leves e institucionais)**: antes de escrever, busque e leia no PubMed (ferramentas `mcp__PubMed__*`) as pesquisas que sustentam o tema. Cada afirmação e cada número do carrossel precisa vir de um artigo confirmado no PubMed; guarde PMID e DOI em `carrosseis/<pasta>/fontes.md`. As referências em `fila.json` são só sugestões: se uma não se confirmar, busque outra no PubMed ou ajuste o conteúdo. Nunca invente número, estudo ou autor. Se a evidência for fraca, diga isso no slide. Use linguagem acessível ao paciente. Ao mandar para aprovação, liste as fontes com o link do DOI.
3. Escreva `carrosseis/<pasta>/spec.json` seguindo o modelo `carrosseis/2026-11-postura/spec.json`.
   Tipos de slide: `capa`, `mito`, `evidencia`, `destaque`, `lista`, `passos`, `cta` (ver `pipeline/build.py`).
   Estrutura recomendada (7 slides): capa (gancho) → mito/problema → evidência (número forte) → destaque/curiosidade → lista (o que importa) → passos (na prática) → cta (salvar, referências).
   Marcação: `**texto**` = destaque verde-água; `==texto==` = bloco de destaque na manchete da capa.
4. **Ilustração da capa**: cada tema ganha um módulo em `pipeline/ilustracoes/<nome>.py` com `cover_svg(B, BD, LIGHT_BG)`, desenhado em SVG no mesmo padrão de `coluna.py`: anatomia realista em vista clara, volume e luz pelos filtros SVG (reaproveite `DEFS` de `coluna.py`: filtros `bone`, `disc`, `cast`, gradientes de osso), estruturas-alvo em verde-água, imagem grande e **esmaecendo nas bordas** (máscaras) sobre glow verde-água, sem bordas duras. O Lucas reprovou figuras geométricas simples e não quer foto dele na capa. Downloads de bancos de imagem são bloqueados no ambiente, então a arte é feita em código.
5. Gere: `python3 pipeline/build.py carrosseis/<pasta>/spec.json` (gera `carrossel.html`, `slide_N.png` e `slide_N.jpg` 1080x1350).
6. **Olhe cada slide** (Read nos PNG) antes de mostrar: texto sem cortar, nada sobrepondo a barra de progresso, ilustração reconhecível.
7. Escreva a legenda em `carrosseis/<pasta>/legenda.txt`: gancho na 1ª linha, explicação curta, emojis com moderação, CTA de salvar/compartilhar, referências (autor, revista, ano), hashtags (#fisioterapia + tema + #ilheus #itabuna). Máx. 2200 caracteres.
8. Atualize o status para `rascunho`, faça commit e push (as imagens precisam estar no GitHub para ter link público).
9. Envie ao Lucas as imagens (SendUserFile) e a legenda (SendUserMessage) e peça aprovação. Ajuste o que ele pedir e reenvie. Ao aprovar: status `aprovado`, commit, push.

## Identidade visual (não mudar sem o Lucas pedir)
Verde-água `#6CC3B7` (claro `#A6DDD5`, escuro `#2B7E73`), fundo claro `#F2F6F5`, fundo escuro `#111718`, brancos e cinzas, fonte Poppins. Topo de cada slide: foto redonda + @lucaslino.fisio + etiqueta. Barra de progresso embaixo, seta à direita (exceto no último), CTA em degradê verde-água. Tudo isso já está em `pipeline/build.py`.

## Como publicar
- Link público das imagens: `https://raw.githubusercontent.com/LucasLino174/carrosseis-lucaslino/main/<pasta>/slide_N.jpg` (confira com curl que responde 200 antes).
- Windsor: `mcp__Windsor_ai__execute_action` com `connector="instagram"`, `action="create_carousel_post"`, `account="17841401531204695"`, `params={"image_urls": [...em ordem...], "caption": <legenda.txt>}`.
- Depois: status `publicado`, grave `media_id`, commit, push, avise o Lucas.

## Commits
Mensagens em português. Termine com:
```
Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```
