"""Atualiza README e diagnóstico a partir dos números calculados."""
from pathlib import Path
import html,re
from finance import load_rows,validate_rows,summarize,category_variances,monthly_summary,projection_summary,AREAS
ROOT=Path(__file__).resolve().parents[1]
def money(n):
    return "R$ "+f"{n:,.2f}".replace(",","X").replace(".",",").replace("X",".")
def pct(n):
    return "—" if n is None else f"{n*100:.1f}%".replace(".",",")
def build_docs():
    rows=load_rows(ROOT/"data/fact_finance.csv");validate_rows(rows);s=summarize(rows,2025);eac=projection_summary(rows,2025,9)
    drivers=category_variances(rows);areas=[summarize(rows,2025,a) for a in AREAS]
    metric_rows="\n".join(f"| {label} | {money(s['budget'][key])} | {money(s['actual'][key])} |" for label,key in [("Receita","revenue"),("Gastos","expenses"),("Resultado operacional simplificado","result")])
    metric_rows+=f"\n| Margem | {pct(s['budget']['margin'])} | {pct(s['actual']['margin'])} |"
    worst_area=min(areas,key=lambda a:a["variance"])
    driver_rows="\n".join(f"| {d['label']} | {money(d['variance'])} |" for d in drivers)
    area_rows="\n".join(f"| {AREAS[a['area_id']]} | {money(a['actual']['result'])} | {money(a['variance'])} |" for a in areas)
    monthly=monthly_summary(rows,2025);worst_month=min(monthly,key=lambda m:m["variance"])
    margin_delta=(s["actual"]["margin"]-s["budget"]["margin"])*100 if s["actual"]["margin"] is not None and s["budget"]["margin"] is not None else None
    margin_note=("— (receita zero; diferença de margem indisponível)" if margin_delta is None else f"{margin_delta:.1f}".replace(".",",")+" pontos percentuais")
    area_note=(f"A área de {AREAS[worst_area['area_id']]} teve o maior desvio desfavorável: {money(worst_area['variance'])}." if worst_area["variance"]<0 else "Nenhuma área teve desvio desfavorável.")
    share_note=(f"{AREAS[worst_area['area_id']]} concentrou aproximadamente {pct(abs(worst_area['variance']/s['variance']))} do desvio total." if s["variance"]<0 and worst_area["variance"]<0 else "O desvio total é zero; participação percentual não se aplica." if s["variance"]==0 else "O desvio total foi favorável; a comparação de áreas está na tabela.")
    month_note=(f"O mês com maior desvio desfavorável foi {worst_month['month']}: {money(worst_month['variance'])}." if worst_month["variance"]<0 else "Não houve meses com desvio desfavorável.")
    negative_drivers=[d for d in drivers if d["variance"]<0]
    driver_note=(f"{min(negative_drivers,key=lambda d:d['variance'])['label']} teve o maior impacto desfavorável." if negative_drivers else "Nenhuma categoria teve impacto desfavorável.")
    expense_eac_note=(f"Os gastos EAC ficam {money(abs(eac['expense_variance']))} acima do orçamento." if eac['expense_variance']<0 else f"Os gastos EAC ficam {money(eac['expense_variance'])} abaixo do orçamento." if eac['expense_variance']>0 else "Os gastos EAC ficam em linha com o orçamento.")
    readme=f"""# Financial Performance Analytics

**Um caso de análise financeira: do dado ao diagnóstico do resultado.**

Projeto de portfólio de [André Mello](https://github.com/andremellotech), com Power BI, Power Query, DAX, Excel e Python.

**Versão 1.0.0** · [Como usar](docs/user-guide.md) · [Guia no navegador](docs/user-guide.html) · [Baixar Excel](excel/FinancialPerformance.xlsx)

[Demonstração online — disponível após ativar Pages](https://andremellotech.github.io/financial-performance-analytics/). A publicação ainda depende do envio do repositório e da ativação do workflow.

![Prévia navegável dos dados do projeto](docs/images/dashboard-preview.jpg)

> Dados inteiramente fictícios. A imagem é uma captura da prévia web desta entrega, não do Power BI Desktop. Para dados alterados, abra a prévia atualizada.

## A pergunta de negócio

**Onde o resultado ficou abaixo do planejado e quais fatores explicam o desvio?**

O caso representa uma empresa fictícia de serviços, com Analytics, Engenharia e Operações durante 2024 e 2025. O orçamento de 2025 prevê crescimento; o realizado simula menor receita em parte do ano e pressão de gastos.

O relatório organiza indicadores no topo, evolução mensal com pontos de atenção ao lado e comparação detalhada abaixo. A identidade visual é própria, com azul e âmbar. Nenhum dado ou elemento de identidade de empresa foi utilizado.

## Resultado do caso: 2025

| Indicador | Orçado | Realizado |
| :--- | ---: | ---: |
{metric_rows}

O desvio do resultado foi **{money(s['variance'])} ({pct(s['variance_pct'])})**. {area_note} A decomposição separa receita, gastos e compensações. Veja a [análise completa](docs/findings.md).

Veja também as [recomendações gerenciais](docs/management-actions.md): achados, hipóteses a investigar, dados necessários e ações sugeridas. São propostas sobre o caso fictício, sem economias ou decisões atribuídas a uma empresa real.

## Explore o projeto

- **Prévia navegável:** baixe o repositório e abra [preview/index.html](preview/index.html). As sete perspectivas e os filtros funcionam localmente, sem CDN ou servidor.
- **Power BI:** abra [FinancialPerformance.pbip](powerbi/FinancialPerformance.pbip) no Desktop e clique em **Atualizar** para carregar os dados embarcados. Consulte o [guia do Power BI](docs/powerbi-guide.md).
- **Excel:** abra [FinancialPerformance.xlsx](excel/FinancialPerformance.xlsx) e selecione ano em B3, área em E3 e mês em H3 na aba Painel. Os filtros alimentam Build-up e Projeção. Consulte o [guia do Excel](docs/excel-guide.md).
- **Dados:** [fatos financeiros](data/fact_finance.csv), [dicionário](docs/data-dictionary.md) e [premissas](docs/assumptions.md).

O GitHub apresenta o código do HTML. Para usar a prévia, abra o arquivo localmente ou publique pelo GitHub Pages conforme o [guia de publicação](docs/publish-guide.md).

## O que foi construído

| Camada | Entrega |
| :--- | :--- |
| Dados | 864 registros mensais e dimensões de calendário, área e categoria |
| Tratamento | Consultas Power Query com validação de cobertura, chaves, cenários e sinais |
| Modelo | Cinco tabelas, três relações e 36 medidas DAX; corte mensal independente |
| Relatório | Sete páginas: Executiva, Orçado × realizado, Build-up, Motivadores, Mensal, Projeção/EAC e Áreas |
| Excel | Painel, Build-up, Projeção e Base, com fórmulas, três controles e quatro gráficos |
| Automação | Gerador determinístico, diagnósticos calculados e workflow de validação |

~~~mermaid
flowchart LR
    G[Gerador fictício] --> C[CSV validados]
    C --> M[Power Query e modelo]
    M --> P[Power BI]
    C --> E[Excel]
    C --> W[Prévia navegável]
~~~

O modelo usa PBIP, TMDL e PBIR para manter tabelas, medidas, páginas e visuais em arquivos legíveis para revisão no GitHub. Veja as [medidas DAX](powerbi/measures.dax) e [consultas M](powerbi/queries/).

## Build-up e projeção de fechamento

<details>
<summary>Ver o Build-up da prévia</summary>

![Build-up da prévia web](docs/images/buildup-preview.jpg)

</details>

O Build-up compõe os gastos por categoria e separa realizado até o corte e projeção restante. A aba Motivadores organiza economias e aumentos de gastos, com a receita separada para conciliar o desvio do resultado. A Visão mensal mostra o mês escolhido e o acumulado de janeiro até ele.

**EAC hipotético = realizado até o mês de referência + orçamento dos meses seguintes.** Valores realizados após o corte não entram na estimativa. A referência inicial é setembro, e o seletor permite qualquer mês do ano. Em dezembro, a parcela projetada é zero e o EAC corresponde ao realizado anual.

No exemplo de 2025 com corte em setembro, o resultado EAC é **{money(eac['eac']['result'])}**, contra {money(eac['budget']['result'])} orçados. Os gastos EAC são {money(eac['eac']['expenses'])}. {expense_eac_note} Isso é uma simulação de fechamento, distinta da análise do realizado anual acima.

<details>
<summary>Ver a projeção de fechamento</summary>

![Projeção de fechamento da prévia web](docs/images/forecast-preview.jpg)

</details>

Carryover, risco de não execução, compromissos de contratos e revisão manual de forecast não são estimados por esta base. As explicações dos motivadores descrevem as premissas fictícias, sem atribuir causalidade a dados corporativos.

## Cenários editáveis

Na prévia e no Excel, Base, Otimista e Conservativo selecionam premissas de receita e gastos dos meses após o corte. O histórico permanece igual. Os valores iniciais são ilustrativos e podem ser editados:

| Cenário | Receita futura vs. orçamento | Gastos futuros vs. orçamento |
| :--- | ---: | ---: |
| Base | 0% | 0% |
| Otimista | +5% | −3% |
| Conservativo | −5% | +3% |

**EAC com cenário = realizado até o corte + orçamento futuro ajustado pelas premissas.** A projeção é arredondada por categoria/mês ao centavo antes dos totais. O Power BI mantém o EAC Base, sem os campos de ajuste de cenário. Consulte o [passo a passo](docs/user-guide.md) para localizar os controles e restaurar as premissas.

## Regras financeiras

Receitas são positivas; custos e despesas são negativos na base. O resultado é a soma dos valores. O indicador de gastos exibe sua magnitude positiva.

- Desvio do resultado = realizado − orçado; positivo é favorável.
- Desvio percentual = desvio / resultado orçado absoluto.
- Margem = resultado / receita no mesmo período e área.
- Comparação anual = realizado do ano anterior, com a mesma área.
- Sem denominador ou comparável, o indicador fica vazio, representado por — na prévia.

Não há impostos, resultado financeiro, depreciação ou integração com SAP nesta versão.

## Reproduza e valide

Python 3.11+, Node.js 24 para os testes da prévia e Power BI Desktop recente para editar o relatório.

~~~sh
python -m pip install -r scripts/requirements.txt
python scripts/generate_data.py
python scripts/validate_data.py
python scripts/build_powerbi.py
python scripts/validate_powerbi.py
python scripts/build_preview.py
python scripts/build_docs.py
python -m unittest discover -s tests
node tests/test_preview.js
node tests/test_scenarios.js
~~~

A semente 42 reproduz a mesma base. O workflow roda os testes e verifica divergências nos materiais gerados. A planilha não é reconstruída pelos comandos Python: atualize a Base conforme o guia do Excel.

Para reconstruir a partir de CSV já editados, execute **python scripts/build_all.py**. Esse comando preserva os CSV e renova o projeto, a prévia e os textos. O gerador de dados é uma ação separada que restaura a simulação original. As capturas do README são imagens desta entrega e não são renovadas pelo workflow.

## Verificação da entrega

Cálculos Python, JavaScript e Excel reconciliados nos oito filtros anuais e nos 96 recortes de EAC por ano/área/mês. Os resumos mensal e acumulado também reconciliam. JSON Power BI validado contra esquemas Microsoft; modelo TMDL aceito pelo parser oficial. Consulte a [verificação da entrega](docs/verification.md).

Os três cenários iniciais foram comparados em 288 recortes de ano/área/mês. Consulte também a [validação nos aplicativos](docs/native-validation.md), o [histórico de versões](CHANGELOG.md) e as [notas para publicar v1.0.0](docs/release-notes.md). A versão identifica o pacote local; a Release no GitHub ainda não foi publicada.

**Abertura visual, execução DAX e atualização M no Power BI Desktop ainda precisam de validação no aplicativo.** Validação de arquivos não confirma a renderização nativa. A planilha também não foi aberta no Microsoft Excel.

## Autor e licença

[André Mello](https://www.linkedin.com/in/aamello/) · [GitHub](https://github.com/andremellotech)

Código e dados fictícios sob [MIT](LICENSE). Os esquemas Microsoft mantêm a [licença de origem](docs/schemas/LICENSE).
"""
    findings=f"""# Análise do caso fictício

Recorte: 2025, todas as áreas. Valores calculados a partir de data/fact_finance.csv.

## Resultado

Resultado realizado de {money(s['actual']['result'])}, contra {money(s['budget']['result'])} orçados. Desvio de {money(s['variance'])} ({pct(s['variance_pct'])}). Margem de {pct(s['actual']['margin'])}, contra {pct(s['budget']['margin'])} orçados. Diferença de margem: {margin_note}.

O resultado ficou {pct(s['yoy_pct'])} frente ao realizado de 2024. Crescimento da receita, resultado e margem devem ser acompanhados separadamente.

## Decomposição do desvio

| Categoria | Contribuição ao desvio do resultado |
| :--- | ---: |
{driver_rows}
| **Total** | **{money(s['variance'])}** |

{driver_note} As categorias têm sinais financeiros: menor despesa gera contribuição positiva ao resultado; os impactos e as compensações estão na tabela.

## Áreas

| Área | Resultado realizado | Desvio frente ao orçamento |
| :--- | ---: | ---: |
{area_rows}

{share_note} {month_note}

## Perguntas para aprofundamento

1. Quanto da diferença de receita vem de volume, preço, calendário de entrega ou capacidade?
2. Quais contratos ou usos explicam o gasto de tecnologia acima do orçamento?
3. O gasto de pessoal acompanha a receita e a capacidade planejada de Engenharia?
4. A economia em custos diretos decorre de eficiência ou de menor volume?

A base mensal agregada não contém contratos, preços, horas ou volumes para responder essas perguntas. As premissas do gerador são fictícias, estão documentadas em assumptions.md e não representam causalidade estimada de uma operação real.
"""
    (ROOT/"README.md").write_text(readme,encoding="utf-8")
    (ROOT/"docs").mkdir(exist_ok=True)
    (ROOT/"docs/findings.md").write_text(findings,encoding="utf-8")
    build_user_guide()
    print("README e diagnóstico atualizados com os cálculos da base.")
def build_user_guide():
    """Versão HTML local do mesmo passo a passo, sem dependências externas."""
    source=ROOT/'docs/user-guide.md'
    if not source.exists():return
    def rich(s):
        s=html.escape(s)
        return re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',s)
    blocks=[];lines=source.read_text(encoding='utf-8').splitlines();i=0
    while i<len(lines):
        line=lines[i];i+=1
        if not line.strip():continue
        if line.startswith('# '):blocks.append('<h1>'+rich(line[2:])+'</h1>')
        elif line.startswith('## '):blocks.append('<h2>'+rich(line[3:])+'</h2>')
        elif line.startswith('|'):
            table=[line]
            while i<len(lines) and lines[i].startswith('|'):table.append(lines[i]);i+=1
            rows=[]
            for j,row in enumerate(table):
                if j==1:continue
                tag='th' if j==0 else 'td'
                rows.append('<tr>'+''.join('<'+tag+'>'+rich(cell.strip())+'</'+tag+'>' for cell in row.strip('|').split('|'))+'</tr>')
            blocks.append('<div class="table-scroll"><table>'+''.join(rows)+'</table></div>')
        elif line.startswith('- '):
            items=[line[2:]]
            while i<len(lines) and lines[i].startswith('- '):items.append(lines[i][2:]);i+=1
            blocks.append('<ul>'+''.join('<li>'+rich(t)+'</li>' for t in items)+'</ul>')
        else:blocks.append('<p>'+rich(line)+'</p>')
    page='<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Como usar · Financial Performance Analytics</title><style>body{margin:0;background:#f3f5f9;color:#26344c;font:16px/1.65 system-ui}main{max-width:980px;margin:auto;padding:28px}h1,h2{color:#182d51;line-height:1.25}h2{margin-top:34px;border-top:1px solid #dfe5ef;padding-top:22px}a{color:#3157c5}.table-scroll{overflow:auto}table{border-collapse:collapse;font-size:14px;width:100%;background:white}th,td{padding:12px;border-bottom:1px solid #dfe5ef;text-align:left}th{background:#182d51;color:white}nav{display:flex;gap:20px;flex-wrap:wrap}li{margin:6px 0}</style><main><nav><a href="../preview/index.html">Abrir relatório</a><a href="../excel/FinancialPerformance.xlsx">Baixar Excel</a><a href="https://github.com/andremellotech/financial-performance-analytics">Código no GitHub</a></nav>'+''.join(blocks)+'</main></html>'
    (ROOT/'docs/user-guide.html').write_text(page,encoding='utf-8')
    style_file=ROOT/'docs/guide.css'
    if style_file.exists():
        page=page.replace('</style>',style_file.read_text(encoding='utf-8')+'</style>',1)
        (ROOT/'docs/user-guide.html').write_text(page,encoding='utf-8')

if __name__=="__main__":build_docs()
