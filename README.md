# FluxoCatálogo Sankhya → VTEX

Integração em Python responsável por validar produtos no Sankhya e criar ou atualizar o cadastro correspondente no catálogo da VTEX.

> **Status do fluxo:** esta documentação descreve o comportamento efetivamente implementado no código atual do projeto. O `plan.md` contém algumas funcionalidades planejadas que ainda não fazem parte do fluxo executado, como sincronização de preço e estoque.

## Visão geral

O processo parte de um `CODPROD` do Sankhya e usa esse mesmo código como `RefId` na VTEX.

```text
SANKHYA
   │
   │ CODPROD
   ▼
Validação dos dados de e-commerce
   │
   ├── inválido ──► encerra processamento
   │
   ▼
Verifica produto na VTEX pelo RefId
   │
   ├── não existe ──► cria produto
   │
   └── existe ──────► atualiza produto
                           │
                           ▼
                    Atualiza especificações
                           │
                           ▼
                    Verifica/cria SKU
                           │
                           ▼
                    Cria/atualiza SKU File
```

## O que é sincronizado

### Produto

- Nome
- Categoria
- Marca
- `RefId`
- Título
- `LinkId`
- Descrição
- Data de lançamento
- Visibilidade
- Ativação
- Meta description
- `ShowWithoutStock`
- Score

### Especificações

- Descrição
- Diferenciais
- Características
- Download de materiais
- Imagem da descrição

### SKU

- Nome
- `RefId`
- Dimensões
- Peso
- Cubagem
- Unidade de medida
- Código do fabricante
- Condição comercial
- Multiplicador

### SKU File / imagem

- Imagem principal
- URL
- Nome
- Label
- Posição

## O que não é sincronizado atualmente

O código executado em `scripts/main.py` **não sincroniza preço nem estoque**.

Essas funcionalidades aparecem como objetivo no `plan.md`, mas não existem como etapas do fluxo principal atual.

---

# Estrutura do projeto

```text
FluxoCatalogoSankhyaVtex/
├── sankhya/
│   ├── snk_client.py          # Cliente HTTP/autenticação Sankhya
│   ├── snk_check.py           # Validação do produto para e-commerce
│   ├── snk_fetch.py           # Consultas de dados no Sankhya
│   ├── sankhya_insert.py      # Gravação de departamentos no Sankhya
│   └── snk_utils.py            # Funções auxiliares
│
├── vtex/
│   ├── vtex_client.py         # Cliente HTTP VTEX
│   ├── vtex_fetch.py          # Consultas/identificadores VTEX
│   ├── vtex_create.py         # Criação de produto, SKU e arquivo
│   ├── vtex_update.py         # Atualização de produto, SKU e especificações
│   ├── vtex_utils.py          # Verificação de existência
│   ├── vtex_get.py            # Consultas auxiliares
│   ├── vtex_sync.py           # Sincronização de departamentos
│   └── vtex_df_departaments.py# Tratamento da árvore de categorias
│
├── scripts/
│   └── main.py                # Orquestrador principal
│
├── tests/
│   ├── unit/
│   └── integration/
│
├── notebooks/
├── utils/
├── requirements.txt
├── plan.md
└── README.md
```

---

# Requisitos

- Python 3
- Acesso às APIs do Sankhya
- Credenciais de API da VTEX
- Permissão para consultar/cadastrar/alterar catálogo na VTEX

Dependências principais:

- `requests`
- `python-dotenv`
- `tenacity`
- `pandas`
- `pytest`

Instalação:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

No Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

---

# Configuração

Crie um arquivo `.env` na raiz do projeto.

```env
SANKHYA_TOKEN=...
SANKHYA_APPKEY=...
SANKHYA_PASSWORD=...
SANKHYA_USERNAME=...

VTEX_APP_KEY=...
VTEX_APP_TOKEN=...
VTEX_ACCOUNT_NAME=...
VTEX_BASE_URL=...
```

O projeto também possui variáveis relacionadas a notificações:

```env
BOTTOKEN=...
CHATID=...
```

e:

```env
APP_ENV=...
```

## Segurança

**Nunca versione o `.env`.**

As credenciais utilizadas pelo projeto dão acesso a sistemas externos e devem permanecer somente no ambiente de execução.

Recomenda-se:

```gitignore
.env
.env.*
!.env.example
```

Se alguma credencial real tiver sido publicada em um repositório Git, ela deve ser revogada/rotacionada.

---

# Execução

O ponto de entrada atual é:

```text
scripts/main.py
```

No arquivo existe uma lista de produtos para processamento:

```python
produtos = [412158]

for produto in produtos:
    vtex_process_product(produto)
```

Para executar:

```bash
python scripts/main.py
```

Para processar outros produtos, altere a lista:

```python
produtos = [412158, 412159, 412160]
```

---

# Fluxo de processamento

A função principal é:

```python
vtex_process_product(codprod)
```

Ela executa:

```text
1. check_sankhya_ecommerce_infos()
2. sankhya_product_exist_no_vtex()
3. vtex_process_update_product()
   OU
   vtex_process_new_product()
```

## 1. Validação no Sankhya

Função:

```python
check_sankhya_ecommerce_infos(codprod)
```

O produto precisa possuir:

- `AD_USADOLV`
- `AD_ATIVOLV`
- `AD_VTEXCATEGORIA`

Se algum estiver vazio, o processamento é interrompido.

---

## 2. Verificação na VTEX

O sistema utiliza o `CODPROD` para procurar o produto através do `RefId`.

```http
HEAD /api/catalog_system/pvt/products/productgetbyrefid/{CODPROD}
```

Se existir:

```text
UPDATE
```

Se não existir:

```text
CREATE
```

---

# Criação de produto

Quando o produto não existe:

```python
vtex_process_new_product(codprod)
```

Executa:

```text
vtex_create_product()
        │
        ▼
vtex_update_basic_info()
        │
        ▼
vtex_update_specifications()
        │
        ▼
vtex_create_sku()
        │
        ▼
vtex_create_sku_file()
```

## Produto

```http
POST /api/catalog/pvt/product
```

Os dados são obtidos do Sankhya através de:

```text
CRUDServiceProvider.loadRecords
```

Campos principais:

```text
CODPROD
DESCRPROD
MARCA
AD_VTEXCATEGORIA
AD_MODELOREF
AD_DESCLONGALV
```

---

# Atualização de produto

Quando o produto já existe:

```python
vtex_process_update_product(codprod)
```

Executa:

```text
vtex_update_basic_info()
        │
        ▼
vtex_update_specifications()
        │
        ▼
verifica SKU
   │
   ├── existe ──► vtex_update_sku()
   │
   └── não existe ► vtex_create_sku()
        │
        ▼
vtex_create_sku_file()
```

---

# APIs utilizadas

## Sankhya

### Login

```http
POST https://api.sankhya.com.br/login
```

Função:

```python
snk_bearer_token()
```

Retorna o `bearerToken`.

### Consulta

```http
GET https://api.sankhya.com.br/gateway/v1/mge/service.sbr?serviceName=CRUDServiceProvider.loadRecords&outputType=json
```

Serviço:

```text
CRUDServiceProvider.loadRecords
```

Função:

```python
snk_get()
```

### Gravação

```http
POST https://api.sankhya.com.br/gateway/v1/mge/service.sbr?serviceName=DatasetSP.save&outputType=json
```

Serviço:

```text
DatasetSP.save
```

Função:

```python
snk_post()
```

É usado principalmente no fluxo de sincronização de departamentos.

---

# VTEX

| Método | Endpoint | Finalidade |
|---|---|---|
| HEAD | `/api/catalog_system/pvt/products/productgetbyrefid/{CODPROD}` | Verificar existência do produto |
| GET | `/api/catalog_system/pvt/products/productgetbyrefid/{CODPROD}` | Obter Product ID |
| POST | `/api/catalog/pvt/product` | Criar produto |
| PUT | `/api/catalog/pvt/product/{ProductId}` | Atualizar produto |
| POST | `/api/catalog_system/pvt/products/{ProductId}/specification` | Atualizar especificações |
| POST | `/api/catalog/pvt/stockkeepingunit` | Criar SKU |
| GET | `/api/catalog_system/pvt/sku/stockkeepingunitByProductId/{ProductId}` | Obter SKU |
| HEAD | `/api/catalog_system/pvt/sku/stockkeepingunitByProductId/{ProductId}` | Verificar SKU |
| PUT | `/api/catalog/pvt/stockkeepingunit/{SKUId}` | Atualizar SKU |
| POST | `/api/catalog/pvt/stockkeepingunit/{SKUId}/file` | Criar SKU File |
| GET | `/api/catalog/pvt/stockkeepingunit/{SKUId}/file` | Consultar SKU Files |
| PUT | `/api/catalog/pvt/stockkeepingunit/{SKUId}/file/{SKUFileId}` | Atualizar SKU File |

---

# Mapeamento Sankhya → VTEX

## Produto

| Sankhya | VTEX |
|---|---|
| `CODPROD` | `RefId` |
| `DESCRPROD` | `Name` |
| `DESCRPROD` | `Title` |
| `MARCA` | `BrandName` |
| `AD_VTEXCATEGORIA` | `CategoryId` |
| `AD_DESCLONGALV` | `Description` |
| `CODPROD` + nome | `LinkId` |
| nome do produto | `MetaTagDescription` |

## Especificações

| Sankhya | VTEX |
|---|---|
| `AD_DESCLONGALV` | Especificação ID 20 — Descrição |
| `AD_DIFERENCIAISLV` | Especificação ID 21 — Diferenciais |
| `AD_DESCTECNICALV` | Especificação ID 22 — Características |
| `AD_URLDEMATERIAIS` | Especificação ID 23 — Download de materiais |
| `AD_URLIMGLV` | Especificação ID 24 — Imagem da descrição |

## SKU

| Sankhya | VTEX |
|---|---|
| `DESCRPROD` | `Name` |
| `CODPROD` | `RefId` |
| `AD_ALTURALV` | `Height` / `PackagedHeight` |
| `AD_COMPRIMENTOLV` | `Length` / `PackagedLength` |
| `AD_LARGURALV` | `Width` / `PackagedWidth` |
| `AD_PESOLV` | `WeightKg` / `PackagedWeightKg` |
| `M3` | `CubicWeight` |
| `AD_UNIDADELV` | `MeasurementUnit` |
| `CODPROD` | `ManufacturerCode` |
| `AD_URLVIDEOLV` | `Videos` |

---

# Tratamento de imagem

O campo:

```text
ENDIMAGEM
```

é consultado no Sankhya.

Quando não existe uma URL de imagem específica utilizada pela função de SKU File, o código utiliza o fallback:

```text
https://img.casacontente.com.br/{CODPROD}.jpg
```

A imagem é enviada como arquivo principal do SKU:

```json
{
  "IsMain": true,
  "Label": "Main",
  "Position": 0
}
```

---

# Cliente HTTP e resiliência

As chamadas utilizam `requests.Session()` para reaproveitamento de conexões.

As sessões estão configuradas com:

```text
pool_connections = 100
pool_maxsize     = 100
pool_block       = True
```

O projeto utiliza `tenacity` para retry.

### Sankhya

As funções de autenticação e consulta possuem até 5 tentativas.

### VTEX

As chamadas genéricas possuem até 10 tentativas com backoff exponencial, limitado a 30 segundos.

---

# Logs

O `main.py` configura:

```text
INFO
```

com formato:

```text
[DATA-HORA] [NÍVEL] [ARQUIVO] mensagem
```

Exemplo:

```text
[08-10/10:20] [INFO] [vtex_fetch.py] 📊 VTEX ID: 12345
```

---

# Departamentos / categorias

Existe também um fluxo separado para sincronização da árvore de categorias.

Fluxo:

```text
VTEX
 │
 └── GET category/tree/2
        │
        ▼
   transforma em DataFrame
        │
        ▼
Sankhya
 │
 └── consulta AD_ADVTEXCATEGORIAS
        │
        ▼
compara os DataFrames
        │
        ▼
insere no Sankhya o que falta
```

O fluxo pode ser acionado pela função:

```python
sync_vtex_departments()
```

Ela está atualmente comentada no `main.py`.

---

# Testes

O projeto possui testes unitários e de integração:

```text
tests/
├── unit/
└── integration/
```

Execução:

```bash
pytest
```

Para executar somente testes unitários:

```bash
pytest tests/unit
```

Para integração:

```bash
pytest tests/integration
```

> Os testes de integração podem depender de credenciais e acesso aos serviços externos.

---

# Arquivo técnico

A documentação detalhada do fluxo está em:

```text
DOCUMENTACAO_TECNICA.md
```

Esse documento contém:

- fluxo ponta a ponta;
- endpoints;
- métodos HTTP;
- funções Python responsáveis;
- consultas Sankhya;
- mapeamento de campos;
- payloads;
- fluxo de criação;
- fluxo de atualização;
- tratamento de SKU;
- tratamento de imagens;
- sincronização de departamentos;
- limitações atuais.

---

# Referências oficiais

- Sankhya Developer: https://developer.sankhya.com.br/
- VTEX Developers: https://developers.vtex.com/
- Python Requests: https://requests.readthedocs.io/
- Tenacity: https://tenacity.readthedocs.io/
- Pytest: https://docs.pytest.org/

---

# Observações importantes

1. O `CODPROD` do Sankhya é a chave de referência usada para localizar o produto na VTEX.
2. O fluxo de produto depende da existência dos campos de controle de e-commerce no Sankhya.
3. O código atual não implementa sincronização de preço.
4. O código atual não implementa sincronização de estoque.
5. `vtex_update_sku_file()` existe, mas o fluxo principal utiliza `vtex_create_sku_file()` mesmo no caminho de atualização.
6. O `main.py` atualmente processa uma lista fixa de produtos.
7. Credenciais devem ser fornecidas por variáveis de ambiente e nunca pelo código-fonte.
