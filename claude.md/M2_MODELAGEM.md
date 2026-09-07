# M2 — Modelagem, migrations e seed

**Pré-requisito:** M1 concluído.

## Objetivo
Banco modelado, migrado, visível no `/admin` e populado com dados de exemplo.

## Modelos (em `visitas/models.py`)

### `Experiencia`
| Campo | Tipo |
|---|---|
| `titulo` | CharField(120) |
| `descricao` | TextField |
| `duracao_minutos` | PositiveIntegerField |
| `preco` | DecimalField(8,2) |
| `capacidade_por_horario` | PositiveIntegerField |
| `ativa` | BooleanField(default=True) |
| `criado_em` / `atualizado_em` | auto_now_add / auto_now |

### `Visita`
| Campo | Tipo |
|---|---|
| `nome` | CharField(120) |
| `email` | EmailField |
| `telefone` | CharField(20), blank |
| `experiencia` | FK → Experiencia, `on_delete=PROTECT`, `related_name='visitas'` |
| `data` | DateField |
| `horario` | TimeField |
| `num_pessoas` | PositiveIntegerField |
| `observacoes` | TextField, blank |
| `status` | CharField(12) com `TextChoices`, default `PENDENTE` |
| `criado_em` / `atualizado_em` | auto_now_add / auto_now |

`Status` como `models.TextChoices`: `PENDENTE`, `CONFIRMADA`, `CANCELADA`.
`Meta.ordering` de `Visita` por `data` e `horario`.
`__str__` útil nos dois modelos.

## Escopo
1. Os dois modelos + migrations aplicadas.
2. Registrar ambos no `/admin` com `list_display` mínimo.
3. Management command `seed_experiencias` criando **3 experiências** com preço,
   duração e capacidade diferentes entre si (Visita Clássica, Degustação
   Guiada, Tour do Alambique com Almoço). Idempotente (`get_or_create`).

## Critério de aceite
- `makemigrations` + `migrate` limpos
- `python manage.py seed_experiencias` roda duas vezes sem duplicar
- Os 3 registros aparecem no `/admin`

## Explique no final
- O que a migration gerada contém e o que acontece se eu editar o model sem gerar uma nova
- **Por que `PROTECT` e não `CASCADE`** nessa FK (isso vai virar item do DECISOES.md)
- O que `related_name` muda na prática
- Por que `auto_now_add` e `auto_now` são diferentes

## Fora de escopo
Formulário, telas, validação de regra de negócio, capacidade.
