# Premissas da simulação

Todos os valores são fictícios; o caso pode ser reproduzido com semente 42.

## Projeção / EAC

A estimativa de fechamento usa o realizado de janeiro até o mês de referência e o orçamento dos meses restantes, com a mesma área e ano. O corte inicial é setembro. Não utiliza o realizado futuro, nem extrapola a tendência dos meses anteriores. Em dezembro, todo o ano é realizado e a projeção restante é zero.

Esta premissa não estima carryover, risco de não execução, compromissos de contratos ou ajustes manuais. Os motivadores apresentam os desvios calculados e as regras fictícias da simulação abaixo, sem provar causalidade em dados alterados.

Na prévia e no Excel, percentuais editáveis ajustam receita e gastos futuros sobre o orçamento: Base 0%/0%, Otimista +5%/−3% e Conservativo −5%/+3%. São valores ilustrativos, não calibrados a dados operacionais. O fator é 1 + percentual; cada categoria/mês é arredondada ao centavo antes dos totais. Histórico e orçamento original permanecem iguais. O Power BI mantém o caso Base. Campos ausentes ou percentuais fora de −100% a 100% não são tratados como zero.

| Premissa | Regra |
| :--- | :--- |
| Receita mensal base de 2024 | Analytics R$ 230 mil; Engenharia R$ 320 mil; Operações R$ 180 mil |
| Orçamento de 2025 | Crescimento de 12% sobre a base |
| Sazonalidade | Fatores mensais de 0,90 a 1,12, definidos no gerador |
| Custos diretos | 22% da receita orçada |
| Pessoal | 30% da receita orçada |
| Tecnologia | 7% da receita orçada |
| Comercial | 5,5% da receita orçada |
| Administrativo | 6,5% da receita orçada |
| Margem orçada | 29% |

O realizado recebe pequenas variações determinísticas. Em 2025, o gerador simula menor receita em Engenharia de junho a outubro, menor receita em Analytics de julho a setembro, gasto adicional de tecnologia desde março, de pessoal em Engenharia desde julho e comercial em Analytics no último trimestre.

Custos diretos acompanham a receita realizada. As demais categorias partem do orçamento e recebem os fatores do código. As premissas são hipotéticas; a análise mede seus efeitos na base gerada, sem estimar causalidade em uma empresa real. Valores são arredondados para centavos antes de exportar; cálculos Python usam Decimal.
