## O que muda

Entrega a primeira versão interna do Frutmar Data Hub. Os produtos passam a ser consultados e editados em um banco central, enquanto XLSX/CSV funciona como canal de entrada.

- Cadastro, busca, filtros, indicadores e edição com histórico.
- Importação com prévia, erros por linha, confirmação parcial explícita e gravação atômica.
- Proteção contra arquivos repetidos e IDs/códigos duplicados; exportação CSV.
- Identidade visual Frutmar e carga inicial dos 154 produtos fornecidos.
- Dependências fixadas e documentação de instalação e arquitetura.

## Validação

- Sete testes de integração passaram, incluindo a planilha real e rollback de importações conflitantes.
- Sintaxe JavaScript e `git diff --check` passaram.
- Fluxos de importação, cadastro, edição, busca e histórico foram verificados no Chromium, além do layout móvel.

## Escopo

Versão para desenvolvimento local com SQLite, sem autenticação/RBAC. PostgreSQL, migrações, login, permissões e backups permanecem necessários antes da implantação compartilhada. Estoque da planilha é referência histórica e não determina disponibilidade.
