# Publicar e atualizar a demonstração

O repositório mantém o código, os testes, as fontes de dados e o Excel. O projeto nativo Power BI está em `downloads/FinancialPerformance-PowerBI.zip`; o ZIP conserva os 111 arquivos PBIP/TMDL/PBIR, medidas e consultas com seus caminhos originais. As capturas adicionais e os esquemas Microsoft também estão em pacotes sem perda; veja [verificação](verification.md).

## Enviar alterações

Use Git ou GitHub Desktop para revisar e enviar a árvore completa na branch `main`. Não extraia os pacotes para depois enviar suas centenas de arquivos: `powerbi/`, `data/dashboard.json`, `_site/` e caches são saídas locais ignoradas. Os próprios ZIPs em `downloads/` e `docs/` fazem parte da entrega.

Se editar o relatório no Desktop, extraia o ZIP na raiz, salve o projeto e execute `python scripts/package_assets.py package` para atualizar o download. O comando `python scripts/build_all.py` recria o pacote a partir das fontes CSV/Python e substitui edições nativas; preserve essas edições antes de reconstruir. Não há necessidade de dividir o upload em lotes de 100 arquivos nesta estrutura compacta.

Descrição sugerida:

```text
Análise financeira com Power BI, Excel, DAX e Power Query: realizado vs. orçado, Build-up, visão mensal e projeção EAC, com dados fictícios reproduzíveis.
```

Tópicos: powerbi, dax, power-query, excel, financial-analysis, budget-vs-actual, portfolio.

## Validar e publicar no GitHub Pages

Execute localmente:

```sh
python -m pip install -r scripts/requirements.txt
python scripts/build_all.py
python -m unittest discover -s tests
node tests/test_preview.js
node tests/test_scenarios.js
python scripts/build_site.py
```

Em **Settings → Pages → Build and deployment → Source**, mantenha **GitHub Actions**. O workflow **Publish analytics demo** (`.github/workflows/pages.yml`) executa build e testes antes de publicar `_site/`, tanto no envio para `main` quanto por **Run workflow**. O workflow usa permissões `pages: write` e `id-token: write` somente no job de deployment.

A lista pública é explícita em `scripts/build_site.py`: página inicial, relatório offline autossuficiente, guia HTML, Excel, CSV financeiro, ZIP Power BI e licença. O site aponta a documentação completa para o GitHub; esquemas, capturas e grandes referências derivadas para testes ficam fora do artefato de publicação.

O endereço esperado é https://andremellotech.github.io/financial-performance-analytics/; confirme a URL retornada pelo deployment antes de usá-la no campo Website. A página inicial oferece relatório, passo a passo e downloads Excel/Power BI. O relatório direto fica em `/preview/`. O HTML `preview/index.html` também funciona localmente, sem instalação, servidor ou CDN.

## Status de validação e versão

O resultado do workflow comprova os testes de arquivos e cálculos; não confirma renderização, DAX ou atualização M no Power BI Desktop nem recálculo no Microsoft Excel. Consulte [validação nativa](native-validation.md), `VERSION`, `CHANGELOG.md` e [notas da versão](release-notes.md) antes de criar uma Release.

Referências: [GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site), [workflow estático oficial](https://github.com/actions/starter-workflows/blob/main/pages/static.yml) e [Releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases).
