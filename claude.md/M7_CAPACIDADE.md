# M7 — Extra 1: trava de capacidade por horário

**Pré-requisito:** M6 concluído. **Daqui em diante é "além do mínimo".**
Se o prazo apertar, os módulos M8 e M9 saem antes deste.

## Objetivo
O alambique não pode receber mais gente num horário do que a experiência
suporta. Sem isso, o overbooking é descoberto com o grupo no portão.

## Regra
Para uma tentativa de agendamento em (`experiencia`, `data`, `horario`):
soma de `num_pessoas` das visitas **não canceladas** naquele slot, mais as
pessoas da nova visita, não pode passar de `experiencia.capacidade_por_horario`.

## Implementação — trecho de defesa obrigatória
Esta é a regra que eu escolhi adicionar por conta própria, então ela vai
destacada no PR — o que a torna a pergunta mais provável da entrevista inteira.
Você implementa, mas com estas exigências:

1. **Diga onde colocou a regra e por quê.** Liste em duas ou três linhas as
   opções que existiam (form, model, módulo de serviço), qual você escolheu e o
   trade-off que isso trouxe. Implemente na sua recomendação, sem me esperar —
   se eu discordar, eu peço a mudança depois.
2. Casos de borda a tratar, todos explicitados no código:
   - visita cancelada não conta na soma
   - edição de visita existente não pode conflitar consigo mesma
   - dois envios simultâneos no último lugar (race condition). Com MySQL isso
     deixa de ser hipotético: apresente a opção de `transaction.atomic()` +
     `select_for_update()` travando as visitas do slot, e explique o custo do
     lock. Se decidirmos não implementar, tem que constar no `DECISOES.md` como
     limitação conhecida — limitação assumida conta a favor, esquecimento não
3. Ao final, as 5 perguntas da sabatina **sobre esta regra**, incluindo uma
   sobre concorrência.

## Escopo (você faz)
1. Mensagem de erro clara: quantos lugares restam naquele horário.
2. Sugestão dos horários vizinhos com vaga.
3. Indicador de ocupação na tela de detalhe da visita: a **barra segmentada** do
   `DESIGN.md`, fina, em cobre sobre filete, mostrando quantas vagas do horário
   estão tomadas. É a peça mais "instrumento" do painel.

## Critério de aceite
- Estourar a capacidade é recusado, com mensagem que diz quantas vagas sobraram
- Cancelar uma visita **devolve** as vagas
- Editar uma visita sem mudar o horário não acusa conflito falso

## Explique no final
- Como a regra se comporta sob concorrência e qual é o limite dessa solução
- Por que a checagem no backend não pode ser substituída por esconder o horário na UI
