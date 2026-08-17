#python
import requests
import pandas as pd
import numpy as np
from collections import defaultdict

TOKEN = "SEU_TOKEN_AQUI"
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
            break
        data = r.json()
        if not data:
            break
        for c in data:
            login = None
            if c.get("author") and c["author"].get("login"):
                login = c["author"]["login"]
            date = c["commit"]["author"]["date"][:10]
            commits.append({"login": login, "date": date, "ano": ano})
        page += 1
    return commits

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
print("\n=== M01 — Cadência de Commits ===")
for label, df in todos.items():
    mensal = df.groupby(df["date"].str[:7]).size()
    print(f"\n{label}: média={mensal.mean():.1f} DP={mensal.std():.1f} CV={mensal.std()/mensal.mean()*100:.1f}%")
    anual = df.groupby("ano").size()
    print(anual.to_string())

