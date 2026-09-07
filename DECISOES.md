# DECISÕES.md — registro de decisões técnicas

> Cada entrada: contexto, decisão, por quê. Alternativas descartadas só quando ajudam
> a explicar a decisão.

## Tema — alambique de cachaça artesanal em Salinas/MG

**Decisão:** agendamento de visita guiada e degustação para um alambique
fictício em Salinas/MG.

**Por quê:** Salinas é a capital nacional da cachaça artesanal, um tema
regional real e que dá para defender com naturalidade numa conversa técnica.
Ele também foge dos exemplos citados no próprio enunciado do teste
(barbearia, clínica, curso, ONG), que tendem a se repetir entre candidatos —
e criatividade é o primeiro critério de avaliação declarado. O domínio ainda
gera regras de negócio que não são só CRUD: capacidade por horário, duração e
preço variando por tipo de tour, visitas em grupo — o suficiente para
justificar os extras dos módulos M7–M9 sem inventar requisito fora do tema.

Vocabulário: "opção" da spec vira `Experiencia` (o tipo de tour); "registro"
vira `Visita`.

## Stack — Django + templates + HTMX/Alpine: o que ganhei e o que perdi

**Decisão:** Django 5.2 LTS (Class Based Views + templates server-rendered),
MySQL 8.4 em container, Tailwind v4 via CDN, HTMX 2 e Alpine 3 só nos pontos
de interatividade pontual (troca de status, toasts), autenticação nativa do
`django.contrib.auth`, testes com `django.test` nativo.

**Por quê:** o teste é essencialmente CRUD + painel protegido + regras de
negócio simples — exatamente o ponto forte do Django: `ListView` já entrega
filtro, busca e paginação (requisito 8) com pouco código próprio, e o auth
nativo cobre login/logout/proteção de rota sem precisar reinventar nada.

**O que ganhei:** velocidade para chegar no CRUD e no painel (admin, forms,
migrations, auth prontos), menos decisão de infraestrutura para tomar sozinho
como iniciante em Django, e uma stack que a Mupi usa internamente.

**O que perdi:** nenhuma reatividade de SPA — toda troca de tela é
server-rendered, com HTMX cobrindo só os pedaços que precisavam de feedback
sem reload (status, presença). Também abri mão de tipagem forte de request/
response que frameworks tipo FastAPI/Next dariam, e da familiaridade que eu já
tinha com Laravel/Express — o custo foi a curva de aprendizado do "jeito
Django" (migrations, ORM, sistema de templates) na mesma semana da entrega.

## Por que Django 5.2 LTS e não a 6.x

**Contexto:** no início do projeto a versão atual do Django já era a 6.1.

**Decisão:** fixar `Django==5.2.*` no `requirements.txt`.

**Por quê:** a 5.2 é a LTS (três anos de suporte) e é a versão à qual a maior
parte do material de aprendizado — inclusive o tutorial oficial que fiz no
dia 1 — está alinhada. Aprender Django e entregar o teste na mesma semana
pede material que combine com o código que estou escrevendo; as features
novas da 6.x não seriam usadas por este projeto de qualquer forma.

## Por que Tailwind pelo browser build (CDN)

**Decisão:** Tailwind v4 carregado por `<script>` no `<head>`, sem build,
sem `django-tailwind`.

**Por quê:** é a via de CSS que o próprio enunciado do teste autoriza
explicitamente ("Tailwind via CDN, uma linha no `<head>`") e evita gastar
tempo configurando toolchain, que não é o que está sendo avaliado. Assumo
que é build de prototipagem — em produção seria CLI/Vite com purge de
classes não usadas; aqui o CSS entregue é maior do que precisaria ser. Custo
aceito conscientemente pelo tempo que economiza.

## Por que MySQL em container e não SQLite

**Decisão:** MySQL 8.4 LTS rodando em container Docker, não SQLite em
arquivo.

**Por quê:** MySQL dá paridade com o que rodaria em produção — tipos e
constraints reais (`on_delete=PROTECT` só é reforçado de verdade num banco
com FK de verdade), e `select_for_update()` disponível caso a trava de
capacidade do M7 precisasse de transação (ver decisão de concorrência mais
abaixo). O custo aceito em troca: quem avalia precisa ter Docker e as libs de
sistema do `mysqlclient` instaladas — por isso o README detalha esse
pré-requisito explicitamente.

## Por que containerizei só o banco, não a aplicação

**Decisão:** só o serviço `db` está no `docker-compose.yml`. O Django roda no
host, dentro de uma venv.

**Por quê:** containerizar a aplicação evitaria uma dependência a mais
(Docker para rodar o próprio Django), mas custaria rebuild de imagem a cada
alteração de código e tiraria o reload instantâneo do `runserver` — atrito
real numa semana curta de desenvolvimento e aprendizado. Containerizar só o
banco resolve o problema real (isolar um serviço com estado, versão e
configuração próprios) sem pagar esse custo. Fica registrado aqui como
decisão de **não fazer**, não como corte por falta de tempo.

## Por que `on_delete=PROTECT` em `Visita.experiencia`

**Decisão:** a foreign key de `Visita` para `Experiencia` usa
`on_delete=models.PROTECT`, não `CASCADE` nem `SET_NULL`.

**Por quê:** o painel não tem `DeleteView` para `Experiencia` — "remover" uma
experiência da vitrine pública é editar `ativa` para `False`, nunca apagar o
registro (ver decisão do M6 abaixo). `PROTECT` é a trava que impede alguém de
tentar apagar uma `Experiencia` pelo banco ou por um admin futuro enquanto
existir qualquer `Visita` vinculada — inclusive uma visita antiga já
concluída, cujo histórico não pode virar `NULL` nem sumir. `CASCADE` apagaria
visitas reais junto com a experiência; `SET_NULL` deixaria visitas antigas
sem saber a qual experiência pertenceram. Nenhuma das duas é aceitável para
um registro que já aconteceu.

## Por que não usei `django-allauth`

**Decisão:** autenticação do painel é só `django.contrib.auth` nativo
(`LoginView`, `LogoutView`, `LoginRequiredMixin`), sem `django-allauth`.

**Por quê:** o `allauth` resolve social login, verificação de e-mail, múltiplos
provedores e fluxos de signup — nenhum requisito da spec pede isso; o que é
pedido é login, logout e rota protegida, e o nativo cobre os três sem
configuração extra. Escolhi não carregar uma dependência com superfície que eu
não usaria e não conseguiria explicar inteira numa entrevista — carregar
biblioteca "porque é o padrão" sem precisar de todo o que ela oferece é o
tipo de escolha que o teste pede para justificar, não para copiar.

## Ambiguidades adicionais da spec

**Painel sem nenhum registro vs. filtro sem resultado:** são dois estados
vazios diferentes, tratados com mensagens diferentes em
`visita_list.html` — "nenhuma visita agendada ainda" quando a tabela
`Visita` está mesmo vazia (`existe_visita=False` em `VisitaListView`), e
"nenhuma visita encontrada para esse filtro" quando existem visitas mas o
filtro/busca não bateu com nenhuma. Separar os dois evita que alguém ache que
o sistema nunca recebeu agendamento quando na verdade só o filtro atual está
sem resultado.

**Data no passado:** o formulário público recusa (`VisitaForm.clean_data()`
levanta `ValidationError` se `data < date.today()`), e o campo de data no
HTML já nasce com `min` igual a hoje. Decisão simples: não existe visita
guiada retroativa, então aceitar o valor seria só adiar o erro para dentro do
banco.

**Envio duplicado:** decidido **não implementar** nenhum bloqueio (não existe
verificação de e-mail + data + experiência repetidos em `VisitaForm` nem em
`views/publico.py`). Bloquear por esses três campos criaria falso positivo
legítimo — a mesma pessoa pode querer agendar duas experiências diferentes no
mesmo dia, ou reagendar depois que a primeira foi cancelada — e o teste não
define nenhuma regra de negócio que justifique um critério de duplicidade
específico. Fica como corte consciente, no mesmo espírito da decisão do M9 de
não implementar aviso de e-mail ao admin: sem infraestrutura ou regra clara
para apoiar a regra, a decisão mais segura é não regrar demais um caso que a
spec não define.

**Fuso horário:** `TIME_ZONE = 'America/Sao_Paulo'` e `USE_TZ = True` no
`settings.py`. Com `USE_TZ = True`, o Django guarda os `DateTimeField` em UTC
no banco e converte para o fuso configurado na exibição — sem isso,
`compareceu`/`criado_em`/`atualizado_em` e o cálculo de
`pode_cancelar_pelo_visitante()` (que compara `timezone.now()` com a data e
hora combinadas da visita) ficariam ambíguos assim que o servidor rodasse num
ambiente com fuso diferente do horário local do alambique.

## Como escolhi o que testar

**Decisão:** os testes cobrem os três fluxos que a spec nomeia
(`test_agendamento.py`, `test_painel.py`, `test_status.py`), mais os testes
de M7 (capacidade) e M9 (link do visitante) por serem a lógica de negócio
mais frágil do projeto, e o CRUD de experiências (`test_experiencias.py`).

**Por quê:** o critério que usei foi "onde uma quebra silenciosa faz o
sistema perder dado ou vazar acesso" — não inflar contagem com teste de
getter. Por isso `test_painel.py` não testa só o `GET` redirecionando sem
sessão: testa também que o `POST` anônimo no endpoint de mudança de status
não altera nada, que é o furo mais fácil de deixar passar (o
`LoginRequiredMixin` protege a listagem, mas um endpoint de escrita separado
pode ficar exposto sem ninguém perceber, porque o `GET` continua redirecionando
"bonitinho"). A trava de capacidade (M7) entrou porque é onde um bug é
invisível até o grupo errado chegar no portão lotado.

## Uso de IA

### Onde usei e para quê

Usei IA em três frentes, com papéis diferentes.

Antes de escrever código, usei para planejar: quebrei a spec em módulos com
escopo fechado e critério de aceite, e defini a stack confrontando o que eu
já sabia com o que o teste pedia. Durante a implementação, usei para gerar
código Django, já que eu venho de Laravel e Node — o Django foi a curva de
aprendizado desta semana. E usei como revisor: ao fim de cada módulo, pedia
perguntas sobre o código que acabara de sair, e respondia sem olhar a tela.
Quando eu não conseguia explicar uma decisão, voltava e estudava aquele
trecho antes de seguir.

O que eu não deleguei foi a leitura da spec e as decisões de produto. Os três
itens que fiz além do pedido saíram de perguntas sobre o negócio, não de
sugestão de ferramenta.

### Uma vez em que a IA me deu algo ruim ou errado

**Episódio A — o bug de layout que só apareceu na tela.** A IA gerou os
templates da página pública e do painel, e o código estava sintaticamente
correto: as views respondiam, os dados apareciam, os testes passavam. Quando
abri no navegador em tela cheia, todo o conteúdo estava confinado a menos da
metade da largura da janela, e as linhas divisórias das seções paravam no
meio da tela, como se a página tivesse sido cortada. Percebi olhando, não
lendo — é o tipo de erro que não quebra nada: nenhuma exceção, nenhum teste
vermelho, HTML válido. Se eu tivesse só revisado o código sem abrir a página
em resolução cheia, teria entregado assim. Inspecionei o elemento no DevTools
para achar qual wrapper estava limitando a largura, corrigi a estrutura do
container e movi as bordas de seção para a tag externa, de modo que a linha
atravessasse a tela e o conteúdo ficasse centrado, e conferi em 1920px e em
375px. Lição: código gerado que "funciona" não é código verificado — passei
a abrir cada tela renderizada, em duas larguras, antes de commitar.

**Episódio B — configuração de Tailwind desatualizada.** Para configurar as
cores e fontes do projeto sem toolchain de CSS, a IA me deu um bloco usando o
CDN antigo do Tailwind com um objeto `tailwind.config` em JavaScript. Funcionou
o suficiente para eu seguir em frente. Fui conferir na documentação oficial
quando precisei entender como as variáveis de tema se transformavam em
classes, e descobri que aquela forma é da versão 3 e está descontinuada: na
versão 4 o CDN é outro e a configuração é CSS-first, declarada com `@theme`
dentro de um bloco de estilo. Ou seja, a IA me entregou o padrão da versão
anterior com confiança, sem mencionar que havia mudado. Troquei o script e
migrei a configuração para `@theme`, e registrei uma limitação que descobri
no caminho: o build de navegador é para desenvolvimento e protótipo, em
produção eu usaria CLI ou Vite com purge. Lição: em ferramenta que virou
major recente, a IA responde com o padrão antigo e sem aviso — passei a
conferir a documentação da versão específica antes de aceitar bloco de
configuração.

**Episódio C — sugestões "extras" copiadas da própria spec.** Pedi ajuda para
escolher o que fazer além do mínimo. A IA sugeriu histórico de mudanças de
status, contadores com gráfico no painel e proteção contra spam. Pareciam
razoáveis e eu quase segui. Ao reler o enunciado, vi que aquelas três coisas
estavam literalmente na lista de sugestões do próprio teste — e que a mesma
seção avisava que quem só executa aquela lista entrega o resultado de todo
mundo. A IA tinha reciclado o texto que eu mesmo tinha dado como contexto, e
devolvido como se fosse ideia. Joguei as três para "se sobrar tempo" e troquei
o critério: passei a perguntar o que faltava para o alambique operar de
verdade na segunda de manhã, e daí saíram os três que entreguei — a trava de
capacidade por horário (M7), a tela de roteiro do dia (M8) e o link de
acompanhamento do visitante (M9). Lição: IA otimiza para resposta plausível, e
o material que está no contexto é o mais plausível de todos — ideia de
produto precisa de uma pergunta sobre o negócio, não de um pedido de sugestão.

### Decisões que tomei contra a sugestão da IA

**Banco de dados.** A recomendação foi SQLite, com o argumento de fricção
zero na instalação: quem for avaliar não precisa de Docker nem de
credencial, e o critério de "roda na máquina de outra pessoa seguindo só o
seu README" fica mais seguro. Fui de MySQL em container, por dois motivos: é
o banco que eu já opero no meu dia a dia, e eu queria paridade de tipos e
constraints com produção — em especial para poder discutir a condição de
corrida da regra de capacidade com `select_for_update`, que o SQLite não
oferece (ver "Por que MySQL em container e não SQLite" e "Concorrência na
trava de capacidade" acima). Assumi o custo: o README passou a exigir Docker
e as bibliotecas de sistema do driver, e documentei os dois.

**Direção visual.** A sugestão foi um visual claro e artesanal, alinhado à
tradição de um produtor de cachaça, com o argumento de que "futurista" num
alambique seria incoerente com o tema. Discordei e fui para uma interface
escura de instrumentos. Meu argumento: um alambique é uma planta industrial —
cobre, tubulação, termômetro, teor medido em décimos — e tratar o
agendamento como operação medida diz mais sobre o negócio do que um panfleto
de tradição. A faixa de leituras no topo da página e a barra de ocupação por
horário no painel saem dessa leitura. Registro também o que perdi com a
segunda escolha: tela escura reflete mais sob sol direto, e a tela de
roteiro do dia é justamente a que se usa no portão às nove da manhã — mitigado
com contraste máximo e tipografia grande (ver decisão do M8 acima), mas é um
trade-off assumido, não um detalhe que passou.

## M6 — Desativar `Experiencia` em vez de deletar

**Contexto:** o painel precisa de um jeito de "remover" uma experiência da home
pública sem apagar o histórico de visitas já feitas.

**Decisão:** `Experiencia` nunca é deletada pelo painel. O CRUD só tem `ListView`,
`CreateView` e `UpdateView` — não existe `DeleteView`. "Desativar" é editar o campo
`ativa` para `False`.

**Por quê:** `Visita.experiencia` usa `on_delete=models.PROTECT` (decisão do M2).
Deletar uma `Experiencia` com qualquer `Visita` vinculada — mesmo uma visita antiga,
já concluída — levantaria `ProtectedError` e travaria a operação. Desativar não tem
esse problema: a `Visita` continua apontando para a mesma `Experiencia`, só que ela
para de aparecer no formulário público (`Experiencia.objects.filter(ativa=True)`,
já usado em `views/publico.py` e no `queryset` do `VisitaForm`). Ao desativar uma
experiência com visitas pendentes futuras, o painel avisa quantas existem — a
desativação não é bloqueada, é só sinalizada, porque cancelar essas visitas é uma
decisão humana, não automática.

## M7 — Onde mora a regra de capacidade por horário

**Contexto:** a trava de capacidade (soma de `num_pessoas` por `experiencia` +
`data` + `horario`) precisa ser consultada em dois lugares sem relação entre si:
na validação do agendamento público (`VisitaForm`) e na barra de ocupação do
painel (`VisitaDetailView`).

**Decisão:** a consulta e o cálculo de vagas moram num módulo de serviço,
`visitas/capacidade.py`, com funções simples (`pessoas_reservadas`,
`vagas_restantes`, `sugerir_horarios_vizinhos`). O `VisitaForm.clean()` chama
essas funções para validar e montar a mensagem de erro; a `VisitaDetailView`
chama a mesma função para montar a barra de ocupação.

**Por quê:** colocar a regra só no `Visita.clean()` do model deslocaria uma
consulta que soma linhas irmãs (outras visitas do mesmo slot) para dentro de um
método de instância, que normalmente valida só os próprios campos. Colocar só
no `VisitaForm` deixaria a `VisitaDetailView` sem acesso à mesma lógica, forçando
duplicar a query ou o painel importar o form só para reaproveitar um pedaço
dele. Um módulo de serviço evita as duas coisas e é testável sozinho, sem
precisar de request nem de form. Ressalva: "camada de serviço" não é um padrão
que o Django prescreve — é uma escolha nossa para não duplicar regra de negócio,
não algo copiado de tutorial.

## M7 — Concorrência na trava de capacidade: limitação assumida

**Contexto:** a validação de capacidade é check-then-act — `vagas_restantes()`
roda no `clean()` do form, e o `save()` acontece depois, fora de qualquer bloco
atômico. Duas requisições simultâneas disputando o último lugar do mesmo
horário podem, cada uma, ler "1 vaga livre" e as duas passarem, estourando a
capacidade.

**Decisão:** não implementar `transaction.atomic()` + `select_for_update()`
agora. A opção correta seria abrir a transação na view pública, travar com
`select_for_update()` as visitas não canceladas daquele slot, recontar dentro
da transação e só então salvar — isso fecha a corrida, mas serializa qualquer
escrita concorrente (agendar, cancelar, confirmar) que toque o mesmo
`experiencia` + `data` + `horario` enquanto o lock estiver aberto, e exige
reestruturar a view (`form.is_valid()`/`form.save()` hoje não rodam dentro de
um bloco atômico).

**Por quê aceitar a limitação:** o volume esperado é de um alambique artesanal,
não um e-commerce de alta concorrência — o risco só se materializa quando duas
pessoas tentam pegar a última vaga do mesmo horário no mesmo instante. Nenhum
critério de aceite do M7 testa concorrência. Fica registrado aqui como
limitação conhecida e consciente, não como esquecimento.

## M8 — Tela escura no roteiro de hoje, mesmo sob sol direto

**Contexto:** o `/painel/hoje/` é a única tela do projeto pensada para ser
usada fora de uma mesa — no celular, na mão, de manhã, possivelmente com sol
batendo na tela. Tela escura reflete mais luz ambiente que tela clara, o que é
uma desvantagem real desse cenário específico.

**Decisão:** manter o tema escuro do projeto (`vapor` sobre `grafite`) também
nessa tela, sem criar uma variante clara só para ela. Mitigar com contraste
máximo (a maior razão de luminância que a paleta oferece), tipografia grande
(`.medida` em 28px para o horário) e alvos de toque grandes (botões de
presença em coluna, `py-4`), em vez de resolver com uma segunda paleta.

**Por quê:** o projeto não tem tema claro em lugar nenhum — criar um só para
essa tela quebraria a identidade visual e ainda exigiria manter dois conjuntos
de cores testados. O contraste `vapor`/`grafite` já é o maior disponível na
paleta; o resto do problema (reflexo de sol na tela do aparelho) é uma
limitação de hardware que nenhuma escolha de CSS resolve. Assumido como
trade-off consciente, registrado aqui em vez de descoberto na entrevista.

## M9 — Link de acompanhamento do visitante

**Contexto:** o formulário público (M3) não devolve nenhum jeito de o
visitante saber se a visita foi confirmada, nem de desistir sem ligar para o
alambique — uma vaga fantasma persiste até alguém do painel perceber e
cancelar manualmente.

**Decisão — prazo de cancelamento de 24h antes do horário agendado:**
`Visita.HORAS_LIMITE_CANCELAMENTO = 24`, verificado em
`pode_cancelar_pelo_visitante()` comparando `timezone.now()` com o
`datetime` combinado de `data` + `horario`.

**Por quê:** é o próprio exemplo citado na spec do módulo e dá ao alambique
uma janela mínima para remanejar a vaga sem impor uma regra tão rígida que
recuse cancelamentos de última hora com uma antecedência maior — não existe
critério de negócio informado que justifique um número diferente.

**Decisão — admin não é avisado do cancelamento:** não implementado.

**Por quê:** não existe backend de e-mail configurado em nenhum lugar do
projeto (`settings.py` sem `EMAIL_*`, `.env.example` sem chave de e-mail) —
criar esse canal só para este módulo seria adicionar infraestrutura nova fora
do escopo pedido. O cancelamento já fica visível no painel (campo
`cancelada_por_visitante`, mostrado em `visita_detail.html` e na listagem),
que é o canal que já existe e que o responsável já consulta.

**Decisão — cancelamento de visita já `CONFIRMADA` é permitido pelo
visitante:** sim, enquanto dentro do prazo.

**Por quê:** `TRANSICOES_PERMITIDAS` (M6) já modela
`CONFIRMADA -> CANCELADA` como transição válida, e é o cenário mais comum na
prática — visita confirmada que precisa ser desmarcada depois. Negar isso só
ao visitante, mantendo a mesma transição liberada para o painel, criaria uma
inconsistência sem motivo.

**Decisão — UUID no lugar do `id` sequencial na URL:** `token` é
`UUIDField(default=uuid.uuid4, unique=True, db_index=True)`, gerado sozinho
por visita.

**Por quê:** um `id` sequencial deixaria qualquer pessoa adivinhar
`/minha-visita/43/` e ver nome, e-mail e telefone de outro visitante trocando
um número na URL. UUID4 tem 122 bits de entropia — não é enumerável por
tentativa. O modelo de ameaça aqui é baixo risco: o pior cenário é o próprio
link vazar (encaminhado, capturado num proxy), expondo só a visita do dono do
link — não um sistema de pagamento nem dado de terceiros — o que torna a
solução proporcional ao caso sem precisar de autenticação para esta tela.
