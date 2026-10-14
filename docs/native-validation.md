# Conferir nos aplicativos

Status desta entrega: validação estrutural e cálculos de referência executados; abertura, atualização M e execução DAX no Power BI Desktop e recálculo nativo no Microsoft Excel ainda não executados.

## Power BI Desktop

1. Abra powerbi/FinancialPerformance.pbip no Desktop recente.
2. Clique em Atualizar. Confirme que as consultas embarcadas carregam sem erro.
3. Confira as sete páginas, títulos, filtros e ausência de sobreposição.
4. Selecione 2025/Todas e compare receita, gastos e resultado anual com a tabela do README.
5. Abra Projeção / EAC e selecione setembro. Compare o caso Base com a prévia e o Excel em Base, receita 0% e gastos 0%.
6. Selecione dezembro. O restante deve ser zero e o EAC deve coincidir com o realizado anual.
7. Selecione janeiro e 2024/Engenharia. Confirme que mês, ano e área têm o mesmo escopo nas tabelas e indicadores.
8. Salve capturas reais em docs/images somente depois de conferir os visuais. Identifique-as como Power BI Desktop, preservando as capturas web atuais.

## Microsoft Excel

1. Abra excel/FinancialPerformance.xlsx e aguarde o recálculo.
2. Teste Painel B3/E3/H3 e compare o caso Base com o README.
3. Em Projeção L37 selecione Otimista e Conservativo. Confira os ajustes ativos em L40/L46 e a atualização do Build-up e do gráfico.
4. Com setembro e Base, edite L41 de 0% para 1%. Receita projetada e resultado devem mudar; realizado até corte deve permanecer igual. Restaure 0%.
5. Em dezembro, cenários diferentes devem chegar ao mesmo realizado anual.
6. Confira fórmulas, quatro gráficos e valores mensais somando o EAC, sem erro de fórmula. Salve e reabra.

## Registrar evidência

Anote versão do aplicativo, data, filtros, valores comparados e resultado da conferência. Atualize verification.md somente com verificações efetivamente realizadas. Os testes automatizados e o parser do modelo não confirmam renderização ou cálculo no aplicativo nativo.
