# DIREÇÃO DE ARTE — vale para todos os módulos de interface

> **Como usar:** este arquivo entra junto com o `00_CONTEXTO.md` na raiz do repo.
> Todo módulo que mexe em template (M1, M3, M4, M5, M6, M8, M9) obedece a ele.
> Não improvisar visual: se algo não está aqui, perguntar.

## O ponto de partida

O projeto não vai parecer bem feito por ter framework de frontend. Vai parecer
bem feito por ter **paleta decidida, tipografia decidida e escala de espaçamento
consistente**. É isso que separa uma tela profissional de uma tela de tutorial —
e nada disso exige build.

Toda a personalidade vem do assunto: **alambique de cachaça artesanal no norte de
Minas**. Cobre, cana, barrica de madeira, rótulo impresso, luz seca do sertão.

## Tokens

### Cor — 5 valores, nomeados
| Nome | Hex | Uso |
|---|---|---|
| `garrafa` | `#16241E` | Verde-vidro quase preto. Texto principal e superfícies escuras |
| `papel` | `#E8E9E1` | Off-white levemente esverdeado. Fundo de tudo |
| `cobre` | `#A8642A` | **A cor forte, e é a única.** Ação primária, o alambique, o destaque |
| `cana` | `#7C8F5A` | Verde de folha de cana, dessaturado. Apoio, bordas, ícones |
| `barrica` | `#6B4A2E` | Marrom de madeira. Filetes e divisores |

Regra de restrição: **o cobre aparece pouco.** Se tudo é cobre, nada é. Um botão
primário por tela, e o resto em `garrafa` sobre `papel`.

Status (badges) — semântica, não decoração:
`pendente` fundo `#F0E4CE` texto `#7A5518` · `confirmada` fundo `#DDE5CE` texto
`#3F5426` · `cancelada` fundo `#EFDAD5` texto `#8A3B2A`.

### Tipografia — duas famílias, via Google Fonts (CDN, sem build)
- **Display: Bodoni Moda.** Serifa de alto contraste, da tradição do rótulo
  gravado de destilado. Não é o Playfair de sempre, e a escolha tem motivo
  ligado ao assunto: rótulo de garrafa. Usar em tamanho grande, peso 400–600,
  `letter-spacing` levemente negativo. Só em títulos.
- **Texto e interface: Archivo.** Grotesca ligeiramente condensada, boa em
  tamanho pequeno, ótima em tabela densa. Corpo, labels, botões, painel.

Escala: `12 · 14 · 16 · 20 · 26 · 34 · 46 · 62` px. Corpo em 16/1.6.
Linha de texto corrido com no máximo 70 caracteres.

### Espaçamento
Múltiplos de 4, usando só: `4 · 8 · 12 · 16 · 24 · 32 · 48 · 72 · 112`.
Raio de borda: **2px em quase tudo** (cara de rótulo impresso, não de app),
e `9999px` só nas badges. Nada de raio grande e uniforme em tudo.

## Como configurar isso sem build

**Atenção à versão.** O Tailwind v4 mudou isso completamente. O CDN antigo
(`cdn.tailwindcss.com`) e o objeto `tailwind.config` em JavaScript são da v3 e
estão descontinuados. Na v4 o CDN é o *browser build* e a configuração é
CSS-first, com a diretiva `@theme` dentro de um `<style type="text/tailwindcss">`.
Cada variável de tema gera a utilitária correspondente automaticamente.

No `<head>` do `base.html`:

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:opsz,wght@6..96,400..600&family=Archivo:wght@400;500;600&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
<style type="text/tailwindcss">
  @theme {
    --color-garrafa: #16241E;
    --color-papel:   #E8E9E1;
    --color-cobre:   #A8642A;
    --color-cana:    #7C8F5A;
    --color-barrica: #6B4A2E;

    --font-display: "Bodoni Moda", serif;
    --font-corpo:   Archivo, system-ui, sans-serif;

    --radius-rotulo: 2px;
  }
</style>
```

Com isso, `bg-papel`, `text-garrafa`, `font-display` e `rounded-rotulo` passam a
existir como classe. **É esse trecho que faz o projeto ter identidade em vez de
cinza padrão.**

Duas ressalvas técnicas, e as duas viram conversa boa na entrevista:
- O browser build é **para desenvolvimento e protótipo**, não para produção — em
  produção seria CLI ou Vite, com purge. O README do teste autoriza CDN
  explicitamente, então a escolha é consciente, não desconhecimento. Registrar
  no `DECISOES.md`.
- Não conte com `@apply` aqui: ele depende do pipeline de build. Composição é
  por classe utilitária no HTML.

## Página pública

O herói abre com o mais característico do assunto: **o alambique de cobre**.
Uma foto grande, de banco de imagem livre, baixada para `static/` (não hotlink),
com o título em Bodoni por cima e um botão em cobre. Não usar número grande com
label pequena, não usar gradiente como enfeite.

Seções, poucas e boas:
1. Herói — foto do alambique, nome da casa, uma linha do que é, botão de reserva
2. A casa — texto curto de história, com um filete `barrica` separando
3. Como funciona a visita — **aqui numeração 1/2/3 é legítima, porque é uma
   sequência real** (chegada, alambique, degustação, loja). Em outras seções, não numerar
4. Experiências — os 3 cards, com preço, duração e o que inclui
5. Onde fica e quando abre
6. Formulário

Alinhamento à esquerda em tudo. Centralizado só no herói, se ajudar.

## Painel

Discreto de propósito — quem usa passa horas ali. Fundo `papel`, tipografia
Archivo, densidade alta, filetes `barrica` em vez de card com sombra. Cobre
somente na ação primária e no item de menu ativo. A tabela é o produto: alinhar
números à direita, datas em coluna fixa, badge de status legível de longe.

## Estados vazios
Não são erro, são convite. Uma frase que diz o que fazer, na voz da interface,
com um traço de ilustração SVG simples (uma garrafa, um barril) em `cana`.
Estado vazio de "nenhum resultado para esse filtro" é diferente de "nada
cadastrado ainda" — textos diferentes.

## Escrita da interface
- Verbo do botão = verbo do resultado: botão "Reservar visita" → toast "Visita reservada"
- Sentence case sempre. Sem CAPS em label, sem "→" no fim de botão
- Erro não pede desculpa e não é vago: diz o que aconteceu e o que fazer.
  "Esse horário já está lotado. Restam 4 lugares às 15h." > "Erro ao agendar."

## Anti-lista: o que NÃO fazer
Estes são os vícios que fazem uma tela parecer gerada, e a spec deles premia
exatamente o oposto ("com a sua cara, não a cara de um tutorial"):
- Fundo creme quente + serifa de alto contraste + acento terracota. É o combo
  mais batido que existe hoje — por isso a paleta acima é esverdeada e o acento é cobre
- Tudo picado em cards idênticos, mesmo raio, mesma sombra cinza
- Eyebrow em CAPS espaçado acima de cada título
- Gradiente como decoração
- `fade-and-slide-up` em cada seção e transição de hover em cada card
- Meta-informação juntada com bullet do meio ("A · B · C")
- Monoespaçada em label pequena só pra parecer técnico

## Piso de qualidade (sem anunciar)
Responsivo até 375px · foco de teclado visível (`focus-visible`, não `outline:none`)
· contraste conferido no texto sobre cobre · `prefers-reduced-motion` respeitado ·
label associado a todo input.

## Movimento
Um momento orquestrado só, e ele responde a uma ação: a linha da tabela que muda
de status no painel dá um destaque curto ao trocar. Nada de animação de entrada
espalhada pela página.

## Processo obrigatório antes de codar tela
No M1, antes de escrever o `base.html`: apresente o plano visual (paleta em uso,
escala de tipo aplicada, wireframe em ASCII do herói e da tabela do painel) e
**espere eu aprovar**. Depois de construir, critique o próprio resultado contra a
anti-lista acima e me diga o que mudaria.
