# Usar a planilha

Abra excel/FinancialPerformance.xlsx. Na aba Painel, escolha o ano em B3, a área em E3 e o mês de referência em H3 (1–12, inicialmente 9). Ano e área alimentam todas as saídas. O mês controla Build-up e Projeção; o Painel mantém a análise anual.

Desvio positivo é favorável. Em gastos, exibidos positivos, desvio favorável = orçado − realizado. Na margem, a diferença é em pontos percentuais.

## Organização do painel

As abas são Painel, Build-up, Projeção e Base. Os filtros editáveis ficam apenas no Painel; as outras duas saídas mostram as seleções por fórmulas.

- **Painel:** análise anual, evolução mensal, áreas e categorias.
- **Build-up:** composição dos gastos em cascata, realizado/projetado e tabela de desvios favoráveis.
- **Projeção:** EAC, conciliação por categoria e mês, com receita positiva e gastos negativos no detalhamento.
- **Base:** 864 registros fictícios originais, preservados e tipados.

EAC = realizado até o mês de referência + orçamento dos meses restantes. Em dezembro, o restante é zero. Valores realizados depois do corte não entram na projeção. A margem total usa receita e resultado totais.

## Cenários

Na Projeção, L37 é o único seletor de cenário. L41:L43 contêm premissas de receita futura e L47:L49, de gastos futuros. As células amarelas são editáveis: digite **5%**, e não o número 5. Base começa em 0%/0%; Otimista em +5%/−3%; Conservativo em −5%/+3%. Estes valores são ilustrativos.

As linhas ativas L40/L46 selecionam as premissas do caso. Elas alimentam o orçamento projetado por categoria/mês em A56:M63, arredondado ao centavo. O detalhe, o EAC e o Build-up usam esse mesmo cálculo. O orçamento anual e o realizado até corte permanecem iguais. Em dezembro, os cenários convergem para o realizado anual. Use percentuais entre −100% e 100%; premissa ativa ausente ou inválida fica visível como erro, sem substituir por zero.

A cascata é um gráfico editável de colunas empilhadas com uma base acumulada sem preenchimento. Os cálculos ficam visíveis abaixo da tabela de gastos. Azul identifica realizado, âmbar identifica projetado e cinza identifica o orçamento anual. Os quatro gráficos mantêm referências a células e se atualizam com os filtros.

## Atualizar

A Base tem 864 linhas: Data, Ano, Área, Categoria, Natureza, Cenário e Valor. As fórmulas usam SUMIFS; não são apenas resultados colados.

Valide os CSV e substitua as linhas preservando colunas, datas numéricas, valores numéricos e rótulos das dimensões. O contrato atual cobre 2024–2025. Ampliação exige ajustar os intervalos das fórmulas.

A planilha não tem conexão Power Query salva nem é reconstruída pelo workflow. O Power Query de atualização automática está no Power BI; a troca da Base do Excel é manual.

## Verificação

Receita, gastos, resultado e margem reconciliaram com Python nos oito filtros anuais e nos 96 recortes EAC de dois anos, quatro seleções de área e 12 meses. O mecanismo de autoria recalculou a planilha e os painéis foram renderizados e inspecionados.

Os três casos iniciais também reconciliaram em 288 recortes. O arquivo preserva fórmulas, quatro listas de seleção, quatro abas e quatro gráficos. Não foi aberto no Microsoft Excel para confirmar comportamento nativo. Veja user-guide.md e native-validation.md.
