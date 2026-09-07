<img src="logo.png" alt="Mupi Systems Logo" width="200"/>

# Visitas ao Alambique

Sistema de agendamento de visita guiada e degustação para um alambique de
cachaça artesanal em Salinas/MG. Um visitante escolhe uma experiência (visita
clássica, degustação guiada, tour com almoço...), preenche o formulário
público e o pedido entra no banco como `pendente`. Do outro lado, o painel
protegido por login lista, filtra e busca esses pedidos, confirma ou cancela
cada um, e gerencia as experiências oferecidas na página pública.

## Stack e versões

| Camada | Tecnologia |
|---|---|
| Linguagem / framework | Python 3.12 · Django 5.2 LTS |
| Banco de dados | MySQL 8.4 LTS (container Docker) |
| Configuração / driver do banco | python-decouple · mysqlclient |
| Frontend | Tailwind CSS v4 (browser build via CDN) · HTMX 2 · Alpine 3 |
| Autenticação | `django.contrib.auth` nativo |
| Testes | `django.test` (`TestCase` + `Client`), nativo do Django |

O Django roda no host (dentro de uma venv), só o banco vai em container — os
motivos de cada uma dessas escolhas estão no `DECISOES.md`.

## Pré-requisitos

- **Python 3.12**
- **Docker** e **Docker Compose**
- Libs de sistema do `mysqlclient` (é aqui que a instalação mais costuma
  quebrar). No Ubuntu/Debian:

  ```bash
  sudo apt install pkg-config default-libmysqlclient-dev build-essential
  ```

## Instalação

1. Clone o repositório e entre na pasta:

   ```bash
   git clone <url-do-seu-fork>
   cd projeto_dev_2026_2
   ```

2. Crie e ative a venv, depois instale as dependências:

   ```bash
   python3.12 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Copie o arquivo de variáveis de ambiente. Os valores de dev já funcionam
   sem editar nada:

   ```bash
   cp .env.example .env
   ```

## Subindo o banco

Suba o container do MySQL:

```bash
docker compose up -d
```

Espere o banco ficar `healthy` antes de seguir (o healthcheck do
`docker-compose.yml` demora alguns segundos):

```bash
docker compose ps
```

## Preparando a aplicação

Com o banco de pé, rode, nesta ordem:

```bash
python manage.py migrate
python manage.py seed_experiencias
python manage.py createsuperuser
```

- `migrate` cria as tabelas.
- `seed_experiencias` cadastra as 3 experiências iniciais (Visita Clássica,
  Degustação Guiada, Tour do Alambique com Almoço). É idempotente — pode
  rodar de novo sem duplicar nada.
- `createsuperuser` cria o usuário que faz login no painel — sem isso não dá
  para entrar em `/painel/`.

Opcional, só para testar a listagem do painel com volume de dados (só roda
com `DEBUG=True`, gera ~200 visitas variadas e não afeta as experiências):

```bash
python manage.py seed_visitas
```

## Rodando o projeto

```bash
python manage.py runserver
```

- Página pública: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Login do painel: [http://127.0.0.1:8000/login/](http://127.0.0.1:8000/login/)
- Painel (exige login): [http://127.0.0.1:8000/painel/](http://127.0.0.1:8000/painel/)

Atalho: depois que `.env`, migrations, seed e superuser já existirem uma
primeira vez, `make run` sobe o banco e o servidor numa tacada só (é só um
alias para os dois comandos acima — não substitui os passos anteriores na
primeira vez que o projeto é configurado).

## Rodando os testes

```bash
python manage.py test
```

Os testes rodam contra um banco `test_<MYSQL_DATABASE>` que o Django cria e
derruba a cada execução — não é o banco de desenvolvimento. Para isso, o
usuário do MySQL precisa de privilégio de `CREATE`/`DROP DATABASE` em bancos
`test_%`, já concedido pelo `docker/mysql/init.sql`
(`GRANT ALL PRIVILEGES ON \`test_%\`.* TO 'visitas_app'@'%'`).

Se `manage.py test` der erro de permissão ao criar o banco de teste,
provavelmente o volume do MySQL já existia quando o `init.sql` foi criado (ele
só roda na primeira inicialização do volume). Nesse caso:

```bash
docker compose down -v
docker compose up -d
```

Isso recria o volume do zero e reaplica o `init.sql`.

## Parando o projeto

```bash
docker compose down       # para o container, mantém os dados
docker compose down -v    # para o container e apaga o volume do banco
```

## Mais informações

- Decisões técnicas, ambiguidades da spec e uso de IA: `DECISOES.md`
- Decisões de identidade visual (paleta, tipografia, escrita de interface):
  `DESIGN.md`
