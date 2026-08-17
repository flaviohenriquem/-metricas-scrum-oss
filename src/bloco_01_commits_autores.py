"""
Bloco 01 — Coleta via API REST: commits e autores
Métricas: M01, M04, M07, M08, M09, M10, M11, M12, M14, M15

Repositórios analisados:
- angular/angular.js (2010-2022)
- angular/angular (2014-2026)

Dissertação: Um Catálogo de Métricas de Gestão para Equipes Ágeis
COMPMAT/UERJ, 2026
"""

import os
import requests
import pandas as pd
import numpy as np
from collections import defaultdict

TOKEN = os.environ.get("GITHUB_TOKEN", "")
HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

REPOS = [
    {"owner": "angular", "repo": "angular.js", "label": "AngularJS",
     "anos": list(range(2010, 2023))},
    {"owner": "angular", "repo": "angular",    "label": "Angular",
     "anos": list(range(2014, 2027))},
]


def coletar_commits_por_ano(owner, repo, ano):
    commits = []
    page = 1
    since = f"{ano}-01-01T00:00:00Z"
    until = f"{ano}-12-31T23:59:59Z"
    while True:
        url = f"https://api.github.com/repos/{owner}/{repo}/commits"
        params = {"since": since, "until": until, "per_page": 100, "page": page}
        r = requests.get(url, headers=HEADERS, params=params)
        if r.status_code != 200:
            print(f"    Erro {r.status_code}")
            break
        data = r.json()
        if not data:
            break
        for c in data:
            login = None
            if c.get("author") and c["author"].get("login"):
                login = c["author"]["login"]
                date = c["commit"]["author"]["date"]
            commits.append({"login": login, "date": date, "ano": ano})
        page += 1
    return commits


def gini(valores):
    v = sorted(valores)
    n = len(v)
    if n == 0:
        return 0
    soma = sum(v)
    if soma == 0:
        return 0
    return (2 * sum((i + 1) * v[i] for i in range(n)) / (n * soma)) - (n + 1) / n


# ─── COLETA ───────────────────────────────────────────────
todos = {}
for repo_info in REPOS:
    owner = repo_info["owner"]
    repo  = repo_info["repo"]
    label = repo_info["label"]
    anos  = repo_info["anos"]
    print(f"\n{'='*50}\nRepositório: {owner}/{repo}\n{'='*50}")
    dados = []
    for ano in anos:
        print(f"  Coletando {ano}...", end=" ", flush=True)
        commits = coletar_commits_por_ano(owner, repo, ano)
        print(f"{len(commits)} commits")
        dados.extend(commits)
    todos[label] = pd.DataFrame(dados)

# ─── M01 — Cadência de commits ────────────────────────────
# DP calculado com divisor n-1 (estimador amostral, pandas padrão)
print("\n" + "="*50)
print("M01 — Cadência de Commits (commits/mês)")
print("="*50)
for label, df in todos.items():
    mensal = df.groupby(df["date"].str[:7]).size()
    media  = mensal.mean()
    dp     = mensal.std()  # ddof=1 (amostral)
    cv     = dp / media * 100
    print(f"\n{label}: média={media:.1f} DP={dp:.1f} CV={cv:.1f}%")
    anual = df.groupby("ano").size()
    print(anual.to_string())

# ─── M04 — Tempo médio entre commits ──────────────────────
# NOTA: calcula intervalo entre timestamps completos de
# commits consecutivos (ordem cronológica). Commits no mesmo
# dia em horários distintos produzem intervalos fracionários,
# truncados para dias inteiros (.days), o que pode resultar
# em muitos intervalos iguais a zero.
print("\n" + "="*50)
print("M04 — Tempo Médio entre Commits (dias)")
print("="*50)
for label, df in todos.items():
    df2 = df.copy()
    df2["date"] = pd.to_datetime(df2["date"])
    datas_geral = sorted(df2["date"].unique())
    intervalos_geral = [
        (datas_geral[i+1] - datas_geral[i]).days
        for i in range(len(datas_geral) - 1)
    ]
    print(f"\n{label}: média={np.mean(intervalos_geral):.2f} dias")
    for ano, grupo in df2.groupby("ano"):
        datas = sorted(grupo["date"].unique())
        if len(datas) < 2:
            print(f"  {ano}: dados insuficientes")
            continue
        intervalos = [(datas[i+1] - datas[i]).days for i in range(len(datas)-1)]
        print(f"  {ano}: {np.mean(intervalos):.2f} dias")

# ─── M07 — Engajamento de colaboradores ───────────────────
print("\n" + "="*50)
print("M07 — Engajamento de Colaboradores (contrib. distintos/mês)")
print("="*50)
for label, df in todos.items():
    df2 = df[df["login"].notna()].copy()
    df2["mes"] = df2["date"].str[:7]
    mensal = df2.groupby(["ano", "mes"])["login"].nunique()
    anual_media = mensal.groupby("ano").mean()
    print(f"\n{label}:")
    print(anual_media.round(1).to_string())

# ─── M08 — Coeficiente de Gini ────────────────────────────
print("\n" + "="*50)
print("M08 — Concentração de Contribuições (Gini anual)")
print("="*50)
for label, df in todos.items():
    df2 = df[df["login"].notna()]
    print(f"\n{label}:")
    for ano, grupo in df2.groupby("ano"):
        counts = grupo["login"].value_counts().tolist()
        g = gini(counts)
        print(f"  {ano}: {g:.3f}")

# ─── M09 — Proporção de core team ─────────────────────────
print("\n" + "="*50)
print("M09 — Proporção de Core Team (autores responsáveis por 80% dos commits)")
print("="*50)
for label, df in todos.items():
    df2 = df[df["login"].notna()]
    print(f"\n{label}:")
    for ano, grupo in df2.groupby("ano"):
        counts = grupo["login"].value_counts()
        total  = counts.sum()
        acum   = 0
        core   = 0
        for v in counts:
            acum += v
            core += 1
            if acum >= total * 0.8:
                break
        pct = core / len(counts) * 100
        print(f"  {ano}: {core}/{len(counts)} autores = {pct:.1f}%")

# ─── M10 — Taxa de retenção ───────────────────────────────
print("\n" + "="*50)
print("M10 — Taxa de Retenção de Contribuidores (%)")
print("="*50)
for label, df in todos.items():
    df2 = df[df["login"].notna()]
    anos = sorted(df2["ano"].unique())
    print(f"\n{label}:")
    for i in range(1, len(anos)):
        ano_ant = anos[i-1]
        ano_at  = anos[i]
        set_ant = set(df2[df2["ano"] == ano_ant]["login"])
        set_at  = set(df2[df2["ano"] == ano_at]["login"])
        if not set_ant:
            continue
        retidos = len(set_ant & set_at)
        taxa = retidos / len(set_ant) * 100
        print(f"  {ano_ant}→{ano_at}: {retidos}/{len(set_ant)} = {taxa:.1f}%")

# ─── M11 — Longevidade média ───────────────────────────────
print("\n" + "="*50)
print("M11 — Longevidade Média dos Contribuidores (anos)")
print("="*50)
for label, df in todos.items():
    df2   = df[df["login"].notna()]
    longa = df2.groupby("login")["ano"].nunique()
    print(f"\n{label}: média={longa.mean():.2f} anos (N={len(longa)} autores)")

# ─── M12 — Novos contribuidores ───────────────────────────
print("\n" + "="*50)
print("M12 — Proporção de Novos Contribuidores (%)")
print("="*50)
for label, df in todos.items():
    df2   = df[df["login"].notna()]
    anos  = sorted(df2["ano"].unique())
    vistos = set()
    print(f"\n{label}:")
    for ano in anos:
        ativos = set(df2[df2["ano"] == ano]["login"])
        novos  = ativos - vistos
        pct    = len(novos) / len(ativos) * 100 if ativos else 0
        print(f"  {ano}: {len(novos)}/{len(ativos)} = {pct:.1f}%")
        vistos |= ativos

# ─── M14 — Conversão de novatos ───────────────────────────
print("\n" + "="*50)
print("M14 — Taxa de Conversão de Novatos (%)")
print("="*50)
for label, df in todos.items():
    df2   = df[df["login"].notna()]
    anos  = sorted(df2["ano"].unique())
    vistos = set()
    print(f"\n{label}:")
    for i in range(len(anos) - 1):
        ano  = anos[i]
        prox = anos[i+1]
        ativos      = set(df2[df2["ano"] == ano]["login"])
        novos       = ativos - vistos
        ativos_prox = set(df2[df2["ano"] == prox]["login"])
        convertidos = novos & ativos_prox
        pct = len(convertidos) / len(novos) * 100 if novos else 0
        print(f"  {ano}: {len(convertidos)}/{len(novos)} = {pct:.1f}%")
        vistos |= ativos

# ─── M15 — Contribuidores ocasionais ──────────────────────
print("\n" + "="*50)
print("M15 — Proporção de Contribuidores Ocasionais (exatamente 1 commit no histórico)")
print("="*50)
for label, df in todos.items():
    df2        = df[df["login"].notna()]
    counts     = df2.groupby("login").size()
    ocasionais = (counts == 1).sum()
    total      = len(counts)
    print(f"\n{label}: {ocasionais}/{total} = {ocasionais/total*100:.1f}%")
