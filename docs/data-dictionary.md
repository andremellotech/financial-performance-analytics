# Dicionário dos dados

Fonte: simulação gerada por scripts/generate_data.py, semente 42. Os dados não representam pessoas, clientes ou uma empresa real.

Cada registro de fact_finance.csv representa **mês × área × categoria × cenário**, em BRL.

| Campo | Tipo | Significado |
| :--- | :--- | :--- |
| month | Data ISO | Primeiro dia do mês, de 2024-01-01 a 2025-12-01 |
| area_id | Texto | ANA, ENG ou OPS |
| category_id | Texto | REV, DIR, PES, TEC, COM ou ADM |
| scenario | Texto | Orçado ou Realizado |
| amount_brl | Decimal | Duas casas; receita positiva e gastos negativos |

Chave única: month,area_id,category_id,scenario. São 864 registros: 24 × 3 × 6 × 2.

CSV em UTF-8, delimitador vírgula e decimal com ponto. O Power Query usa cultura en-US para ler datas ISO e decimais.

## Dimensões

- dim_area.csv: area_id, area_name; três áreas.
- dim_category.csv: category_id, category_name, nature, sort_order; seis categorias.
- dim_calendar.csv: date, year, month, month_name, year_month, year_month_order; 731 datas consecutivas, incluindo 29/02/2024.

## Modelo

Calendario[Data] → Financas[Data]  
Areas[AreaId] → Financas[AreaId]  
Categorias[CategoriaId] → Financas[CategoriaId]

Dimensões filtram os fatos em relações de um para muitos. O calendário diário suporta a comparação anual do fato mensal. dashboard.json contém dados e cálculos derivados para a prévia.

A tabela **Corte**, com os 12 meses, é um controle independente no Power BI. Não tem relação com os fatos: suas medidas usam o mês selecionado para separar realizado e orçamento restante. A seleção padrão é setembro. As quatro tabelas e os CSV originais permanecem iguais.

dashboard.json inclui referências de EAC para 96 recortes e referências mensal/acumulado para verificação. Essas saídas são calculadas, não um terceiro cenário de dados reais.

Os validadores recusam cenário/chave desconhecidos, duplicatas, cobertura incompleta, valores não finitos, casas decimais incompatíveis e sinais inválidos. O contrato desta versão está fechado em 2024–2025; ampliar o horizonte exige ajustar calendário, validação, consultas e a área de dados da planilha.
