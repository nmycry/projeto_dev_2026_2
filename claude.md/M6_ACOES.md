# M6 — Ações de status e gestão de experiências

**Pré-requisito:** M5 concluído.
**Requisitos da spec cobertos:** 9, 10.

## Objetivo
Admin confirma/cancela uma visita e vê o resultado na hora. Admin cria, edita e
desativa experiências.

## Escopo
1. View de mudança de status por `POST` (`/painel/visitas/<id>/status/`):
   - **protegida por login como todas as outras** — o `LoginRequiredMixin` tem
     que estar aqui também, não só na listagem. Endpoint de escrita esquecido é
     a falha de segurança mais comum nesse tipo de painel, e o M10 tem teste
     justamente para isso
   - valida a transição pedida
   - **responde só o fragmento da linha da tabela**, trocado via HTMX
   - toast de feedback com Alpine

2. **CSRF com HTMX.** O `POST` do HTMX não passa pelo `<form>`, então o token não
   vai sozinho e o Django devolve 403. Resolver de um jeito só, no `base.html`,
   com `hx-headers` no `<body>` mandando o `X-CSRFToken` — não espalhar token
   por cada botão. Saber explicar por que o 403 acontece é pergunta provável.
3. Transições permitidas: definir explicitamente e recusar o resto no backend
   (não só esconder o botão). Confirmar uma visita já cancelada não pode passar.
4. CRUD de `Experiencia` no painel: `ListView`, `CreateView`, `UpdateView`.
   Desativar é editar `ativa`, **não** deletar.
5. Ao desativar uma experiência com visitas pendentes futuras: avisar o admin
   quantas são (decisão a registrar no DECISOES.md).

## Critério de aceite
- Confirmar/cancelar sem recarregar a página inteira; o badge muda na hora
- `POST` de transição inválida é recusado **no backend**, com mensagem
- Experiência desativada sai da home pública e **continua** aparecendo nas visitas antigas
- Sem HTMX (JS desligado) a ação ainda funciona ou falha de forma clara

## Explique no final
- O que o HTMX está realmente enviando e o que a view devolve (não é JSON, é HTML)
- Por que o `POST` do HTMX dá 403 sem o `X-CSRFToken` e o que o token protege
- Por que a regra de transição mora no backend e não no template
- Por que desativar em vez de deletar, e como isso se conecta com o `PROTECT` do M2

## Fora de escopo
Capacidade (M7), histórico de status, notificações.
