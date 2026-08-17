
"""
Bloco 02 — Coleta via API REST: PRs, issues e releases
Métricas: M02, M03, M13, M16, M17, M18

Repositórios analisados:
- angular/angular.js (2010-2022)
- angular/angular (2014-2026)

Notas metodológicas:
- M02: intervalos convertidos para dias inteiros antes da média (.dt.days)
- M13: coleta os 300 PRs merged mais recentes (não aleatório); arquivos
  paginados para capturar PRs com mais de 30 arquivos
- M16: AngularJS usa tags git (sem releases formais no GitHub)
- M17: snapshot calculado na data de execução do script

Dissertação: Um Catálogo de Métricas de Gestão para Equipes Ágeis
COMPMAT/UERJ, 2026
"""

import os
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timezone

TOKEN = os.environ.get("GITHUB_TOKEN", "")
HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

REPOS = [
    {"owner": "angular", "repo": "angular.js", "label": "AngularJS"},
    {"owner": "angular", "repo": "angular",    "label": "Angular"},
]


def get_paginado(url, params=None):
    """Coleta todos os registros de um endpoint paginado."""
    if params is None:
        params = {}
    resultados = []
    page = 1
    while True:
        params["page"] = page
        params["per_page"] = 100
        r = requests.get(url, headers=HEADERS, params=params)
        if r.status_code != 200 or not r.json():
            break
        resultados.extend(r.json())
        page += 1
    return resultados


def coletar_arquivos_pr(owner, repo, numero):
    """Coleta número total de arquivos de um PR com paginação completa."""
    total = 0
    page  = 1
    while True:
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{numero}/files"
        r   = requests.get(url, headers=HEADERS, params={"per_page": 100, "page": page})
        if r.status_code != 200:
            break
        dados = r.json()
        if not dados:
            break
        total += len(dados)
        if len(dados) < 100:
            break
        page += 1
    return total


# ─── M02 e M03 ────────────────────────────────────────────
print("="*50)
print("M02 — Ciclo de Pull Request (dias, média)")
print("M03 — Taxa de PRs fechados sem merge (%)")
print("="*50)
for repo_info in REPOS:
    owner = repo_info["owner"]
    repo  = repo_info["repo"]
    label = repo_info["label"]
    print(f"\n{label}")

    prs_raw = get_paginado(
        f"https://api.github.com/repos/{owner}/{repo}/pulls",
        {"state": "closed"}
    )

    prs = []
    for pr in prs_raw:
        prs.append({
            "created":   pr["created_at"],
            "merged":    pr["merged_at"],
            "closed":    pr["closed_at"],
            "is_merged": pr["merged_at"] is not None
        })

    df = pd.DataFrame(prs)
    df["created"] = pd.to_datetime(df["created"])
    df["merged"]  = pd.to_datetime(df["merged"])

    merged_df = df[df["is_merged"]]
    # .dt.days trunca para dias inteiros antes da média
    ciclo = (merged_df["merged"] - merged_df["created"]).dt.days
    print(f"  M02 — Ciclo médio: {ciclo.mean():.1f} dias (N={len(merged_df)} PRs merged)")

    rejeitados = (~df["is_merged"]).sum()
    taxa = rejeitados / len(df) * 100
    print(f"  M03 — Taxa de rejeição: {taxa:.1f}% ({rejeitados}/{len(df)} PRs fechados)")

# ─── M13 — Granularidade dos PRs ──────────────────────────
# Coleta os 300 PRs merged mais recentes (ordenados por criação decrescente)
# Pagina o endpoint de arquivos para capturar PRs com mais de 30 arquivos
print("\n" + "="*50)
print("M13 — Granularidade dos Pull Requests (arquivos por PR)")
print("="*50)
AMOSTRA_M13 = 300
for repo_info in REPOS:
    owner = repo_info["owner"]
    repo  = repo_info["repo"]
    label = repo_info["label"]
    print(f"\n{label}")

    prs_merged = []
    page = 1
    while len(prs_merged) < AMOSTRA_M13:
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
        params = {
            "state":     "closed",
            "sort":      "created",
            "direction": "desc",
            "per_page":  100,
            "page":      page
        }
        r = requests.get(url, headers=HEADERS, params=params)
        if r.status_code != 200 or not r.json():
            break
        for pr in r.json():
            if pr["merged_at"] and len(prs_merged) < AMOSTRA_M13:
                prs_merged.append(pr["number"])
        page += 1

    print(f"  PRs coletados: {len(prs_merged)}")
    arquivos = []
    for i, num in enumerate(prs_merged):
        n = coletar_arquivos_pr(owner, repo, num)
        arquivos.append(n)
        if (i + 1) % 100 == 0:
            print(f"  {i+1}/{len(prs_merged)} processados...")

    s = pd.Series(arquivos)
    print(f"  Média   : {s.mean():.1f} arquivos")
    print(f"  Mediana : {s.median():.1f} arquivos")
    print(f"  P90     : {s.quantile(0.9):.1f} arquivos")

# ─── M16 — Cadência de releases ───────────────────────────
print("\n" + "="*50)
print("M16 — Cadência de Releases (intervalo médio em dias)")
print("="*50)
for repo_info in REPOS:
    owner = repo_info["owner"]
    repo  = repo_info["repo"]
    label = repo_info["label"]

    # Tenta releases formais primeiro
    releases_raw = get_paginado(
        f"https://api.github.com/repos/{owner}/{repo}/releases"
    )
    datas = [r["published_at"] for r in releases_raw if r.get("published_at")]

    fonte = "releases formais"
    if not datas:
        # Fallback: tags com data do commit
        fonte = "tags git"
        tags_raw = get_paginado(
            f"https://api.github.com/repos/{owner}/{repo}/tags"
        )
        for tag in tags_raw:
            sha = tag["commit"]["sha"]
            r2  = requests.get(
                f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}",
                headers=HEADERS
            )
            if r2.status_code == 200:
                data_commit = r2.json()["commit"]["committer"]["date"]
                datas.append(data_commit)

    datas_dt = sorted([pd.to_datetime(d) for d in datas if d])
    intervalos = [(datas_dt[i+1] - datas_dt[i]).days
                  for i in range(len(datas_dt) - 1)]

    print(f"\n{label} ({fonte}): {len(datas_dt)} versões · "
          f"intervalo médio={np.mean(intervalos):.1f} dias")

# ─── M17 — Idade média de issues abertas ──────────────────
# Snapshot calculado na data de execução do script
print("\n" + "="*50)
print("M17 — Idade Média de Issues Abertas (dias)")
print("="*50)
ref = datetime.now(timezone.utc)
print(f"Data de referência (snapshot): {ref.strftime('%Y-%m-%d')}")
for repo_info in REPOS:
    owner = repo_info["owner"]
    repo  = repo_info["repo"]
    label = repo_info["label"]

    issues_raw = get_paginado(
        f"https://api.github.com/repos/{owner}/{repo}/issues",
        {"state": "open"}
    )
    idades = []
    for issue in issues_raw:
        if issue.get("pull_request"):
            continue  # exclui PRs que aparecem no endpoint de issues
        abertura = pd.to_datetime(issue["created_at"])
        idades.append((ref - abertura).days)

    s = pd.Series(idades)
    print(f"\n{label}: N={len(s)} · média={s.mean():.0f} dias · "
          f"mediana={s.median():.0f} dias")

# ─── M18 — Visibilidade externa ───────────────────────────
print("\n" + "="*50)
print("M18 — Visibilidade Externa (stars e forks, snapshot)")
print("="*50)
for repo_info in REPOS:
    owner = repo_info["owner"]
    repo  = repo_info["repo"]
    label = repo_info["label"]
    r = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}",
        headers=HEADERS
    )
    data = r.json()
    print(f"\n{label}: stars={data['stargazers_count']} · "
          f"forks={data['forks_count']}")
