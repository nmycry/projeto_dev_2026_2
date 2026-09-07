# M1 — Fundação do projeto

**Pré-requisito meu:** ter feito o tutorial oficial do Django partes 1–4 à mão,
num projeto descartável. Não pule isso.
**Pré-requisito do repositório:** fork já criado e clonado.

## Objetivo
Projeto Django rodando na minha máquina, com o template base e o layout
público esqueleto no ar. Nada de model ainda.

## Escopo
1. `venv`, `requirements.txt` **com versões travadas**
   (`Django==5.2.*`, `python-decouple==3.*`, `mysqlclient==2.*`),
   `.gitignore` cobrindo `.venv/`, `__pycache__/`, `.env`, `staticfiles/`.
2. `django-admin startproject config .` e `python manage.py startapp visitas`.
3. **`docker-compose.yml`** com um serviço só, `db`:
   - imagem `mysql:8.4`
   - variáveis do `.env` (`MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`,
     `MYSQL_ROOT_PASSWORD`)
   - `command` forçando `utf8mb4` e collation `utf8mb4_unicode_ci`
   - volume nomeado, para os dados sobreviverem ao `down`
   - porta publicada em **`3307:3306`** — não 3306, para não colidir com um MySQL
     já instalado na máquina de quem for avaliar
   - `healthcheck` com `mysqladmin ping`, para o README poder dizer
     "espere ficar healthy antes de migrar"
4. **`docker/mysql/init.sql`**, montado em `/docker-entrypoint-initdb.d/`:
   dar ao usuário da aplicação privilégio nos bancos `test\_%`. Sem isso,
   `manage.py test` falha por permissão — o Django cria um banco `test_<nome>`
   ao rodar os testes, e a imagem do MySQL só concede privilégio no banco
   principal. **Obrigatório**: é o que faz os testes rodarem na máquina de outra
   pessoa. Atenção: esse script só executa quando o volume nasce do zero.
5. `config/settings.py`:
   - `SECRET_KEY`, `DEBUG` e `ALLOWED_HOSTS` vindos de `.env` via `python-decouple`
   - `DATABASES` apontando para MySQL, host/porta/usuário/senha do `.env`
   - `OPTIONS` com `charset: utf8mb4` e
     `init_command: "SET sql_mode='STRICT_TRANS_TABLES'"` — modo estrito é o que a
     documentação do Django recomenda; sem ele o MySQL trunca dado calado
   - `LANGUAGE_CODE = 'pt-br'`, `TIME_ZONE = 'America/Sao_Paulo'`, `USE_TZ = True`
   - app `visitas` registrada, diretório de templates configurado
6. `.env.example` versionado, com valores de dev que sobem sem edição nenhuma —
   incluindo `DEBUG=True`, senão o `runserver` não serve os arquivos de `static/`
   e quem avaliar abre a página sem imagem.
7. Reestruturar `visitas/views.py` no pacote `visitas/views/` com
   `__init__.py`, `publico.py` e `painel.py` (vazios por enquanto).
8. `visitas/urls.py` incluído no `config/urls.py`, com uma rota `/` provisória.
9. **Plano visual antes do código.** Seguindo o `DESIGN.md`, apresente paleta em
   uso, escala de tipo aplicada e wireframe em ASCII do herói e da tabela do
   painel. **Espere minha aprovação** antes de escrever template.
10. `templates/base.html`: Google Fonts (Bodoni Moda + Archivo), **Tailwind v4
    browser build + bloco `@theme` exatamente como está no `DESIGN.md`** (não o
    CDN v3 com `tailwind.config`, que está descontinuado), HTMX 2 e Alpine 3 por
    `<script>`, blocos `{% block titulo %}` e `{% block conteudo %}`, header e
    footer do alambique.
11. `STATIC_URL` e `STATICFILES_DIRS` configurados, com `static/` criado.
12. `templates/visitas/home.html` estendendo a base, com o herói já no visual
    definido — é o teste de que os tokens estão valendo.

## Critério de aceite
- `docker compose up -d` sobe o banco e ele chega a `healthy`
- `python manage.py migrate` conecta e cria as tabelas do Django
- `python manage.py runserver` sobe sem warning
- `/` abre com as fontes carregadas e as cores do `DESIGN.md` aplicadas —
  `bg-papel` e `text-garrafa` funcionando como classe
- `.env` não aparece no `git status`
- `docker compose down && docker compose up -d` mantém os dados (volume funcionando)

## Aviso sobre fuso horário no MySQL
Com `USE_TZ = True`, o MySQL precisa das tabelas de fuso carregadas
(`mysql_tzinfo_to_sql`) para lookups de data sobre campo `DateTimeField`
funcionarem certo. No nosso caso os campos do agendamento são `DateField` e
`TimeField`, então o risco é baixo — **mas não filtre `criado_em__date` sem
antes conferir isso**, porque é o tipo de bug que passa silencioso. Se precisar
filtrar por dia de criação, use faixa de datetime. Vale registrar como limitação
conhecida no `DECISOES.md`.

## Aviso sobre o driver
`mysqlclient` compila extensão C. No Ubuntu exige
`sudo apt install pkg-config default-libmysqlclient-dev build-essential`.
Documentar isso no README no M11 — é onde a instalação quebra na máquina de
outra pessoa. Se a compilação virar problema real, me avise **antes** de trocar
por `PyMySQL`: ele exige o hack `install_as_MySQLdb()` e não é oficialmente
suportado pelo Django, o que é dívida de entrevista.

## Explique no final
- O que `startproject` cria e para que serve cada arquivo
- Por que o banco está em container e a aplicação não
- Por que `sql_mode` estrito importa (o que o MySQL faz sem ele)
- Para que serve o `init.sql` dos privilégios de `test\_%`
- Por que `DEBUG` e as credenciais não podem vir hardcoded

## Fora de escopo
Models, migrations, formulário, autenticação, qualquer tela real.
