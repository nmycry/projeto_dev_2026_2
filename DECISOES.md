# DECISÕES.md — registro de decisões técnicas

> Cada entrada: contexto, decisão, por quê. Alternativas descartadas só quando ajudam
> a explicar a decisão.

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
