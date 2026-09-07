# M5B — Restyle visual do que já existe

**Pré-requisito:** M1 a M5 concluídos e commitados. Rodar **antes** do M6.
**Este módulo não muda comportamento.** Nenhuma view, model, form, url ou
migration é tocada. Se algum teste do M10 quebrar depois disso, o restyle
passou onde não devia.

## Contexto
A direção de arte do projeto mudou: o `DESIGN.md` na raiz agora descreve um
**painel de instrumentos de destilaria** — grafite quase preto, cobre como
único metal, filetes de 1px, números em mono tabular, sem sombra em lugar
nenhum. O M1 e o M5 foram construídos na direção anterior (fundo claro,
serifa Bodoni, cards). Este módulo converte o que existe.

**Leia o `DESIGN.md` inteiro antes de começar.** Ele é a fonte; o que segue é
só o roteiro da conversão.

## Escopo

### 1. `base.html` — trocar a fundação
- Substituir o `<link>` do Google Fonts: sai Bodoni Moda, entra
  `Archivo` com eixo de largura (`wdth,wght@100..125,400..700`) e
  `JetBrains Mono` (`wght@400;500`)
- Substituir o bloco `@theme` inteiro pelo do `DESIGN.md` (grafite, aco, vapor,
  nevoa, cobre, filete) e adicionar as classes `.titulo` e `.medida`
- `<body>` em `bg-grafite text-vapor font-corpo`
- Header e footer refeitos: sem sombra, separados por `border-b border-filete`

### 2. Varredura de tokens em todos os templates
Passe por **todos** os arquivos em `templates/` e converta:

| Antigo | Novo |
|---|---|
| `bg-papel` | `bg-grafite` (fundo de página) ou `bg-aco` (superfície elevada) |
| `text-garrafa` | `text-vapor` |
| `bg-garrafa` | `bg-aco` |
| `text-cana`, `border-cana` | `text-nevoa`, `border-filete` |
| `border-barrica`, `bg-barrica` | `border-filete` |
| `font-display` | classe `.titulo` |
| `text-cobre`, `bg-cobre` | mantém — mas revisar a regra de restrição |
| `rounded`, `rounded-md`, `rounded-lg` | `rounded-maquina` (2px) |
| `shadow-*` | **remover.** Sombra não existe neste projeto; virou filete |

Ao final, **grepe** por `papel`, `garrafa`, `barrica`, `cana`, `Bodoni`,
`shadow` e `font-display` nos templates. Zero ocorrências.

### 3. Regra de restrição do cobre
Depois da varredura, o cobre provavelmente está em excesso — ele era acento numa
paleta clara e agora é o único metal num fundo escuro. Revise: **um botão sólido
em cobre por tela, no máximo.** Todo o resto do cobre vira borda de 1px,
sublinhado, item de menu ativo ou número em destaque.

### 4. Herói da home — adicionar a faixa de dados
O elemento que define o projeto e que não existia antes: abaixo do título, uma
linha de leituras em `.medida`, separadas por filete vertical, no formato
`40,2% ABV · 90 min de visita · 3 experiências · 12 vagas/horário`.
Os números vêm do banco onde possível (contagem de experiências ativas,
duração e capacidade), não hardcoded.

Overlay da foto em `grafite` a ~70%, senão o texto não lê.

### 5. Tabela do painel — a conversão mais importante
- Status: **chip com borda de 1px e texto colorido**, fundo `aco`. Não pílula
  preenchida. Cores no `DESIGN.md`
- Separação de linhas por `border-b border-filete`. Nada de card, nada de sombra
- Datas, horários, contadores e IDs em `.medida`, **alinhados à direita**
- Cabeçalho da tabela em `text-nevoa`, 12px
- Estados vazios: ilustração SVG em linha de 1px `cobre`, estilo diagrama
  técnico — não desenho ilustrativo

### 6. Formulário e campos
Campos em `bg-aco`, `border border-filete`, foco com `border-cobre` e
`focus-visible` visível. Nunca `outline:none` sem substituto.

## Fora de escopo
Views, models, forms, urls, migrations, testes. O M6 e os extras vêm depois.

## Critério de aceite
- `python manage.py test` continua verde, sem nenhum teste alterado
- `git diff --stat` mostra mudança **só** em `templates/` e, se necessário,
  `static/` — nenhum `.py` tocado
- Grep por token antigo nos templates retorna vazio
- Nenhum `shadow-` sobrou
- Home e painel abertos em 375px continuam usáveis
- Contraste: `nevoa` não está carregando informação essencial em nenhum lugar

## Commit
Um commit só, isolado: `style: aplica direcao visual de painel de instrumentos`.
Isolado importa por dois motivos: dá pra reverter sem perder lógica, e no
histórico fica legível que houve uma decisão de design deliberada em vez de
mexida solta em template.

## Ao terminar
1. Critique o próprio resultado contra a **anti-lista** do `DESIGN.md`, item por
   item, e diga o que ainda está fora
2. As 5 perguntas da sabatina (regra 3 do `CLAUDE.md`) — aqui elas caem sobre
   decisão visual: por que filete em vez de sombra, por que mono só em medida,
   por que o cobre é restrito
