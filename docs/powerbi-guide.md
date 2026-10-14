# Abrir e atualizar o Power BI

1. Extraia o pacote completo e mantenha as pastas juntas.
2. Abra powerbi/FinancialPerformance.pbip no Power BI Desktop recente.
3. Clique em **Atualizar** para carregar os CSV embarcados. O projeto contém definições, não um cache pré-carregado.
4. O ano começa em 2025. Os filtros de ano e área estão sincronizados nas sete páginas. Build-up, Motivadores, Mensal e Projeção compartilham o mês de referência, inicialmente setembro.

Se sua versão pedir habilitação de projetos/TMDL/PBIR, consulte suas opções de versão prévia ou atualize para uma versão que suporte os formatos. O Desktop otimizado para Report Server não é o alvo.

## Organização do relatório

- **Visão executiva:** quatro indicadores no topo, evolução mensal à esquerda, desvios e comparação anual à direita, tabela mensal abaixo.
- **Orçado × realizado:** indicadores do orçamento, comparação mensal, impactos por categoria e tabela com valores e percentuais.
- **Build-up:** cascata de gastos EAC por categoria, com realizado até corte e orçamento restante separados na tabela e nos indicadores.
- **Motivadores:** impactos favoráveis e desfavoráveis nos gastos, separados da receita para conciliar o resultado.
- **Visão mensal:** orçamento, realizado e desvio do mês escolhido, com resultado acumulado de janeiro até ele.
- **Projeção / EAC:** resultado estimado de fechamento e detalhamento dos valores usados em cada mês.
- **Áreas e categorias:** impactos no resultado e comparação das áreas, com detalhamento por categoria logo abaixo.

Os sete layouts usam a mesma base fictícia e a mesma identidade própria. As tabelas são visuais nativos e permitem rolagem para consultar o detalhe. A cascata nativa do Power BI mostra o EAC das categorias, enquanto a prévia e o Excel também separam as parcelas dentro das colunas.

EAC = realizado de janeiro até referência + orçamento restante. O seletor independente Corte não filtra o calendário: as medidas aplicam o corte, preservando todo o ano para a estimativa. Em dezembro, o EAC corresponde ao realizado anual. Se o mês for desmarcado, o padrão das medidas é setembro. As medidas de corte/EAC ficam vazias sem um único ano no contexto.

## Ler os CSV da pasta

Em **Transformar dados → Gerenciar parâmetros**, preencha pDataFolder com o caminho absoluto da pasta data, sem aspas. Feche/aplique e atualize.

Com o parâmetro vazio, o exemplo usa uma cópia embarcada dos CSV desta entrega. Substituir CSV na pasta não atualiza essa cópia: configure o parâmetro ou gere novamente o projeto.

Consultas usam UTF-8 e cultura en-US. O fato recusa duplicatas, chaves/cenários inválidos, cobertura incompleta e sinais incompatíveis. As dimensões devem manter as chaves e tipos do dicionário.

## Editar e salvar

As 36 medidas estão em Financas, pasta Indicadores, e no arquivo measures.dax. O modelo usa cinco tabelas e três relações. Corte contém os 12 meses como controle independente. Os meses e as categorias têm colunas de ordenação.

A comparação anual fica vazia quando há mais de um ano no contexto ou não existe ano anterior comparável. Isso evita comparar 24 meses com somente 12 meses disponíveis.

Para gerar PBIX, use **Arquivo → Salvar como** no Desktop após atualizar e conferir o relatório. O arquivo entregue é um PBIP editável.

## Limite da validação

JSON validado contra esquemas Microsoft; TMDL aceito pelo parser Microsoft com cinco tabelas, três relações e 36 medidas. Isso não executa DAX, atualiza M ou confirma a aparência dos visuais. A abertura visual e a atualização nativa precisam ser conferidas no aplicativo.

As imagens do README são capturas da prévia web.

## Referências

- [PBIP](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview)
- [PBIR](https://learn.microsoft.com/en-us/power-bi/developer/embedded/projects-enhanced-report-format)
- [Modelo semântico](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-dataset)
- [Cascata nativa](https://learn.microsoft.com/pt-br/power-bi/visuals/power-bi-visualization-waterfall-charts)
