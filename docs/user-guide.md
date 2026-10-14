# Como usar o projeto

Este caso usa dados fictícios de 2024–2025. O resultado operacional simplificado é receita menos gastos; não representa lucro líquido, caixa ou EBITDA completo.

## 1. Abra a demonstração

Baixe e extraia o pacote. Entre na pasta financial-performance-analytics e abra preview/index.html no navegador. Mantenha as demais pastas juntas para os links de Excel, dados e documentação funcionarem. A prévia não precisa de servidor, instalação ou internet.

Depois da publicação no GitHub Pages, a demonstração também poderá ser aberta online. O endereço só estará ativo após o workflow de publicação concluir.

## 2. Comece pelo recorte

Na Visão executiva, escolha **2025** e **Todas as áreas**. Ano e área afetam todas as abas. Compare receita, gastos, resultado e margem com o orçamento. Depois selecione **Engenharia** para investigar o desvio desse recorte. Volte para Todas as áreas quando quiser o consolidado.

As abas anuais mostram o ano inteiro. O mês de referência aparece nas abas que precisam de um recorte mensal ou de projeção.

## 3. Siga esta ordem de leitura

| Aba | Pergunta que responde | Como ler |
| :--- | :--- | :--- |
| Visão executiva | Como está o resultado do ano? | Indicadores, evolução mensal e pontos de atenção |
| Orçado × realizado | Quanto ficou acima ou abaixo do plano? | Desvio em reais e percentual, comparando os mesmos períodos |
| Áreas e categorias | Onde está a diferença? | Impactos por categoria e comparação de áreas |
| Visão mensal | O que ocorreu no mês e no acumulado? | Mês escolhido separado do YTD, de janeiro até o corte |
| Build-up | Como os gastos formam o fechamento? | Azul realizado, âmbar projetado; linha tracejada é o orçamento anual |
| Motivadores | Quais gastos aumentaram e quais compensaram? | Economias, aumentos e impacto da receita conciliam o desvio |
| Projeção / EAC | Qual seria o fechamento com estas premissas? | Realizado até o corte somado à projeção dos meses restantes |

## 4. Teste o EAC

Abra Projeção / EAC. Escolha **setembro** e o cenário **Base**, com receita e gastos em **0%**. Esse caso reproduz o orçamento dos meses seguintes, somado ao realizado de janeiro a setembro. O realizado de outubro a dezembro da base fica fora da estimativa.

Troque para **dezembro**: não restam meses futuros, portanto o EAC deve coincidir com o realizado anual em qualquer cenário. Retorne a setembro para explorar as premissas.

## 5. Compare premissas de forecast

Os cenários estão disponíveis na prévia e no Excel. No Power BI, o EAC mantém a regra Base de realizado até o corte + orçamento restante.

| Cenário inicial | Receita futura vs. orçamento | Gastos futuros vs. orçamento |
| :--- | ---: | ---: |
| Base | 0% | 0% |
| Otimista | +5% | −3% |
| Conservativo | −5% | +3% |

São exemplos editáveis, não previsões estimadas dos dados. Cada percentual se aplica uniformemente às categorias correspondentes dos meses após o corte. A projeção arredonda cada categoria/mês ao centavo e soma o detalhe.

Na prévia, escolha um cenário e edite os dois percentuais. **Digite 5 para 5%**. As mudanças afetam Build-up, Motivadores e Projeção / EAC; a Visão mensal e as abas anuais preservam a análise histórica. Alterações duram apenas nesta sessão. **Restaurar premissas** recupera os valores iniciais dos três casos.

Percentuais positivos aumentam o orçamento futuro; negativos reduzem. Por exemplo, gastos +3% aumentam despesas e tendem a reduzir o resultado. Limite dos campos: −100% a +100%.

## 6. Use o Excel

Abra excel/FinancialPerformance.xlsx. Na aba **Painel**, selecione ano em **B3**, área em **E3** e mês de referência de 1 a 12 em **H3**.

Na aba **Projeção**, selecione o cenário em **L37**. Edite as células amarelas **L41:L43** para receita e **L47:L49** para gastos. **Digite 5% no Excel**, e não o número 5. As linhas ativas L40/L46 alimentam a mesma projeção; o Build-up acompanha o cenário selecionado. As premissas ficam abaixo dos indicadores, ao lado do detalhe mensal.

Base contém os registros originais. Não substitua fórmulas por valores. Para alterar fontes, siga excel-guide.md e preserve o contrato de linhas, datas e categorias. A abertura e o recálculo nativos ainda precisam ser conferidos no Microsoft Excel.

## 7. Use o Power BI

Abra powerbi/FinancialPerformance.pbip no Power BI Desktop. Atualize os dados embarcados, selecione um ano e uma área e percorra as sete páginas. Nas páginas com corte, selecione um mês por vez. O EAC nativo usa o caso Base; os ajustes editáveis de cenários estão na prévia e no Excel.

Antes de usar capturas como evidência do Power BI, confirme renderização, atualização M e medidas DAX conforme native-validation.md. Consulte powerbi-guide.md para usar uma pasta externa de CSV.

## 8. Interprete os sinais e limites

- Desvio de resultado positivo é favorável: realizado/EAC acima do orçamento.
- Gastos aparecem positivos nos indicadores. Seu desvio favorável é orçamento menos realizado/EAC: negativo significa gastos acima do plano.
- Na tabela com sinal financeiro, despesas são negativas; receitas são positivas.
- Diferença de margem é medida em pontos percentuais. Margem total usa resultado total dividido pela receita total.
- Um traço indica percentual sem denominador ou comparação indisponível, não zero.

As premissas da simulação não provam causas reais. O relatório não estima carryover, riscos, volume/preço, contratos ou integração SAP. Confira as recomendações em management-actions.md.

## Se algo não aparecer

Extraia o ZIP antes de abrir. Para filtros, permita JavaScript no navegador. Se estiver bloqueado, leia este guia e findings.md no próprio GitHub ou use a planilha. Na tela pequena, arraste a tabela ou cascata dentro do painel para ver todas as colunas. Os filtros da prévia não alteram os CSV nem o Excel; cada arquivo tem seus próprios controles.
