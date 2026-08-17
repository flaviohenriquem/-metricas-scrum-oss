# Mapeamento de Métricas — Catálogo de Gestão para Equipes Ágeis

Documento de referência para o catálogo de 26 métricas derivado do
Mapeamento Sistemático da Literatura (MSL) conduzido segundo as
diretrizes PRISMA (106 estudos, 2019–2025).

Dissertação: *Um Catálogo de Métricas de Gestão para Equipes Ágeis*
COMPMAT/UERJ, 2026.

---

## Dimensões e métricas

| ID | Nome | Tipo | Dimensão | API |
|----|------|------|----------|-----|
| M01 | Cadência de Commits | Direta | Fluxo e Progresso | REST |
| M02 | Tempo de Ciclo de Pull Request | Derivada | Fluxo e Progresso | REST |
| M03 | Taxa de PRs Fechados sem Merge | Derivada | Fluxo e Progresso | REST |
| M04 | Tempo Médio entre Commits | Derivada | Fluxo e Progresso | REST |
| M07 | Engajamento de Colaboradores | Direta | Fluxo e Progresso | REST |
| M13 | Granularidade dos Pull Requests | Derivada | Fluxo e Progresso | REST |
| M21 | Tamanho Médio dos Commits | Derivada | Fluxo e Progresso | GraphQL+REST |
| M23 | Tempo Médio de Vida de PRs Fechados sem Merge | Derivada | Fluxo e Progresso | GraphQL |
| M26 | Frequência de Commits de Correção | Derivada | Fluxo e Progresso | GraphQL |
| M05 | Taxa de Resolução de Issues | Derivada | Qualidade e Estabilidade | REST |
| M06 | Tempo Médio de Resolução de Issues | Derivada | Qualidade e Estabilidade | REST |
| M19 | Tempo de Primeira Resposta Humana | Derivada | Qualidade e Estabilidade | GraphQL |
| M20 | Evolução da Composição Tecnológica | Derivada | Qualidade e Estabilidade | GraphQL+REST |
| M22 | Taxa de Reabertura de Issues | Derivada | Qualidade e Estabilidade | GraphQL |
| M24 | Issues Fechadas sem Interação Humana | Derivada | Qualidade e Estabilidade | GraphQL |
| M16 | Cadência de Releases | Derivada | Planejamento e Estimativa | REST |
| M17 | Idade Média de Issues Abertas | Derivada | Planejamento e Estimativa | REST |
| M18 | Visibilidade Externa do Repositório | Direta | Valor e Alinhamento Estratégico | REST |
| M08 | Concentração de Contribuições (Gini) | Derivada | Fatores Humanos | REST |
| M09 | Proporção de Core Team | Derivada | Fatores Humanos | REST |
| M10 | Taxa de Retenção de Contribuidores | Derivada | Fatores Humanos | REST |
| M11 | Longevidade Média dos Contribuidores | Derivada | Fatores Humanos | REST |
| M12 | Proporção de Novos Contribuidores | Derivada | Fatores Humanos | REST |
| M14 | Taxa de Conversão de Novatos | Derivada | Fatores Humanos | REST |
| M15 | Proporção de Contribuidores Ocasionais | Derivada | Fatores Humanos | REST |
| M25 | Concentração de Modificações por Arquivo | Derivada | Fatores Humanos | GraphQL+REST |

---

## Métricas com amostragem

| ID | Unidade | Limite |
|----|---------|--------|
| M13 | PRs merged mais recentes | 300 |
| M19 | Issues fechadas por ano | 100 |
| M20 | Commits por ano | 50 |
| M21 | Commits por ano | 50 |
| M22 | Issues fechadas por ano | 100 |
| M23 | PRs fechados sem merge por ano | 100 |
| M24 | Issues fechadas por ano | 100 |
| M25 | Commits recentes (histórico completo) | 300 |
| M26 | Commits por ano | 100 |

---

## Notas metodológicas

- **M01**: desvio padrão calculado com divisor n-1 (estimador amostral).
- **M04**: calcula intervalo entre timestamps completos de commits
  consecutivos (não entre dias distintos). Commits no mesmo dia em
  horários diferentes produzem intervalos fracionários, truncados para
  dias inteiros no cálculo, o que explica valores médios baixos como
  0,13 dia em projetos com múltiplos commits diários.
- **M13**: coleta os PRs merged mais recentes retornados pela API
  (ordem decrescente por data de criação), não uma amostra aleatória.
- **M16**: AngularJS não possui releases formais no GitHub; o cálculo
  utilizou tags git com data extraída do commit associado.
- **M19**: considera apenas comentários de autores identificados como
  `User` pela API GraphQL, nos primeiros 5 comentários de cada issue.
- **M20**: extensões mapeadas explicitamente em tabela de correspondência;
  extensões não mapeadas são classificadas como "Outros", e não excluídas
  do cômputo.
- **M21**: mediana é a medida principal; média reportada como
  estatística complementar.
- **M22**: denominador = issues fechadas (`states: CLOSED`).
- **M23**: mediana é a medida principal; média reportada como
  estatística complementar.
- **M26**: amostra própria e independente de M20/M21, de até 100
  commits por ano.

---

- **M24**: interação humana = ao menos um comentário registrado, ou
  evento de rotulagem/fechamento atribuído a uma conta do tipo `User`,
  verificado nos primeiros 5 eventos da linha do tempo de cada issue.
