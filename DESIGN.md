# DIREÇÃO DE ARTE — vale para todos os módulos de interface

> **Como usar:** este arquivo entra junto com o `00_CONTEXTO.md` na raiz do repo.
> Todo módulo que mexe em template (M1, M3, M4, M5, M6, M8, M9) obedece a ele.
> Não improvisar visual: se algo não está aqui, perguntar.

## O conceito: painel de instrumentos de destilaria

Um alambique é uma fábrica de precisão. Cobre, tubulação, termômetro, curva de
destilação, tempo de fermentação, teor alcoólico medido em décimos. A interface
não é brochura de tradição — é **instrumento de operação**: escuro, filetes
finos, números monoespaçados, leituras de dado onde outros sites põem enfeite.

Essa é a resposta de uma frase se perguntarem por que futurista num produtor
artesanal: *"o alambique é uma planta industrial, e eu tratei o agendamento como
operação medida, não como panfleto."* Sem essa justificativa, o visual vira tema
aplicado por cima — e é isso que o avaliador percebe.

Não é ficção científica. Não tem nave, não tem neon rosa, não tem vidro
borrado. É instrumento: preciso, escuro, legível.

## Tokens

### Cor — escuro, com um único metal
| Nome | Hex | Uso |
|---|---|---|
| `grafite` | `#0E1113` | Fundo de tudo. Quase preto, com viés frio |
| `aco` | `#171B1E` | Superfície elevada: linha de tabela, card, campo de formulário |
| `vapor` | `#E6E7E4` | Texto principal. Branco levemente quente, nunca `#fff` puro |
| `nevoa` | `#78848A` | Texto secundário, labels, meta-informação |
| `cobre` | `#C87A3F` | **A única cor cromática.** Ação primária, item ativo, dado em destaque |

Regra de restrição, e ela é o que segura o visual: **o cobre é filete e brilho
pontual, não preenchimento.** Um botão sólido em cobre por tela, no máximo. O
resto do cobre aparece como borda de 1px, sublinhado ou número em destaque.

Status — chip com borda de 1px e texto colorido, **não** pílula preenchida:
`pendente` `#E0A24E` · `confirmada` `#7FC9A0` · `cancelada` `#D9705F`.
Fundo do chip é `aco`; a cor vive na borda e no texto.

### Tipografia — uma família com eixo de largura, mais uma mono
Via Google Fonts, sem build.

- **Títulos: Archivo em largura expandida** (`wdth` 110–125), peso 600, tracking
  levemente negativo. Fica maquinado e largo — futurista sem cair em Orbitron
  ou Space Grotesk, que são o clichê imediato do gênero.
- **Corpo e interface: Archivo em largura normal** (`wdth` 100). Mesma família,
  então o conjunto tem unidade e você carrega uma fonte só.
- **Números, horários, contadores, IDs: JetBrains Mono.** Tudo que é medida vai
  em mono e com dígitos tabulares. É o detalhe que faz a tela parecer
  instrumento em vez de site.

Escala: `12 · 14 · 16 · 20 · 26 · 34 · 48 · 68` px. Corpo 16/1.6.
Texto corrido com no máximo 70 caracteres por linha.

### Espaçamento e forma
Múltiplos de 4: `4 · 8 · 12 · 16 · 24 · 32 · 48 · 72 · 112`.
**Raio 2px, e nada maior.** Canto vivo é maquinado; canto arredondado é app de
banco. Separação por **filete de 1px** em `#232A2E`, nunca por sombra —
sombra não existe neste projeto.

## Como configurar isso sem build

**Atenção à versão.** O CDN antigo (`cdn.tailwindcss.com`) e o objeto
`tailwind.config` em JavaScript são da v3 e estão descontinuados. Na v4 o CDN é o
*browser build* e a configuração é CSS-first, com `@theme` dentro de um
`<style type="text/tailwindcss">`. Cada variável de tema gera a utilitária
correspondente automaticamente.

No `<head>` do `base.html`:

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@100..125,400..700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
<style type="text/tailwindcss">
  @theme {
    --color-grafite: #0E1113;
    --color-aco:     #171B1E;
    --color-vapor:   #E6E7E4;
    --color-nevoa:   #78848A;
    --color-cobre:   #C87A3F;
    --color-filete:  #232A2E;

    --font-corpo: Archivo, system-ui, sans-serif;
    --font-mono:  "JetBrains Mono", ui-monospace, monospace;

    --radius-maquina: 2px;
  }
  /* largura expandida do Archivo para títulos */
  .titulo { font-family: var(--font-corpo); font-variation-settings: "wdth" 118; letter-spacing: -0.02em; }
  /* dígitos tabulares em toda medida */
  .medida { font-family: var(--font-mono); font-variant-numeric: tabular-nums; }
</style>
```

Com isso existem `bg-grafite`, `text-vapor`, `border-filete`, `text-cobre`,
`rounded-maquina`, mais as classes `.titulo` e `.medida`.

Duas ressalvas, e as duas viram conversa boa na entrevista:
- O browser build é **para desenvolvimento e protótipo**, não produção — lá seria
  CLI ou Vite com purge. O README do teste autoriza CDN explicitamente, então é
  escolha consciente. Registrar no `DECISOES.md`.
- Não conte com `@apply`: depende do pipeline de build.

## Página pública

Herói: foto do alambique de cobre sangrando na tela inteira, escurecida por
overlay em `grafite` a 70%, título grande na classe `.titulo` por cima. Abaixo
do título, **a faixa de dados** — o gesto que define o projeto: uma linha de
leituras em `.medida`, separadas por filete vertical, tipo
`40,2% ABV · 90 min de visita · 3 experiências · 12 vagas/horário`.
Foto baixada para `static/`, sem hotlink.

Seções, poucas e boas, separadas por filete de 1px:
1. Herói com a faixa de dados
2. A casa — texto curto, com um dado medido ao lado (ano de fundação, litros/safra)
3. Como funciona a visita — **numeração 1/2/3 é legítima aqui**, é sequência
   real, e os números vão em `.medida` grande e cobre. Em outra seção, não numerar
4. Experiências — 3 blocos com preço, duração e capacidade em mono
5. Onde fica e quando abre
6. Formulário — campos em `aco`, borda `filete`, foco com borda `cobre`

Alinhamento à esquerda em tudo.

## Painel

É onde o conceito rende mais. Fundo `grafite`, tabela densa, sem card e sem
sombra: só filetes. Números, datas e horários em `.medida`, alinhados à direita.
Cobre no item de menu ativo e na ação primária.

Dois detalhes que aproveitam o tema:
- **Barra de ocupação do horário** — segmentada, fina, em cobre sobre `filete`,
  mostrando quantas vagas do slot estão tomadas. Encaixa direto com o extra do
  M7 e é a peça mais "instrumento" da tela
- **Roteiro de hoje (M8) como painel de embarque** — horários em coluna mono,
  grupos por horário, status em chip. A metáfora do quadro de embarque de
  aeroporto é coerente com o conceito e resolve leitura à distância

**Ressalva honesta sobre o M8:** tela escura sob sol direto reflete mais que tela
clara. Mitigação: contraste máximo (`vapor` sobre `grafite` é a maior razão
possível), tipo grande e alvo de toque grande. Registrar como trade-off assumido
no `DECISOES.md` — não como algo que passou batido.

## Estados vazios
Não são erro, são convite. Uma frase dizendo o que fazer, em `nevoa`, com um
traço de ilustração SVG em linha de 1px `cobre` — um alambique esquemático, tipo
diagrama técnico, não desenho fofo. "Nenhum resultado para esse filtro" e "nada
cadastrado ainda" são textos diferentes.

## Escrita da interface
- Verbo do botão = verbo do resultado: "Reservar visita" → "Visita reservada"
- Sentence case sempre. Sem CAPS em label, sem "→" no fim de botão
- Erro diz o que aconteceu e o que fazer: "Esse horário já está lotado. Restam 4
  lugares às 15h." > "Erro ao agendar."

## Anti-lista: o que NÃO fazer
Futurista tem clichês próprios, e cair neles entrega a tela como gerada — a spec
premia o oposto ("com a sua cara, não a cara de um tutorial"):
- Gradiente roxo-para-azul em qualquer lugar
- Glassmorphism: card translúcido com `backdrop-blur`
- Neon ciano ou verde-ácido brilhando em tudo
- `box-shadow` colorido fazendo glow em botão e card
- Grid de linhas luminosas como fundo decorativo
- Orbitron, Space Grotesk, Michroma, ou qualquer fonte "de nave"
- Layout bento: mosaico de blocos de tamanhos diferentes sem hierarquia real
- Mono em tudo, inclusive texto corrido — mono é só para medida
- `fade-and-slide-up` em cada seção, hover que levanta cada card

## Piso de qualidade (sem anunciar)
Responsivo até 375px · foco de teclado visível em `cobre` (`focus-visible`, nunca
`outline:none`) · contraste conferido: `nevoa` só em texto de apoio, nunca em
informação essencial · `prefers-reduced-motion` respeitado · label associado a
todo input · a interface é escura por design, o que **não** é o mesmo que ter
alternância de tema — não vender como dark mode.

## Movimento
Um momento só, e responde a uma ação: ao mudar o status, a linha da tabela pisca
uma vez com borda em cobre e volta. Nada de animação de entrada pela página.

## Processo obrigatório antes de codar tela
No M1, antes de escrever o `base.html`: apresente o plano visual (paleta em uso,
escala aplicada, wireframe em ASCII do herói com a faixa de dados e da tabela do
painel) e **espere eu aprovar**. Depois de construir, critique o próprio
resultado contra a anti-lista e me diga o que mudaria.
