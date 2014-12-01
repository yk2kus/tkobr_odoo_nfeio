Integração Odoo NFE.io
==========

Módulo de integração entre o [Odoo][1] e [NFE.io][2], para preenchimento automático dos dados de empresa através do seu CNPJ e/ou endereço completo via CEP.

# Funcionalidades

Este módulo adiciona um botão de pesquisa junto ao campo CNPJ e outro depois do CEP, para preenchimento automático dos dados da empresa e/ou endereço buscando a informação ao NFE.io.

- **CNPJ**, Obtenha os dados de uma empresa através do seu CNPJ:
  - Nome Fantasia
  - Razão Social
  - Data Abertura
  - Natureza Jurídica
  - Tipo Fiscal
  - Situação Cadastral
  - Data Situação Cadastral
  - Data Cadastro MEI
  - Natureza Jurídica
  - CNAE Principal
  - CNAE Secundários
  - Endereço Completo
- **Endereços**, preenche o endereço através do CEP inserido:
  - País (Brasil, por omissão)
  - Estado (UF)
  - Cidade
  - Rua
  - Bairro

# Sobre a [NFE.io][2]

A NFE.io é uma WebAPI robusta e bastante completa que permite a consulta de informações empresariais para todo o Brasil (empresas, endereços, países, cidades, estados, notas fiscais eletrônicas).  
Esta API disponibiliza um serviço de acesso aos dados (API REST) que possibilita consultar os dados extraídos diretamente de diferentes fontes como Receita Federal, Correios, Simples Nacional, IBGE entre outros.

# Dependências

Para instalar este módulo tem de instalar o módulo l10n_br_base do repositório [l10n_br_core][4] da localização Brasileira.  
Para funcionar deve primeiro se cadastrar no site [NFE.io][3] para a obtenção da APIKEY, que deve ser inserida no campo NFEIO API em Configurações/Empresas, aba Configuração na(s) empresa(s).

[1]: http://www.odoo.com/
[2]: http://nfe.io/consultas-automatizadas/
[3]: http://app.nfeio.io/
[4]: https://github.com/odoobrasil-fiscal/l10n_br_core
