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
