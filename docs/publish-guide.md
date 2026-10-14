# Publicar no GitHub

1. Crie um repositório **Public** chamado financial-performance-analytics na conta andremellotech. Deixe **Add README** desligado, **No .gitignore** e **No license**: esses arquivos já estão no pacote.
2. Para envio pelo navegador, extraia **financial-performance-analytics-upload.zip**. Ele contém três pastas numeradas. O GitHub aceita até **100 arquivos por envio**; o projeto contém 195.
3. Na raiz do repositório, clique em **uploading an existing file**, ou **Add file → Upload files**. Abra **01-arquivos-iniciais** no computador e arraste **seu conteúdo** para a página. São 82 arquivos. Confirme em **Commit changes**, na branch main.
4. Volte à raiz do repositório e repita o upload com o **conteúdo** de **02-relatorio-powerbi**: arraste a pasta powerbi que está dentro dela. São 93 arquivos. Confirme o commit.
5. Volte novamente à raiz e envie o **conteúdo** de **03-modelo-e-workflows**: as pastas powerbi e .github. São 20 arquivos; os arquivos de powerbi são acrescentados aos do lote anterior. Confirme o commit. Os workflows entram por último, com o projeto completo.
6. Confira o README e o workflow **Validate analytics project** em Actions. Se o envio não criou a branch main, ajuste a branch padrão antes de ativar o site.
7. Fixe o repositório no perfil, se desejar.

**Não envie o ZIP nem as pastas numeradas.** Envie apenas o conteúdo de cada lote, sempre a partir da raiz do repositório. No resultado final, README.md, index.html, powerbi, data, preview, excel, docs, scripts, tests e .github ficam diretamente na raiz.

O ZIP completo **financial-performance-analytics-v1.0.0.zip** contém o projeto em uma única pasta; também pode ser publicado pelo GitHub Desktop ou git. Para upload pelo navegador, use o ZIP em lotes acima. Se arquivos iniciados por ponto não aparecerem no Explorador de Arquivos, ative **Exibir → Mostrar → Itens ocultos** e confira .gitignore no primeiro lote e .github no terceiro.

Descrição sugerida:

```text
Análise financeira com Power BI, Excel, DAX e Power Query: realizado vs. orçado, Build-up, visão mensal e projeção EAC, com dados fictícios reproduzíveis.
```

Tópicos: powerbi, dax, power-query, excel, financial-analysis, budget-vs-actual, portfolio.

## Ativar a demonstração no GitHub Pages

Em **Settings → Pages → Build and deployment → Source**, escolha **GitHub Actions**. Em Actions, execute **Publish analytics demo** pela opção Run workflow na branch main. O workflow testa o projeto antes de publicar a demonstração.

Abra a URL retornada pelo deployment. O endereço esperado é https://andremellotech.github.io/financial-performance-analytics/; a tela inicial aponta para relatório, passo a passo e Excel. O relatório direto fica em /preview/. Use o endereço confirmado no campo Website. O site não foi publicado na preparação deste pacote.

A prévia também abre localmente pelo arquivo preview/index.html. Dados, estilos e código necessários estão no próprio HTML.

Se o workflow não aparecer, confirme que .github/workflows/pages.yml e validate.yml foram enviados. Se o upload pelo navegador omitir arquivos ocultos, use GitHub Desktop ou git para enviar o conteúdo completo. Não coloque credenciais nos arquivos.

## Status de validação e versão

Após **Validate analytics project** passar no GitHub, o badge dinâmico pode ser adicionado ao README e ao modelo em scripts/build_docs.py, para não ser removido na reconstrução:

```md
[![Validação](https://github.com/andremellotech/financial-performance-analytics/actions/workflows/validate.yml/badge.svg)](https://github.com/andremellotech/financial-performance-analytics/actions/workflows/validate.yml)
```

Ele mostra o status do workflow; não confirma abertura no Power BI ou Excel. Para publicar a tag e os anexos de **v1.0.0**, siga release-notes.md. A versão local já está identificada em VERSION e CHANGELOG.md.

Referências: [Upload de arquivos e pastas](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository), [Configurar GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site), [workflow estático oficial](https://github.com/actions/starter-workflows/blob/main/pages/static.yml) e [Releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases).
