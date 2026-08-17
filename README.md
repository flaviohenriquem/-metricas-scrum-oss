# metricas-scrum-oss

# Métricas de Gestão para Equipes Ágeis — Scripts de Coleta

Repositório de suporte à dissertação de mestrado:

> MENDONÇA, F. H. *Um Catálogo de Métricas de Gestão para Equipes Ágeis.*
> Dissertação (Mestrado em Ciências Computacionais e Modelagem Matemática)
> — Universidade do Estado do Rio de Janeiro, Rio de Janeiro, 2026.

---

## Requisitos

- Python 3.10 ou superior
- Bibliotecas: `requests`, `pandas`, `numpy`, `matplotlib`

Instale as dependências com:

```bash
pip install -r requirements.txt
```

---

## Configuração do token GitHub

Os scripts requerem um Personal Access Token (PAT) do GitHub com escopo
`public_repo`. **Nunca inclua o token diretamente no código.**

Antes de executar qualquer script, defina a variável de ambiente
`GITHUB_TOKEN` no terminal:

```bash
export GITHUB_TOKEN="seu_token_aqui"
```

No Windows (PowerShell):

```powershell
$env:GITHUB_TOKEN="seu_token_aqui"
```

Os scripts leem o token por meio de `os.environ.get("GITHUB_TOKEN", "")`.
Se a variável não estiver definida, as requisições à API retornarão erro
de autenticação (HTTP 401) ou ficarão sujeitas ao limite de taxa não
autenticado do GitHub.

---

## Estrutura do repositório
metricas-scrum-oss/
├── README.md
├── LICENSE
├── requirements.txt
├── docs/
│ └── mapeamento_metricas.md
└── src/
└── src/
├── bloco_01_commits_autores.py
├── bloco_02_pr_issues_releases.py
└── bloco_03_graphql.py

- **`bloco_01_commits_autores.py`** — coleta via API REST: commits e
  autores. Métricas M01, M04, M07, M08, M09, M10, M11, M12, M14, M15.
- **`bloco_02_pr_issues_releases.py`** — coleta via API REST: pull
  requests, issues e releases. Métricas M02, M03, M13, M16, M17, M18.
- **`bloco_03_graphql.py`** — coleta via API GraphQL: métricas que
  exigem consultas estruturadas a históricos de issues, PRs, commits,
  comentários, eventos e arquivos modificados. Métricas M19, M20, M21,
  M22, M23, M24, M25, M26.

Detalhes de cada métrica, incluindo unidades de amostragem, limites de
coleta e notas metodológicas específicas, estão documentados em
`docs/mapeamento_metricas.md`.

---

## Execução

Cada bloco pode ser executado de forma independente, na ordem que for
mais conveniente. Recomenda-se a ordem numérica (01 → 02 → 03), pois
alguns resultados do Bloco 01 são referenciados na interpretação
combinada apresentada na dissertação.

```bash
python src/src/bloco_01_commits_autores.py
python src/src/bloco_02_pr_issues_releases.py
python src/src/bloco_03_graphql.py
```

Os repositórios analisados são fixos no código:
`angular/angular.js` (2010–2022) e `angular/angular` (2014–2026).
Para aplicar os scripts a outros repositórios, altere a lista `REPOS`
no início de cada arquivo.

---

## Limitações e amostragem

Parte das métricas foi calculada sobre amostras, não sobre o histórico
completo dos repositórios, em razão dos limites de requisição das APIs
REST e GraphQL do GitHub. Os critérios de amostragem de cada métrica
estão documentados em `docs/mapeamento_metricas.md` e nas seções
correspondentes da dissertação (Capítulos 5 e 6).

---

## Licença

Este repositório está licenciado sob os termos da licença MIT.
Consulte o arquivo `LICENSE` para o texto completo.

---

## Citação

Se este repositório for utilizado como referência, cite a dissertação
correspondente:
MENDONÇA, F. H. Um Catálogo de Métricas de Gestão para Equipes Ágeis.
Dissertação (Mestrado em Ciências Computacionais e Modelagem
Matemática) — Universidade do Estado do Rio de Janeiro, Rio de
Janeiro, 2026.
