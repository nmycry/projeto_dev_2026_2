# M10 — Testes

**Pré-requisito:** M6 concluído (extras podem estar incompletos).
A spec pede testes nos fluxos "que não podem quebrar", e nomeia três.
Estes são os três — mais dois baratos que fecham furos reais.

## Objetivo
Testes que cobrem exatamente onde uma quebra silenciosa faz o sistema perder
dado ou vazar acesso. Nada de teste de getter para inflar contagem.

## Regras para todos os testes
- `django.test.TestCase` + `Client`. Sem pytest, sem factory, sem mock.
- **`reverse()` em toda URL.** Nunca string literal: teste com URL fixa quebra
  na primeira mudança de rota e vira dívida.
- Nomes de método descrevendo comportamento, em português:
  `test_post_valido_cria_visita_pendente`. A lista de testes tem que ler como
  especificação.
- Cada teste monta o que precisa no próprio `setUp`. Nenhum depende de outro
  teste nem do seed.
- Asserção sobre o **valor**, não só sobre a mudança: comparar com
  `Visita.Status.CONFIRMADA`, não com a string `"confirmada"`.

## Escopo — `visitas/tests/`

### `test_agendamento.py` — o fluxo que gera dado
1. **`POST` válido cria a visita como `PENDENTE`.** Conferir também que os
   campos chegaram certos, não só que o objeto existe.
2. **`POST` inválido não cria nada.** Comparar a contagem **antes e depois**
   (não `count() == 0`, que quebra se o `setUp` criar algo), conferir que a
   resposta é 200 com o formulário reexibido — **não** 500 nem redirect — e usar
   `assertFormError` para provar que o erro saiu no campo certo.
3. **Experiência desativada é recusada no `POST`** e não aparece na home.
   Fecha a segunda metade do comportamento 10: "a página pública reflete a
   mudança". Sem esse teste, alguém desativa uma experiência, ela continua
   sendo agendável, e nada acusa.

### `test_painel.py` — o acesso
4. **`GET` do painel sem sessão redireciona para o login** (`assertRedirects`).
5. **`GET` do painel com sessão retorna 200.** Sem ele, o teste 4 passaria
   mesmo se o painel estivesse quebrado para todo mundo.
6. **`POST` anônimo no endpoint de mudança de status não altera nada.**
   Este é o furo que quase todo mundo deixa: o `LoginRequiredMixin` entra na
   listagem e o endpoint de escrita fica exposto. Aí o `GET` redireciona
   bonitinho, o teste 4 passa, e um `POST` de fora muda o banco em silêncio.
   Conferir que a resposta é redirect/403 **e** que o status no banco continua o
   mesmo depois de `refresh_from_db()`.

### `test_status.py` — a ação
7. **Mudança de status persiste** (`refresh_from_db`, comparando com o valor do
   `TextChoices`).
8. **Transição inválida é recusada e não altera o status** — confirmar uma
   visita já cancelada, por exemplo. Regra recusada no backend, não só botão
   escondido no template.

### Se o M7 existir
9. **Estourar a capacidade do horário é recusado**, e cancelar uma visita
   devolve a vaga. É a lógica de negócio mais frágil do projeto.

## Pré-condição de infraestrutura
Os testes rodam contra o MySQL do container, num banco `test_<nome>` que o Django
cria e derruba a cada execução. Se der erro de permissão, o `init.sql` do M1 não
foi aplicado — provavelmente o volume já existia quando ele foi criado. Nesse caso:
`docker compose down -v && docker compose up -d` para recriar do zero.
**Documentar isso no README**, porque quem for avaliar vai rodar os testes.

## Critério de aceite
- `python manage.py test` verde, sem warning, num clone limpo
- Cada teste passa **isolado** (`manage.py test visitas.tests.test_painel`)
- Rodar duas vezes seguidas dá o mesmo resultado
- **Teste de mutação manual:** comente a linha do `LoginRequiredMixin` e rode.
  Se todos continuarem verdes, os testes não estão testando nada. Repita
  quebrando de propósito a validação e a regra de transição. Desfaça depois

## Explique no final
- Por que **esses** e não outros (vai literal no `DECISOES.md`)
- Por que o `POST` anônimo no endpoint de status é mais perigoso que o `GET` do painel
- O que o `TestCase` faz com transação entre testes, e por que isso exige um
  banco separado (`test_*`) com privilégio próprio
- Por que `reverse()` em vez de URL literal
