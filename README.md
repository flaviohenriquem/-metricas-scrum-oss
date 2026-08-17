# -metricas-scrum-oss

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

Crie um arquivo `.env` na raiz do repositório:
