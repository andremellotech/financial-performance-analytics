# Verificação da entrega

## Cálculos e arquivos

- 23 testes Python passaram, cobrindo a base, sinais, filtros, períodos, projeção, cenários, divisões sem denominador, atualização por CSV, projeto nativo e Excel salvo.
- Os testes JavaScript reconciliaram oito recortes anuais, 96 recortes de EAC e 24 referências de mês/acumulado. Alterar o realizado posterior ao corte não altera o EAC; em dezembro, o EAC coincide com o realizado anual.
- O Excel salvo preserva as 864 linhas da base, quatro abas, quatro seletores e quatro gráficos com referências a células. Os seis percentuais de cenário são editáveis e as linhas ativas alimentam a projeção. Não há erros de fórmula nos valores em cache.
- Os oito recortes anuais e os 96 recortes de projeção foram recalculados no mecanismo de autoria. Painel, Build-up, Projeção e Base foram renderizados e inspecionados.
- Os três cenários iniciais foram recalculados em 288 recortes no Excel e comparados com Python; JavaScript também reconciliou esses recortes. A regra arredonda cada categoria/mês ao centavo antes dos totais.
- O Build-up do Excel usa colunas empilhadas com uma base acumulada invisível para formar a cascata. Realizado e projetado são séries editáveis; as células auxiliares permanecem disponíveis.
- Os JSON do Power BI foram validados contra os esquemas oficiais Microsoft. O parser Microsoft TMDL aceitou cinco tabelas, três relações e 36 medidas.

## Navegação e aparência

As sete perspectivas da prévia abriram no navegador. O controle de mês aparece nas quatro perspectivas que usam corte mensal. Foram conferidos janeiro, dezembro e a seleção 2024/Engenharia; o padrão 2025/Todas/Set foi restaurado.

As quatro novas perspectivas foram conferidas em largura de celular, sem rolagem horizontal da página. Tabelas e cascata extensa usam rolagem dentro do próprio painel. Não houve erros ou avisos no console. As capturas do README correspondem a esta entrega.

Na prévia, foram conferidos Base, Otimista, Conservativo, alteração de premissa por teclado e entradas fora do intervalo. O realizado até corte permaneceu igual. Os três cenários chegaram ao mesmo realizado em dezembro. A Visão mensal abriu com premissas de forecast inválidas, preservando sua independência. Os novos controles foram inspecionados em largura de celular, sem ampliar a página horizontalmente.

O roteiro resumido dentro da prévia e o guia HTML abriram corretamente. Os links locais foram conferidos. Os workflows foram preparados a partir de ações oficiais; sua execução e publicação no GitHub ainda dependem do envio e login.

## Revisão e preservação das fontes

O acabamento final padronizou navegação, espaços, títulos, cabeçalhos e destaques de premissas. As sete abas foram conferidas em desktop e larguras de 320/390 px, sem corte nos valores dos indicadores nem rolagem horizontal da página. Guia e capa também foram conferidos em celular. As capturas foram renovadas.

No Excel, todas as fórmulas e os valores numéricos das quatro abas foram comparados com a versão anterior e permaneceram iguais. A revisão de formato recalculou oito recortes anuais e os três cenários em setembro/dezembro. Os 288 recortes completos já haviam sido reconciliados antes desta revisão visual. O Power BI recebeu ajustes de espaçamento e tipografia, com nova validação estrutural; a inspeção visual no Desktop permanece pendente.

A revisão independente conferiu sinais, limites de período, reconciliação de categorias, fórmulas da planilha salva e referências dos quatro gráficos. Não identificou falhas nos itens revisados.

Os quatro CSV mantêm os hashes da base fictícia anterior. Nenhum arquivo de apresentação, recurso visual ou informação da empresa de referência está incluído no pacote. A referência orientou somente a organização das análises.

## Limites

Não foram executados abertura/renderização, atualização M ou cálculo DAX no Power BI Desktop; nem abertura/recalculo nativo no Microsoft Excel. A validação estrutural não substitui essas verificações. O Power BI apresenta os gastos EAC por categoria na cascata; a separação realizado/projetado aparece nos indicadores e no detalhe.

O EAC Base é hipotético: realizado até o mês de referência mais orçamento dos meses restantes. Na prévia e no Excel, os cenários ajustam somente o orçamento futuro. O Power BI mantém a regra Base. Não há estimativa de tendências, carryover ou riscos. As descrições de motivadores são premissas da simulação, não conclusões sobre uma empresa real.

A planilha usa a base desta entrega e sua atualização é manual. A prévia HTML e os textos podem ser reconstruídos dos CSV. Capturas não são renovadas pelo workflow. A publicação e a execução do workflow no GitHub dependem do envio do repositório.

O pacote é local, sem credenciais, caminhos pessoais ou dependência das bibliotecas de autoria. As consultas permitem informar a pasta dos CSV ou usar os dados fictícios embarcados.


## Pacotes compactos e reprodução

O projeto nativo foi consolidado em `downloads/FinancialPerformance-PowerBI.zip`: 111 entradas com os caminhos originais sob `powerbi/`. Extraia antes de abrir o PBIP. A extração Python preserva edições locais e recusa sobrescritas diferentes; use uma pasta vazia para outra cópia. Para republicar alterações feitas no Desktop, execute `python scripts/package_assets.py package` antes de enviar o ZIP. `build_all.py` reconstrói o modelo a partir dos CSV e substitui o pacote; não o execute sobre edições nativas que queira preservar sem antes salvá-las.

Os 17 JSON oficiais de esquema estão em `docs/schemas/schemas.zip`, com caminhos `docs/schemas/fabric/...` e a licença Microsoft mantida em `docs/schemas/LICENSE`. O validador lê os JSON diretamente do ZIP, sem rede. As dez capturas adicionais da entrega estão preservadas, sem recompressão de imagem, em `docs/images/screenshots.zip`, com seus nomes e caminhos originais; as três imagens usadas no README continuam diretamente acessíveis. Para extrair qualquer pacote de apoio: `python scripts/package_assets.py extract --archive docs/images/screenshots.zip --destination .` (troque o arquivo para os esquemas).

`data/dashboard.json` é derivado dos CSV por `build_preview.py` e ignorado pelo Git. O mesmo objeto de dados, referências financeiras e cenários está embarcado em `preview/index.html`, que continua funcionando offline. Execute `python scripts/build_all.py` antes dos testes em uma cópia recém-baixada. O README mantém seus textos editoriais ao renovar os números calculados.

`python scripts/build_site.py` prepara somente sete dependências públicas: página inicial, prévia autossuficiente, guia HTML, Excel, CSV financeiro, ZIP Power BI e licença. Código, esquemas, capturas adicionais e referências de teste permanecem no repositório, fora do artefato Pages. A documentação completa está ligada ao GitHub.
