# Decisão inicial: plataforma de dados

O domínio é o produto cadastrado, independente do formato da fonte. A API de
cadastro e o importador compartilham `app/domain.py`. Preços são inteiros em
centavos na persistência. O payload preserva os 21 campos conhecidos da origem,
enquanto identidade, código, nome e categoria têm colunas próprias e restrições.

Fluxo: arquivo → prévia temporária validada → confirmação transacional → banco
central → consulta, indicadores e exportação. Nenhum dashboard lê diretamente
o Excel. ID original é preservado; código do sistema é um vínculo externo único,
sem converter códigos ou EANs em números e perder zeros iniciais.

Esta etapa usa um monólito FastAPI e SQLite para permitir execução imediata no
ambiente. SQLite é uma escolha local provisória, não o banco recomendado para
a implantação compartilhada. A migração para PostgreSQL e uma modelagem mais
estruturada exigem migrations explícitas e testes de migração antes de produção.

O estoque da fonte é uma referência histórica, não um saldo operacional. Os
29 registros marcados Conferir continuam assim. Preço de revenda não substitui
preço de venda. Itens do catálogo de fornecedores não são promovidos à base de
produtos automaticamente. O ERP permanece candidato à fonte oficial dos
cadastros e saldos; isso deve ser confirmado com o responsável pelo processo.

Próxima fatia: confirmar regras de preço/unidade e disponibilidade com a operação;
adicionar usuários e permissões, PostgreSQL/migrações e revisão formal das
importações. Evitar uma tabela genérica de planilhas e deduplicação por nome.
