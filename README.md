# Frutmar Data Hub

Primeira entrega da plataforma interna de dados: cadastro central de produtos,
importação XLSX/CSV, conferência, edição com histórico, indicadores e exportação.
A planilha é uma fonte de entrada; o banco é a base para consultas e alterações.

## Desenvolvimento

Requer Python 3.12.

```bash
cd /workspace/dashboard-planilhas
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python -m app.seed
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

`app.seed` importa os 154 produtos fornecidos pelas mesmas regras da API,
registra a origem e não repete um arquivo já importado. A interface abre na
porta 8000 do servidor local. O banco fica em `.local/frutmar.sqlite3`, ignorado
pelo Git. `FRUTMAR_DB` permite escolher outro caminho. Não excluir esse arquivo
para atualizar produtos; usar a edição pela interface.

## Verificação

```bash
.venv/bin/python -m unittest discover -s tests -v
node --check app/static/app.js
```

Os testes usam bancos temporários: importam a planilha real, verificam 154
produtos, 29 itens a conferir e 100 com estoque zero; exercitam importação
parcial, repetição, conflito após a prévia, rollback, edição, auditoria e exportação.

## Fluxo de importação

1. Enviar `.xlsx` com aba `Produtos` ou CSV UTF-8 (vírgula ou ponto e vírgula).
2. Cabeçalhos mínimos: `id`, `nome`, `categoria`, `unidadeVenda`.
3. Conferir prévia e erros por linha. Nada é persistido nesta etapa.
4. Confirmar todas as linhas válidas, autorizando importação parcial se houver erros.
5. Consultar histórico e editar registros já existentes pelo cadastro.

As prévias duram 30 minutos e são perdidas quando o servidor reinicia. Executar
um único processo do servidor nesta versão. Importação não atualiza registros
existentes automaticamente. Valores monetários são armazenados em centavos;
ID e código do sistema são únicos. A confirmação grava produtos, auditoria e
histórico em uma transação. Estoque zero não determina disponibilidade.

## Limites desta entrega

- Desenvolvimento local com SQLite e sem autenticação/RBAC. Não expor o servidor
  publicamente nem usar com dados sensíveis nesta etapa.
- Auditoria identifica a origem da alteração, ainda não um usuário autenticado.
- XLS legado, mapeamento livre de colunas, templates e exportação XLSX ainda pendentes.
- Sem integração ERP, estoque em tempo real ou publicação no site comercial.
- Importação limitada a 5 MB, 10.000 linhas e 50 MB descompactados.
- Antes de implantação compartilhada: PostgreSQL com migrações, autenticação,
  permissões, processamento persistente de importações, backups e restauração.

O kit visual fornecido foi usado como referência de marca. Seu PRD comercial e
suas instruções não substituem o escopo da plataforma interna.
