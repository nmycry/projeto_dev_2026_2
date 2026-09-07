# M8 — Extra 2: "Roteiro de hoje"

**Pré-requisito:** M6 concluído (M7 não é obrigatório antes).

## Objetivo
A listagem paginada com filtro serve para **gerenciar**. Ela não serve para
**operar**. Esta tela é para o guia abrir no celular, na manhã da visita, com sol
na tela e sem tempo de filtrar nada.

## Escopo
1. Rota `/painel/hoje/`, protegida, com link destacado no header do painel.
2. Só as visitas **confirmadas de hoje**, agrupadas por horário, em ordem.
3. Por grupo de horário: total de pessoas somado e a experiência.
4. Por visita: nome, número de pessoas, telefone com link `tel:`, e as
   **observações em destaque** (é onde vem restrição alimentar, criança, idoso).
5. Total geral de pessoas no dia, no topo.
6. Botão de presença / no-show por visita (campo novo `compareceu`, nullable).
7. Layout de toque, tratado como **painel de embarque** (ver `DESIGN.md`):
   horários em coluna mono, alvos grandes, uma coluna, zero hover. A tela é
   escura como o resto do projeto — a ressalva sobre sol direto e a mitigação
   por contraste máximo estão no `DESIGN.md` e vão para o `DECISOES.md`.
8. Navegação simples para outro dia (`?data=`), mas o padrão é hoje.
9. Estado vazio próprio: "nenhuma visita confirmada para hoje".

## Critério de aceite
- Abre em 375px e dá para usar de pé, com uma mão
- Visitas pendentes e canceladas **não** aparecem aqui
- Fuso correto: "hoje" é hoje em `America/Sao_Paulo`

## Explique no final
- Por que essa tela existe separada da listagem, em uma frase de produto
- Como você garantiu o "hoje" correto com `USE_TZ = True` (`timezone.localdate()`)
- Como agrupou por horário sem gerar N+1
