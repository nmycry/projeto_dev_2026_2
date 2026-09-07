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
