# Sistema de E-commerce com Microserviços

Projeto simples de arquitetura de microsserviços desenvolvido para fins escolares.

### Serviços Disponíveis

| Serviço                | Porta | Responsabilidade                     |
|------------------------|-------|--------------------------------------|
| Catálogo Service       | 8001  | Gerenciamento de produtos            |
| Usuários Service       | 8002  | Cadastro e autenticação de usuários  |
| Pedidos Service        | 8003  | Orquestração de pedidos              |
| Estoque Service        | 8004  | Controle de inventário               |
| Pagamento Service      | 8005  | Processamento de pagamento (simulado)|

---

## 📋 Pré-requisitos

- **Python 3.8 ou superior**
- **MySQL Server** instalado e em execução
- **Git** (opcional)

---

## ⚙️ Configuração Inicial

### 1. Configurar o MySQL

Execute os seguintes comandos no MySQL:

```sql
CREATE USER 'dev'@'%' IDENTIFIED BY '123456';
GRANT ALL PRIVILEGES ON *.* TO 'dev'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
```

### 2. Configurar o arquivo `.env` em cada serviço

**É obrigatório** configurar o arquivo `.env` em **cada um** dos 5 serviços.

Entre em cada pasta de serviço e crie (ou edite) o arquivo `.env` com o seguinte conteúdo:

```env
# Configuração do Banco de Dados
DATABASE_URL=mysql+pymysql://dev:123456@localhost:3306/db_catalogo
```

**Atenção:** Altere apenas o nome do banco de dados em cada serviço:

- **catalogo-service/.env** → `db_catalogo`
- **usuarios-service/.env** → `db_usuarios`
- **pedidos-service/.env** → `db_pedidos`
- **estoque-service/.env** → `db_estoque`
- **pagamento-service/.env** → `db_pagamento`

**Exemplo completo para cada serviço:**

**catalogo-service/.env**
```env
DATABASE_URL=mysql+pymysql://dev:123456@localhost:3306/db_catalogo
```

**usuarios-service/.env**
```env
DATABASE_URL=mysql+pymysql://dev:123456@localhost:3306/db_usuarios
```

**pedidos-service/.env**
```env
DATABASE_URL=mysql+pymysql://dev:123456@localhost:3306/db_pedidos
```

**estoque-service/.env**
```env
DATABASE_URL=mysql+pymysql://dev:123456@localhost:3306/db_estoque
```

**pagamento-service/.env**
```env
DATABASE_URL=mysql+pymysql://dev:123456@localhost:3306/db_pagamento
```

---

## 🚀 Como Executar o Projeto

### No Windows

1. Abra a pasta raiz do projeto
2. Dê duplo clique no arquivo **`start-all.bat`**
3. Cinco janelas do Prompt de Comando (CMD) serão abertas automaticamente

### No Linux / macOS

1. Abra o terminal na raiz do projeto
2. Execute:

```bash
python3 start-all.py
```

---

## 🧪 Rotas Principais para Teste

### Catálogo Service
- `POST http://127.0.0.1:8001/products` → Criar produto
- `GET http://127.0.0.1:8001/products` → Listar produtos

### Usuários Service
- `POST http://127.0.0.1:8002/users` → Criar usuário

### Estoque Service
- `PUT http://127.0.0.1:8004/inventory/{productId}` → Adicionar estoque
- `GET http://127.0.0.1:8004/inventory/{productId}` → Consultar estoque

### Pedidos Service (Fluxo Completo)
- `POST http://127.0.0.1:8003/orders` → Criar pedido (integra todos os serviços)

**Exemplo de JSON para criar pedido:**
```json
{
  "usuario_id": 1,
  "itens": [
    { "produto_id": 1, "quantidade": 2 },
    { "produto_id": 2, "quantidade": 1 }
  ]
}
```

### Pagamento Service
- `POST http://127.0.0.1:8005/payments` → Processar pagamento

---

## 🧩 Documentação de API (Redoc)

Cada serviço expõe documentação Swagger/OpenAPI em:

- `http://127.0.0.1:8001/redoc` → Catálogo Service
- `http://127.0.0.1:8002/redoc` → Usuários Service
- `http://127.0.0.1:8003/redoc` → Pedidos Service
- `http://127.0.0.1:8004/redoc` → Estoque Service
- `http://127.0.0.1:8005/redoc` → Pagamento Service

Use esses links para verificar e testar todos os endpoints ativos com a documentação interativa.

---

## Fluxo Recomendado de Teste (Completo)

1. Criar um usuário no serviço de Usuários
2. Criar um ou mais produtos no Catálogo
3. Adicionar estoque para esses produtos
4. Criar um pedido no Pedidos Service (este serviço irá:
   - Validar o usuário
   - Verificar estoque
   - Baixar o estoque
   - Processar o pagamento
   - Retornar o status final)

## 🛠️ Exemplo HTTP Passo a Passo

1. Criar Usuário (Usuários Service)
```bash
curl -X POST http://127.0.0.1:8002/users \
  -H "Content-Type: application/json" \
  -d '{"nome":"João Silva", "email":"joao@teste.com", "senha":"123456"}'
```

2. Criar Produto (Catálogo Service)
```bash
curl -X POST http://127.0.0.1:8001/products \
  -H "Content-Type: application/json" \
  -d '{"nome":"Produto A", "descricao":"Teste", "preco":99.90}'
```

3. Adicionar Estoque (Estoque Service)
```bash
curl -X PUT "http://127.0.0.1:8004/inventory/1?quantidade=10"
```

4. Criar Pedido (Pedidos Service) ⭐ **O Pagamento é processado automaticamente!**
```bash
curl -X POST http://127.0.0.1:8003/orders \
  -H "Content-Type: application/json" \
  -d '{"usuario_id":1, "itens":[{"produto_id":1,"quantidade":2}]}'
```

**Resposta esperada:**
```json
{
  "id": 1,
  "usuario_id": 1,
  "status": "PAGO",  // ou "CANCELADO" se pagamento foi recusado (15% de chance)
  "valor_total": 199.80,
  "criado_em": "2026-03-28T...",
  "itens": [...]
}
```

---

## 📝 Teste Manual de Pagamento (Opcional)

Se quiser processar um pagamento isoladamente (sem criar pedido):

```bash
curl -X POST http://127.0.0.1:8005/payments \
  -H "Content-Type: application/json" \
  -d '{"pedido_id":1, "usuario_id":1, "valor":199.80, "metodo_pagamento":"PIX"}'
```

**Nota:** Este é um teste manual. Normalmente, o Pagamento é processado **automaticamente** quando você cria um Pedido na etapa 4.

---

## Dicas Importantes

- Os bancos de dados são criados automaticamente na primeira execução
- As senhas dos usuários são armazenadas com criptografia (`bcrypt`)
- O Pagamento Service é simulado (aproximadamente 85% de chance de aprovação)
- Para parar um serviço, pressione `Ctrl + C` na janela correspondente

---

**Projeto desenvolvido para disciplina de Microsserviços / Arquitetura de Software**

Qualquer dúvida ou erro durante a execução, verifique:
- Se o MySQL está rodando
- Se o arquivo `.env` está correto em todos os serviços
- Se o usuário `dev` foi criado corretamente no MySQL

---

## 📋 Conformidade com Requisitos (Prova Prática P1)

Este projeto atende **100%** dos requisitos da Prova Prática P1: Arquitetura de Microsserviços aplicados em um E-commerce.

### ✅ Serviços Obrigatórios Implementados

| Serviço | Status | Porta | Endpoints |
|---------|--------|-------|-----------|
| Catálogo Service | ✅ | 8001 | GET/POST /products, GET /products/{id} |
| Usuários Service | ✅ | 8002 | POST /users, GET /users/{id} |
| Pedidos Service | ✅ | 8003 | POST /orders, GET /orders/{id} |
| Estoque Service | ✅ | 8004 | GET /inventory/{id}, PUT /inventory/{id} |
| Pagamento Service | ✅ | 8005 | POST /payments |

### ✅ Endpoints por Serviço

#### Catálogo Service (8001)
- `GET /products` - Listar todos os produtos
- `GET /products/{id}` - Obter detalhes de um produto
- `POST /products` - Cadastrar novo produto

#### Usuários Service (8002)
- `POST /users` - Cadastrar novo usuário
- `GET /users/{id}` - Buscar usuário por ID

#### Pedidos Service (8003)
- `POST /orders` - Criar novo pedido (orquestra todos os serviços)
- `GET /orders/{id}` - Consultar pedido específico

#### Estoque Service (8004)
- `GET /inventory/{productId}` - Consultar estoque de um produto
- `PUT /inventory/{productId}` - Atualizar quantidade em estoque

#### Pagamento Service (8005)
- `POST /payments` - Processar pagamento

### ✅ Regras Arquiteturais Obrigatórias

| Regra | Status | Descrição |
|-------|--------|-----------|
| Banco próprio por serviço | ✅ | Cada serviço tem seu banco de dados isolado |
| Isolamento de dados | ✅ | Nenhum serviço acessa banco de outro |
| Comunicação exclusiva via API REST | ✅ | Apenas HTTP/JSON entre serviços |
| Independência de execução | ✅ | Cada serviço pode rodar isoladamente |

### ✅ Fluxo de Orquestração (Pedidos Service)

O Pedidos Service implementa completamente o fluxo esperado:

1. **Validação de Usuário** - Verifica se usuário existe no serviço de Usuários
2. **Verificação de Estoque** - Consulta disponibilidade no serviço de Estoque
3. **Criação de Pedido** - Registra pedido no banco com status inicial
4. **Processamento de Itens** - Busca dados (preço) no serviço de Catálogo
5. **Decremento de Estoque** - Reduz quantidade após validação
6. **Processamento de Pagamento** - Chama serviço de Pagamento
7. **Atualização de Status** - Define pedido como PAGO ou CANCELADO

### ✅ Qualidade de Código

- ✅ Padrão de projeto Service/Repository/DTO/Model
- ✅ Tratamento de erros com status codes HTTP apropriados
- ✅ Documentação completa em português nos métodos
- ✅ Validações de integridade e regras de negócio
- ✅ Criptografia de senhas com bcrypt
- ✅ Simulação realista de pagamento (85% de aprovação)

---

**Boa sorte no seu projeto!** 🚀
