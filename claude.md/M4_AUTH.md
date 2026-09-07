# M4 — Autenticação e proteção de rota

**Pré-requisito:** M3 concluído.
**Requisitos da spec cobertos:** 5, 6.

## Objetivo
Painel inacessível sem sessão, inclusive pela URL direta. Login e logout
funcionando com o auth nativo.

## Escopo
1. `LoginView` e `LogoutView` nativas, com template de login próprio
   (design simples de propósito — a spec diz que a tela de login não é avaliada).
2. `LOGIN_URL`, `LOGIN_REDIRECT_URL`, `LOGOUT_REDIRECT_URL` no settings.
3. `PainelBaseView` com `LoginRequiredMixin`, para todas as views do painel
   herdarem. Uma `TemplateView` provisória em `/painel/` só para validar o bloqueio.
4. Header do painel com o usuário logado e botão de sair (logout por `POST`).

## Critério de aceite
- `/painel/` em aba anônima **redireciona para o login**, não dá 500 nem mostra conteúdo
- Depois do login, volta para a página que eu tentei acessar (`?next=`)
- Logout encerra a sessão e o `/painel/` volta a barrar
- `createsuperuser` documentado (entra no README no M11)

## Explique no final
- Como o Django sabe que estou logado entre um request e outro (cookie de sessão, middleware)
- O que o `LoginRequiredMixin` faz por baixo e **por que a ordem dos mixins importa**
- Por que logout por `POST` e não por link `GET`
- Por que **não** usei django-allauth (vira item do DECISOES.md)

## Fora de escopo
Listagem, filtros, ações, cadastro de usuário pela interface, permissões por papel.
