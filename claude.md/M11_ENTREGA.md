# M11 — Documentação e submissão

**Pré-requisito:** tudo que vai ser entregue já commitado.
**Este módulo vale nota pesada.** É onde a maioria perde ponto de graça.

## 1. `README.md`
Escrito para alguém que nunca viu o projeto rodar. Deve conter, nesta ordem:
1. O que é o projeto e qual tema escolhi
2. Stack e versões
3. Pré-requisitos: Python 3.12, Docker + Docker Compose, e as libs de sistema do
   `mysqlclient` (`pkg-config`, `default-libmysqlclient-dev`, `build-essential`
   no Ubuntu — dizer isso explicitamente, é onde a instalação quebra)
4. Instalação: clone, venv, `pip install -r requirements.txt`
5. `.env`: copiar do `.env.example` — os valores de dev já funcionam sem editar
6. `docker compose up -d` e **esperar o banco ficar `healthy`**
   (`docker compose ps` mostra o status)
7. `python manage.py migrate`
8. `python manage.py seed_experiencias`
9. **`python manage.py createsuperuser`** — é o passo que mais falta nas entregas
10. `runserver`, em que endereço abre o site e em que endereço abre o painel
11. `python manage.py test` — mencionar o `down -v` como solução se der erro de
    permissão no banco de teste
12. `docker compose down` para parar (e `down -v` para apagar os dados)

**Teste de verdade:** `git clone` do fork numa pasta limpa **e**
`docker compose down -v` para zerar o volume, depois seguir o README
literalmente, sem usar nada que só existe na minha máquina. Se travar em algum
passo, o README está errado, não eu.

## 2. `DECISOES.md` (uma página basta)
- Tema escolhido e por quê
- Stack: o que ganhei e o que perdi com Django + templates + HTMX
- **Por que Django 5.2 LTS e não a 6.x**: suporte de três anos e material de
  aprendizado alinhado, contra features novas que este projeto não usaria
- **Tailwind pelo browser build**: é build de prototipagem, autorizado pelo
  README do teste; em produção seria CLI/Vite com purge. Limitação assumida
- **Por que MySQL em container e não SQLite**: paridade com produção, tipos e
  constraints reais, `select_for_update` disponível — e o custo aceito em troca
  (quem avalia precisa de Docker e das libs do driver)
- Por que containerizei só o banco e não a aplicação
- Por que **não** usei django-allauth
- Por que `on_delete=PROTECT`
- As ambiguidades que percebi e o que decidi em cada uma:
  painel vazio · visitas de experiência desativada · desativar experiência com
  pendentes futuras · cancelar visita confirmada · data no passado · envio
  duplicado · fuso horário · prazo de cancelamento pelo visitante (se M9 existir)
- Como escolhi o que testar
- **Uso de IA**, as três respostas da spec:
  1. onde usei e para quê
  2. **uma vez em que a IA me deu algo ruim ou errado**: o que era, como percebi,
     o que fiz no lugar — usar o `NOTAS_IA.md`, não inventar agora
  3. uma decisão que tomei contra a sugestão da IA

## 3. Descrição do PR
- O que fiz além do pedido e por quê (os extras dos M7/M8/M9 que entraram)
- **O que decidi não fazer e por quê** (o que cortei, e que corte foi deliberado)
- Onde tive dificuldade — ser honesto sobre a curva do Django conta a favor, não contra

## 4. Submissão
Pull Request do meu fork para `mupisystems/projeto_dev_2026_2`.
Conferir antes: histórico com commits incrementais, `.env` fora do repositório,
nenhuma credencial versionada, testes verdes.

## Sua tarefa neste módulo
Revisar meus três documentos como se fosse o avaliador: apontar onde está vago,
onde estou dizendo "usei X" sem dizer por que, e onde um passo do README não roda
numa máquina limpa. **Não escreva o DECISOES.md por mim** — as decisões são minhas,
e eu vou ter que defendê-las em voz alta.
