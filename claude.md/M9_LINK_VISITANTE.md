# M9 — Extra 3: link de acompanhamento do visitante

**Pré-requisito:** M6 concluído. É o extra mais caro; se o prazo apertar, é o primeiro a cair.

## Objetivo
Tapar o buraco do fluxo da spec: do jeito que está, o visitante envia o
formulário e desaparece. Não sabe se foi confirmado, e se desistir, o alambique
segura uma vaga fantasma.

## Escopo
1. Campo `token` (`UUIDField`, default `uuid4`, indexado) na `Visita`. Migration.
2. Rota pública `/minha-visita/<uuid:token>/` — **sem login**:
   - status atual, dados do agendamento, dados da experiência
   - botão de cancelar, se ainda estiver no prazo
3. Regra de prazo para cancelamento: definir um limite (ex. 24h antes) e
   **registrar a escolha no DECISOES.md**.
4. O link aparece na página de sucesso do M3, com aviso para guardar.
5. Cancelamento pelo visitante:
   - muda o status para `CANCELADA`
   - **devolve a vaga** (integra com o M7, se ele existir)
   - fica visível no painel como cancelamento feito pelo visitante, não pelo admin
6. Token inválido ou inexistente: 404 com página amigável, sem vazar se existe.

## Perguntas que este módulo abre — responder no DECISOES.md
- Cancelar até quantas horas antes, e por quê?
- O admin precisa ser avisado? (se não implementar, dizer que decidiu não implementar)
- Cancelamento de visita já confirmada é permitido pelo visitante?
- Token na URL é seguro o suficiente aqui? Qual é o risco real e por que é aceitável?

## Critério de aceite
- Link funciona em aba anônima
- Cancelar dentro do prazo funciona; fora do prazo é recusado no backend
- Token de outra visita não dá acesso a esta

## Explique no final
- Por que UUID e não o `id` sequencial na URL
- Qual é o modelo de ameaça aqui e por que essa solução é proporcional ao caso
