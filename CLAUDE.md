# CONTEXTO FIXO DO PROJETO — leia antes de qualquer módulo

> **Como usar:** salve este arquivo **e o `DESIGN.md`** na raiz do repositório,
> este como `CLAUDE.md`
> (ou `AGENTS.md`, dependendo da ferramenta). Ele vale para todos os módulos.
> Se a sua ferramenta não lê arquivo de contexto, cole este texto no início de
> cada sessão nova.

## Quem sou eu

Desenvolvedor júnior full stack. Sólido em: HTTP, SQL, MVC, ORM (Eloquent),
Git, Docker, Tailwind, JavaScript, React, Laravel, Node.
**Iniciante em Django** — assuma zero conhecimento de CBV, ORM do Django,
templates, migrations, admin, signals, middleware.

## O que estou fazendo

Teste técnico para vaga de dev júnior. A nota final sai de uma **conversa
técnica sobre o meu próprio código**, não de um checklist automático. Código
que eu não entendo é pior que código que não existe.

## Regras de engajamento (não negociáveis)

1. **Um módulo por vez.** Termine o módulo pedido e pare. Não adiante trabalho
   de módulos seguintes.
2. **Explique antes de escrever.** Para cada arquivo novo: 2–3 linhas sobre o
   que ele faz e por que existe. Depois o código.
3. **Modo defesa: toda sessão termina com sabatina.** Depois de entregar o
   módulo, me faça **5 perguntas** sobre o código que você acabou de escrever —
   perguntas de "por que assim e não de outro jeito", não de "o que essa linha
   faz". Espere minha resposta. Depois avalie cada uma: onde eu fui preciso,
   onde eu fui vago, e onde eu claramente repeti o que li sem entender. Se eu
   errar, **não me dê a resposta pronta na hora**: me diga onde procurar e me
   pergunte de novo. Esse passo não é opcional e não pode ser encurtado.
4. **Nenhuma dependência fora da lista abaixo** sem me perguntar primeiro.
5. **Não invente requisito.** Se não está no módulo nem aqui, pergunte.
6. **Sinalize o "jeito Django".** Sempre que usar algo que não é óbvio para
   quem vem de Laravel, marque com um aviso curto explicando o equivalente.
7. **Nada de comentário óbvio no código.** Comentário só onde a decisão não é
   evidente pela leitura.
8. **Ao fim de cada módulo**, entregue: (a) resumo do que mudou, (b) o que eu
   preciso saber explicar na entrevista sobre esse trecho, (c) mensagem de
   commit sugerida.

## Stack — a lista é essa

```
Python 3.12 · Django 5.2 LTS · python-decouple · mysqlclient
MySQL 8.4 LTS em container (docker compose) — Django roda no host, em venv
Tailwind CSS v4 (browser build, via CDN) · HTMX 2 · Alpine 3 — todos por <script>
Testes: django.test (TestCase + Client) — nativo, sem pytest
```

**Django 5.2 LTS, não a 6.x.** A 6.1 é a versão atual, mas a 5.2 é a LTS: suporte
de três anos e, o que mais importa aqui, é a versão a que a maior parte do
material de aprendizado está alinhada — inclusive o tutorial oficial que eu vou
fazer no dia 1. Aprender e entregar na mesma semana pede material que combina com
o código. Isso vira item do `DECISOES.md`.

**Versões travadas no `requirements.txt`** (`Django==5.2.*`, e assim por diante).
O critério deles é "roda na máquina de outra pessoa seguindo só o seu README" —
dependência solta quebra isso no dia em que sair uma major.

**Só o banco vai em container.** Django roda no host, em venv: evita rebuild de
imagem a cada alteração e mantém o `runserver` com reload instantâneo.
Containerizar a aplicação fica registrado no `DECISOES.md` como decisão de não fazer.

**Proibido:** django-allauth, DRF, django-crispy-forms, django-filter,
django-tailwind, django-debug-toolbar, qualquer build de CSS.

Autenticação: `django.contrib.auth` nativo (`LoginView`, `LogoutView`,
`LoginRequiredMixin`).

## Tema e glossário

**Alambique de cachaça artesanal em Salinas/MG** — agendamento de visita
guiada e degustação.

| Termo da spec | Nome no projeto |
|---|---|
| "opção" que o visitante escolhe | `Experiencia` (tipo de tour) |
| "registro" enviado pelo visitante | `Visita` |

Português do Brasil em tudo (labels, mensagens, nomes de campo).

**Toda decisão visual está no `DESIGN.md`** — paleta, tipografia, escala de
espaçamento, estrutura da home, escrita de interface e a anti-lista do que não
fazer. Nenhum módulo de tela improvisa visual: se falta algo lá, pergunte.

## Convenções

- Uma app Django: `visitas`. Views separadas em `views/publico.py` e
  `views/painel.py`.
- Projeto de configuração: `config/`.
- `TIME_ZONE = 'America/Sao_Paulo'`, `USE_TZ = True`, `LANGUAGE_CODE = 'pt-br'`.
- Commits pequenos e incrementais, em português, no imperativo:
  `feat: adiciona formulario publico de agendamento`.
  Prefixos: `feat`, `fix`, `test`, `docs`, `refactor`, `chore`.
- `.env` no `.gitignore`; `.env.example` versionado, com valores de dev que
  sobem sem edição nenhuma.
- Credenciais do banco só via `.env`. Nada de string de conexão no settings.

## Fora de escopo em todo o projeto

- API REST (não existe cliente para ela)
- `/admin` do Django como painel de gestão (fica registrado só para apoio)
- Autenticação escrita do zero
- Deploy (opcional, só se sobrar tempo)
- Containerizar a aplicação Django (só o banco vai em container)
