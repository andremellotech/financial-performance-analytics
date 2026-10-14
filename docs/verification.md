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
