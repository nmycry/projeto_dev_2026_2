# M5 — Painel: listagem e detalhe

**Pré-requisito:** M4 concluído.
**Requisitos da spec cobertos:** 8 (ordenação, filtro, busca, paginação).

## Objetivo
Listagem administrativa das visitas, útil com 200 registros no banco.

## Escopo
1. `VisitaListView` (`ListView`) herdando da base protegida:
   - ordenada por `data`, `horario`
   - **filtro por status** via querystring (`?status=pendente`)
   - **busca por nome ou e-mail** (`?q=`)
   - **paginação** de 20 por página
   - filtro e busca **combinam** e sobrevivem à troca de página
2. Tabela com **badge colorida por status** (a spec cita isso nominalmente),
   nas cores semânticas do `DESIGN.md`. Densidade alta, filete `barrica` em vez
   de card com sombra, cobre só na ação primária.
3. Estado vazio tratado, com a cara do tema — e um estado vazio diferente para
   "nenhum resultado para esse filtro".
4. `VisitaDetailView` com todos os dados da visita e da experiência.
5. Seed de desenvolvimento com ~200 visitas variadas, para eu ver paginação e
   filtro funcionando de verdade (command separado, não roda em produção).

## Critério de aceite
- Filtro + busca + página 2 na mesma URL, tudo funcionando junto
- Nenhuma query dentro do loop do template (checar N+1 na tabela)
- Tabela legível no celular

## Explique no final
- **`get_queryset()` vs `get_context_data()`**: o que fiz em cada um e por quê
- QuerySet é lazy: em que linha exata a query vai ao banco
- Onde estaria o N+1 nessa tela e como o `select_related` resolve
- Como a paginação do Django monta o `page_obj`

## Fora de escopo
Mudar status (M6), CRUD de experiências (M6), tela do dia (M8).
