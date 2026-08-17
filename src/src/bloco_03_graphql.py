
"""
Bloco 03 — Coleta via API GraphQL: métricas avançadas
Métricas: M19, M20, M21, M22, M23, M24, M25, M26

Repositórios analisados:
- angular/angular.js (2010-2022)
- angular/angular (2014-2026)

Notas metodológicas:
- M19: issues CLOSED, até 100/ano, primeiros 5 comentários; autor
  identificado como User pela API GraphQL
- M20: extensões mapeadas explicitamente; demais entram como Outros
- M21: mediana é a medida principal; média reportada como complemento
- M22: denominador = issues fechadas (states: CLOSED)
- M23: mediana é a medida principal; média reportada como complemento
- M24: comentário humano = autor com __typename == User antes do fechamento
- M25: top 20 arquivos mais alterados, 300 commits recentes,
  excluindo dependências e lockfiles
- M26: até 100 commits/ano (amostra própria, independente de M20/M21)
Dissertação: Um Catálogo de Métricas de Gestão para Equipes Ágeis
COMPMAT/UERJ, 2026
"""

import os
import requests
import pandas as pd
import numpy as np
from datetime import datetime
from collections import defaultdict

TOKEN = os.environ.get("GITHUB_TOKEN", "")
HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "Content-Type": "application/json"
}

REPOS = [
    {"owner": "angular", "repo": "angular.js", "label": "AngularJS",
     "anos": list(range(2010, 2023))},
    {"owner": "angular", "repo": "angular",    "label": "Angular",
     "anos": list(range(2014, 2027))},
]

MAX_POR_ANO  = 100
MAX_COMMITS  = 50      # usado em M20 e M21
MAX_COMMITS_M26 = 100  # M26 usa amostra própria de até 100 commits/ano


def graphql(query):
    r = requests.post(
        "https://api.github.com/graphql",
        json={"query": query},
        headers=HEADERS
    )
    return r.json()


# ─── M19 — Tempo de primeira resposta humana ──────────────
print("="*50)
print("M19 — Tempo de Primeira Resposta Humana a Issues (dias)")
print("Issues CLOSED · até 100/ano · primeiros 5 comentários")
print("="*50)
for repo_info in REPOS:
    owner = repo_info["owner"]
    repo  = repo_info["repo"]
    label = repo_info["label"]
    anos  = repo_info["anos"]
    print(f"\n{label}")
    for ano in anos:
        since = f"{ano}-01-01T00:00:00Z"
        cursor = None
        tempos = []
        coletados = 0
        while coletados < MAX_POR_ANO:
            after = f', after: "{cursor}"' if cursor else ""
            q = f"""
            {{
              repository(owner: "{owner}", name: "{repo}") {{
                issues(first: 20{after}, states: [CLOSED],
                       filterBy: {{since: "{since}"}},
                       orderBy: {{field: CREATED_AT, direction: ASC}}) {{
                  pageInfo {{ hasNextPage endCursor }}
                  nodes {{
                    createdAt
                    comments(first: 5) {{
                      nodes {{
                        createdAt
                        author {{ __typename login }}
                      }}
                    }}
                  }}
                }}
              }}
            }}
            """
            data = graphql(q)
            try:
                issues    = data["data"]["repository"]["issues"]["nodes"]
                page_info = data["data"]["repository"]["issues"]["pageInfo"]
            except (KeyError, TypeError):
                break
            for issue in issues:
                criado = datetime.fromisoformat(
                    issue["createdAt"].replace("Z", "+00:00")
                )
                if criado.year != ano:
                    continue
                for comentario in issue["comments"]["nodes"]:
                    autor = comentario.get("author", {})
                    if autor and autor.get("__typename") == "User":
                        resp = datetime.fromisoformat(
                            comentario["createdAt"].replace("Z", "+00:00")
                        )
                        tempos.append((resp - criado).days)
                        break
                coletados += 1
                if coletados >= MAX_POR_ANO:
                    break
            if not page_info["hasNextPage"] or coletados >= MAX_POR_ANO:
                break
            cursor = page_info["endCursor"]
        media = np.mean(tempos) if tempos else None
        print(f"  {ano}: {f'{media:.1f} dias' if media is not None else 'sem dados'} "
              f"(N={len(tempos)})")

# ─── M20 — Composição tecnológica ─────────────────────────
print("\n" + "="*50)
print("M20 — Evolução da Composição Tecnológica")
print(f"Amostra: até {MAX_COMMITS} commits/ano")
print("="*50)
EXT_LANG = {
    ".js":    "JavaScript",
    ".ts":    "TypeScript",
    ".py":    "Python",
    ".java":  "Java",
    ".dart":  "Dart",
    ".go":    "Go",
    ".sh":    "Shell",
    ".bzl":   "Starlark",
    ".bazel": "Starlark",
    ".html":  "HTML",
    ".css":   "CSS",
    ".md":    "Markdown",
}
for repo_info in REPOS:
    owner = repo_info["owner"]
    repo  = repo_info["repo"]
    label = repo_info["label"]
    anos  = repo_info["anos"]
    print(f"\n{label}")
    for ano in anos:
        since  = f"{ano}-01-01T00:00:00Z"
        until  = f"{ano}-12-31T23:59:59Z"
        cursor = None
        lang_count = defaultdict(int)
        coletados  = 0
        while coletados < MAX_COMMITS:
            after = f', after: "{cursor}"' if cursor else ""
            q = f"""
            {{
              repository(owner: "{owner}", name: "{repo}") {{
                defaultBranchRef {{
                  target {{
                    ... on Commit {{
                      history(first: 10{after},
                              since: "{since}", until: "{until}") {{
                        pageInfo {{ hasNextPage endCursor }}
                        nodes {{ oid }}
                      }}
                    }}
                  }}
                }}
              }}
            }}
            """
            data = graphql(q)
            try:
                hist      = data["data"]["repository"]["defaultBranchRef"]["target"]["history"]
                nodes     = hist["nodes"]
                page_info = hist["pageInfo"]
            except (KeyError, TypeError):
                break
            for node in nodes:
                sha = node["oid"]
                r2  = requests.get(
                    f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}",
                    headers=HEADERS
                )
                if r2.status_code != 200:
                    continue
                for f in r2.json().get("files", []):
                    nome = f.get("filename", "")
                    ext  = "." + nome.rsplit(".", 1)[-1] if "." in nome else ""
                    lang = EXT_LANG.get(ext, "Outros")
                    lang_count[lang] += 1
                coletados += 1
                if coletados >= MAX_COMMITS:
                    break
            if not page_info["hasNextPage"] or coletados >= MAX_COMMITS:
                break
            cursor = page_info["endCursor"]
        total = sum(lang_count.values())
        if total > 0:
            top = sorted(lang_count.items(), key=lambda x: x[1], reverse=True)[:5]
            print(f"  {ano}: " + " | ".join(
                f"{k}={v/total*100:.0f}%" for k, v in top
            ))

# ─── M21 — Tamanho médio dos commits ──────────────────────
print("\n" + "="*50)
print("M21 — Tamanho Médio dos Commits (linhas alteradas)")
print(f"Mediana = medida principal · Amostra: até {MAX_COMMITS} commits/ano")
print("="*50)
for repo_info in REPOS:
    owner = repo_info["owner"]
    repo  = repo_info["repo"]
    label = repo_info["label"]
    anos  = repo_info["anos"]
    print(f"\n{label}")
    for ano in anos:
        since  = f"{ano}-01-01T00:00:00Z"
        until  = f"{ano}-12-31T23:59:59Z"
        cursor = None
        linhas = []
        coletados = 0
        while coletados < MAX_COMMITS:
            after = f', after: "{cursor}"' if cursor else ""
            q = f"""
            {{
              repository(owner: "{owner}", name: "{repo}") {{
                defaultBranchRef {{
                  target {{
                    ... on Commit {{
                      history(first: 10{after},
                              since: "{since}", until: "{until}") {{
                        pageInfo {{ hasNextPage endCursor }}
                        nodes {{ oid }}
                      }}
                    }}
                  }}
                }}
              }}
            }}
            """
            data = graphql(q)
            try:
                hist      = data["data"]["repository"]["defaultBranchRef"]["target"]["history"]
                nodes     = hist["nodes"]
                page_info = hist["pageInfo"]
            except (KeyError, TypeError):
                break
            for node in nodes:
                sha   = node["oid"]
                r2    = requests.get(
                    f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}",
                    headers=HEADERS
                )
                if r2.status_code != 200:
                    continue
                stats = r2.json().get("stats", {})
                total = stats.get("additions", 0) + stats.get("deletions", 0)
                linhas.append(total)
                coletados += 1
                if coletados >= MAX_COMMITS:
                    break
            if not page_info["hasNextPage"] or coletados >= MAX_COMMITS:
                break
            cursor = page_info["endCursor"]
        s = pd.Series(linhas)
        print(f"  {ano}: mediana={s.median():.0f} · média={s.mean():.0f} (N={len(s)})")

# ─── M22 — Taxa de reabertura de issues ───────────────────
print("\n" + "="*50)
print("M22 — Taxa de Reabertura de Issues (%)")
print("Denominador: issues fechadas (states: CLOSED) · até 100/ano")
print("="*50)
for repo_info in REPOS:
    owner = repo_info["owner"]
    repo  = repo_info["repo"]
    label = repo_info["label"]
    anos  = repo_info["anos"]
    print(f"\n{label}")
    for ano in anos:
        since  = f"{ano}-01-01T00:00:00Z"
        cursor = None
        total     = 0
        reabertas = 0
        coletados = 0
        while coletados < MAX_POR_ANO:
            after = f', after: "{cursor}"' if cursor else ""
            q = f"""
            {{
              repository(owner: "{owner}", name: "{repo}") {{
                issues(first: 20{after}, states: [CLOSED],
                       filterBy: {{since: "{since}"}},
                       orderBy: {{field: CREATED_AT, direction: ASC}}) {{
                  pageInfo {{ hasNextPage endCursor }}
                  nodes {{
                    createdAt
                    timelineItems(first: 1, itemTypes: [REOPENED_EVENT]) {{
                      totalCount
                    }}
                  }}
                }}
              }}
            }}
            """
            data = graphql(q)
            try:
                issues    = data["data"]["repository"]["issues"]["nodes"]
                page_info = data["data"]["repository"]["issues"]["pageInfo"]
            except (KeyError, TypeError):
                break
            for issue in issues:
                criado = datetime.fromisoformat(
                    issue["createdAt"].replace("Z", "+00:00")
                )
                if criado.year != ano:
                    continue
                total += 1
                if issue["timelineItems"]["totalCount"] > 0:
                    reabertas += 1
                coletados += 1
                if coletados >= MAX_POR_ANO:
                    break
            if not page_info["hasNextPage"] or coletados >= MAX_POR_ANO:
                break
            cursor = page_info["endCursor"]
        pct = reabertas / total * 100 if total > 0 else 0
        print(f"  {ano}: {reabertas}/{total} = {pct:.1f}%")

# ─── M23 — Tempo de vida de PRs rejeitados ────────────────
print("\n" + "="*50)
print("M23 — Tempo Médio de Vida de PRs Rejeitados (dias)")
print("Mediana = medida principal · até 100 PRs/ano")
print("="*50)
for repo_info in REPOS:
    owner = repo_info["owner"]
    repo  = repo_info["repo"]
    label = repo_info["label"]
    anos  = repo_info["anos"]
    print(f"\n{label}")
    for ano in anos:
        cursor = None
        tempos = []
        coletados = 0
        while coletados < MAX_POR_ANO:
            after = f', after: "{cursor}"' if cursor else ""
            q = f"""
            {{
              repository(owner: "{owner}", name: "{repo}") {{
                pullRequests(first: 20{after}, states: [CLOSED],
                             orderBy: {{field: CREATED_AT, direction: ASC}}) {{
                  pageInfo {{ hasNextPage endCursor }}
                  nodes {{
                    createdAt
                    closedAt
                    merged
                  }}
                }}
              }}
            }}
            """
            data = graphql(q)
            try:
                prs       = data["data"]["repository"]["pullRequests"]["nodes"]
                page_info = data["data"]["repository"]["pullRequests"]["pageInfo"]
            except (KeyError, TypeError):
                break
            for pr in prs:
                criado = datetime.fromisoformat(
                    pr["createdAt"].replace("Z", "+00:00")
                )
                if criado.year != ano:
                    continue
                if pr["merged"] or not pr["closedAt"]:
                    continue
                fechado = datetime.fromisoformat(
                    pr["closedAt"].replace("Z", "+00:00")
                )
                tempos.append((fechado - criado).days)
                coletados += 1
                if coletados >= MAX_POR_ANO:
                    break
            if not page_info["hasNextPage"] or coletados >= MAX_POR_ANO:
                break
            cursor = page_info["endCursor"]
        s = pd.Series(tempos)
        if len(s) > 0:
            print(f"  {ano}: mediana={s.median():.1f} · média={s.mean():.1f} (N={len(s)})")
        else:
            print(f"  {ano}: sem dados")

# ─── M24 — Issues fechadas sem interação humana ───────────
print("\n" + "="*50)
print("M24 — Proporção de Issues Fechadas sem Interação Humana (%)")
print("Interação humana = comentário com autor __typename == User antes do fechamento")
print("Examina até 10 comentários por issue · até 100 issues/ano")
print("="*50)
for repo_info in REPOS:
    owner = repo_info["owner"]
    repo  = repo_info["repo"]
    label = repo_info["label"]
    anos  = repo_info["anos"]
    print(f"\n{label}")
    for ano in anos:
        since  = f"{ano}-01-01T00:00:00Z"
        cursor = None
        total              = 0
        sem_interacao_hum  = 0
        coletados          = 0
        while coletados < MAX_POR_ANO:
            after = f', after: "{cursor}"' if cursor else ""
            q = f"""
            {{
              repository(owner: "{owner}", name: "{repo}") {{
                issues(first: 20{after}, states: [CLOSED],
                       filterBy: {{since: "{since}"}},
                       orderBy: {{field: CREATED_AT, direction: ASC}}) {{
                  pageInfo {{ hasNextPage endCursor }}
                  nodes {{
                    createdAt
                    closedAt
                    comments(first: 10) {{
                      nodes {{
                        createdAt
                        author {{ __typename login }}
                      }}
                    }}
                  }}
                }}
              }}
            }}
            """
            data = graphql(q)
            try:
                issues    = data["data"]["repository"]["issues"]["nodes"]
                page_info = data["data"]["repository"]["issues"]["pageInfo"]
            except (KeyError, TypeError):
                break
            for issue in issues:
                criado = datetime.fromisoformat(
                    issue["createdAt"].replace("Z", "+00:00")
                )
                if criado.year != ano:
                    continue
                fechado_em = None
                if issue.get("closedAt"):
                    fechado_em = datetime.fromisoformat(
                        issue["closedAt"].replace("Z", "+00:00")
                    )
                tem_comentario_humano = False
                for comentario in issue["comments"]["nodes"]:
                    autor = comentario.get("author", {})
                    if autor and autor.get("__typename") == "User":
                        if fechado_em:
                            data_coment = datetime.fromisoformat(
                                comentario["createdAt"].replace("Z", "+00:00")
                            )
                            if data_coment <= fechado_em:
                                tem_comentario_humano = True
                                break
                        else:
                            tem_comentario_humano = True
                            break
                total += 1
                if not tem_comentario_humano:
                    sem_interacao_hum += 1
                coletados += 1
                if coletados >= MAX_POR_ANO:
                    break
            if not page_info["hasNextPage"] or coletados >= MAX_POR_ANO:
                break
            cursor = page_info["endCursor"]
        pct = sem_interacao_hum / total * 100 if total > 0 else 0
        print(f"  {ano}: {sem_interacao_hum}/{total} = {pct:.1f}%")

# ─── M25 — Concentração de modificações por arquivo ───────
print("\n" + "="*50)
print("M25 — Concentração de Modificações por Arquivo")
print("Top 20 arquivos · 300 commits recentes · exclui dependências e lockfiles")
print("="*50)
EXCLUIR_ARQUIVOS = {
    "package.json", "package-lock.json", "yarn.lock",
    "pnpm-lock.yaml", "MODULE.bazel.lock", "CHANGELOG.md"
}
EXCLUIR_EXT  = {".lock", ".snap"}
TOP_N        = 20
MAX_COMMITS_M25 = 300


def excluir_arquivo(nome):
    base = nome.split("/")[-1]
    if base in EXCLUIR_ARQUIVOS:
        return True
    ext = "." + base.rsplit(".", 1)[-1] if "." in base else ""
    return ext in EXCLUIR_EXT


for repo_info in REPOS:
    owner = repo_info["owner"]
    repo  = repo_info["repo"]
    label = repo_info["label"]
    print(f"\n{label}")

    arquivo_autores = defaultdict(set)
    arquivo_count   = defaultdict(int)
    cursor    = None
    coletados = 0

    while coletados < MAX_COMMITS_M25:
        after = f', after: "{cursor}"' if cursor else ""
        q = f"""
        {{
          repository(owner: "{owner}", name: "{repo}") {{
            defaultBranchRef {{
              target {{
                ... on Commit {{
                  history(first: 20{after}) {{
                    pageInfo {{ hasNextPage endCursor }}
                    nodes {{
                      oid
                      author {{ user {{ login }} }}
                    }}
                  }}
                }}
              }}
            }}
          }}
        }}
        """
        data = graphql(q)
        try:
            hist      = data["data"]["repository"]["defaultBranchRef"]["target"]["history"]
            nodes     = hist["nodes"]
            page_info = hist["pageInfo"]
        except (KeyError, TypeError):
            break
        for node in nodes:
            sha   = node["oid"]
            user  = (node.get("author") or {}).get("user")
            login = user.get("login") if user else None
            if not login:
                continue
            r2 = requests.get(
                f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}",
                headers=HEADERS
            )
            if r2.status_code != 200:
                continue
            for f in r2.json().get("files", []):
                nome = f.get("filename", "")
                if nome and not excluir_arquivo(nome):
                    arquivo_autores[nome].add(login)
                    arquivo_count[nome] += 1
            coletados += 1
            if coletados >= MAX_COMMITS_M25:
                break
        if not page_info["hasNextPage"] or coletados >= MAX_COMMITS_M25:
            break
        cursor = page_info["endCursor"]

    top = sorted(arquivo_count.items(), key=lambda x: x[1], reverse=True)[:TOP_N]
    dados = [
        {"arquivo": a.split("/")[-1], "modificacoes": c,
         "autores": len(arquivo_autores[a])}
        for a, c in top
    ]
    df = pd.DataFrame(dados)
    print(f"  Média autores distintos (top {TOP_N}): {df['autores'].mean():.1f}")
    print(f"  Mediana: {df['autores'].median():.1f}")
    print(df.to_string(index=False))

# ─── M26 — Frequência de commits de correção ──────────────
print("\n" + "="*50)
print("M26 — Frequência de Commits de Correção (%)")
print("Termos: fix, bug, hotfix, patch, bugfix, revert (primeira linha da mensagem)")
print("Amostra: até 100 commits/ano")
print("="*50)
TERMOS_CORRETIVOS = ["fix", "bug", "hotfix", "patch", "bugfix", "revert"]

for repo_info in REPOS:
    owner = repo_info["owner"]
    repo  = repo_info["repo"]
    label = repo_info["label"]
    anos  = repo_info["anos"]
    print(f"\n{label}")
    for ano in anos:
        since  = f"{ano}-01-01T00:00:00Z"
        until  = f"{ano}-12-31T23:59:59Z"
        cursor = None
        mensagens = []
        coletados = 0
 while coletados < MAX_COMMITS_M26:
            after = f', after: "{cursor}"' if cursor else ""
            q = f"""
            {{
              repository(owner: "{owner}", name: "{repo}") {{
                defaultBranchRef {{
                  target {{
                    ... on Commit {{
                      history(first: 20{after},
                              since: "{since}", until: "{until}") {{
                        pageInfo {{ hasNextPage endCursor }}
                        nodes {{ message }}
                      }}
                    }}
                  }}
                }}
              }}
            }}
            """
            data = graphql(q)
            try:
                hist      = data["data"]["repository"]["defaultBranchRef"]["target"]["history"]
                nodes     = hist["nodes"]
                page_info = hist["pageInfo"]
            except (KeyError, TypeError):
                break
            mensagens.extend([n["message"] for n in nodes])
            coletados += len(nodes)
            if not page_info["hasNextPage"] or coletados >= MAX_COMMITS_M26:
                break
            cursor = page_info["endCursor"]

        corretivos = sum(
            1 for m in mensagens
            if any(t in m.split("\n")[0].lower() for t in TERMOS_CORRETIVOS)
        )
        total = len(mensagens)
        pct   = corretivos / total * 100 if total > 0 else 0
        print(f"  {ano}: {corretivos}/{total} = {pct:.1f}%")
