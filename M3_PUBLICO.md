# M3 — Página pública e formulário de agendamento

**Pré-requisito:** M2 concluído.
**Requisitos da spec cobertos:** 1, 2, 3 (validação), 4 (confirmação), 7 (status inicial).

## Objetivo
Visitante escolhe a experiência, envia o formulário, vê confirmação. Registro
nasce com status `PENDENTE`.

## Escopo
1. `visitas/views/publico.py`:
   - `HomeView` (`TemplateView` ou `CreateView`) listando **só experiências ativas**
   - `POST` criando a `Visita` com status `PENDENTE`
   - Página/rota de sucesso mostrando o que foi agendado
2. `visitas/forms.py`: `VisitaForm` (`ModelForm`), campos do visitante.
   Widgets com classes Tailwind e `label` em português.
3. Templates:
   - **Home com conteúdo real do negócio**, não só o formulário. O comportamento 1
     da spec pede "informações do negócio/projeto" e as opções ativas. Poucas
     seções bem feitas: o alambique e sua história, como funciona a visita
     (o que o visitante vê e prova), as experiências em cards com preço e
     duração, onde fica e quando abre, e o formulário. Sem landing page de
     agência e sem seção vazia só para encher.
   - Página de sucesso.
4. **Validação também no frontend** — o comportamento 3 pede as duas pontas,
   explicitamente. No mínimo, atributos HTML nos widgets do form: `required`,
   `type="email"`, `min` na data (hoje), `min="1"` em número de pessoas,
   `maxlength`. Se quiser ir além, feedback inline com Alpine antes do submit.
   Isso **não substitui** a validação de backend, que é a que protege o banco.
5. Erros de validação exibidos campo a campo, **sem perder o que o usuário digitou**.
6. Labels associados aos campos (`for`/`id`) — barato e conta como acessibilidade.
7. Responsivo: testar em 375px de largura.

## Validação — trecho de defesa obrigatória
Você implementa, mas este é um dos trechos que eu vou ter que defender em voz
alta. Portanto:
- deixe explícito **por que** cada regra entrou em `clean_<campo>` ou em `clean()`,
  e qual seria a consequência de colocá-la no outro lugar
- regras a cobrir: campos obrigatórios · e-mail válido · data não pode ser no
  passado · `num_pessoas` >= 1 · experiência tem que estar ativa
- ao final, as 5 perguntas da sabatina **sobre este trecho** (regra 3 do contexto)

## Critério de aceite
- A home apresenta o negócio, não é só um formulário solto numa página
- Envio válido cria a `Visita` como `PENDENTE` e mostra confirmação
- Envio inválido é bloqueado no navegador (frontend) **e**, se eu burlar o HTML
  via DevTools ou curl, é bloqueado no backend e **não** cria nada
- Erros voltam no formulário preenchido, campo a campo
- Experiência desativada não aparece na home nem é aceita no POST
- Data de ontem é recusada

## Explique no final
- Em que momento exato a validação roda, do request até o save
- O que o `{% csrf_token %}` faz e o que acontece sem ele
- Por que a validação de backend não pode confiar na de frontend

## Fora de escopo
Painel, login, capacidade por horário (isso é M7), e-mail, token do visitante.
