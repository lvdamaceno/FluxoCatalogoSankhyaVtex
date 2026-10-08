# Documentação Técnica — FluxoCatálogo Sankhya → VTEX

## 1. Objetivo

Este documento descreve tecnicamente o fluxo implementado no projeto `FluxoCatalogoSankhyaVtex`, desde a validação de um produto no Sankhya até sua criação ou atualização no catálogo da VTEX.

A análise considera o código atualmente presente no projeto, principalmente:

```text
scripts/main.py
sankhya/snk_client.py
sankhya/snk_check.py
sankhya/snk_fetch.py
sankhya/sankhya_insert.py
vtex/vtex_client.py
vtex/vtex_fetch.py
vtex/vtex_create.py
vtex/vtex_update.py
vtex/vtex_utils.py
vtex/vtex_sync.py
```

---

# 2. Visão arquitetural

```text
                         ┌─────────────────┐
                         │    Sankhya      │
                         └────────┬────────┘
                                  │
                           autenticação
                                  │
                                  ▼
                         consulta Produto
                                  │
                                  ▼
                     validação e-commerce
                                  │
                                  ▼
                         CODPROD / RefId
                                  │
                                  ▼
                         ┌─────────────────┐
                         │      VTEX       │
                         └────────┬────────┘
                                  │
                         produto existe?
                           /            \
                         não            sim
                          │              │
                          ▼              ▼
                       CREATE          UPDATE
                          │              │
                          └──────┬───────┘
                                 ▼
                         especificações
                                 │
                                 ▼
                              SKU
                                 │
                                 ▼
                           SKU File
                                 │
                                 ▼
                         produto catalogado
```

---

# 3. Identificador de integração

O elo entre os sistemas é:

```text
Sankhya.CODPROD
       │
       ▼
VTEX.RefId
```

Exemplo:

```text
CODPROD Sankhya = 412158
RefId VTEX       = 412158
```

A partir desse valor o projeto consegue descobrir o `ProductId` interno da VTEX.

Depois:

```text
CODPROD
   │
   └── RefId
         │
         └── ProductId
                │
                └── SKUId
                       │
                       └── SKUFileId
```

---

# 4. Orquestração

O ponto de entrada é:

```text
scripts/main.py
```

Função principal:

```python
vtex_process_product(codprod)
```

Implementação conceitual:

```python
def vtex_process_product(codprod):
    if check_sankhya_ecommerce_infos(codprod):
        if sankhya_product_exist_no_vtex(codprod):
            vtex_process_update_product(codprod)
        else:
            vtex_process_new_product(codprod)
```

---

# 5. Etapa 1 — Autenticação Sankhya

Arquivo:

```text
sankhya/snk_client.py
```

Função:

```python
snk_bearer_token()
```

Endpoint:

```http
POST https://api.sankhya.com.br/login
```

Headers utilizados:

```http
Accept: application/json
Content-Type: application/json
token: <SANKHYA_TOKEN>
appkey: <SANKHYA_APPKEY>
password: <SANKHYA_PASSWORD>
username: <SANKHYA_USERNAME>
```

Resposta esperada:

```json
{
  "bearerToken": "..."
}
```

O token é utilizado posteriormente como:

```http
Authorization: Bearer <token>
```

---

# 6. Cliente Sankhya

Arquivo:

```text
sankhya/snk_client.py
```

URL base:

```text
https://api.sankhya.com.br/gateway/v1/mge/service.sbr?serviceName=
```

Funções:

```python
snk_get(payload, service)
snk_post(payload, service)
```

## GET

Utilizado para consultas:

```text
snk_get()
    │
    ├── autentica
    │
    └── GET service.sbr
```

## POST

Utilizado para gravações:

```text
snk_post()
    │
    ├── autentica
    │
    └── POST service.sbr
```

---

# 7. Etapa 2 — Validação do produto

Arquivo:

```text
sankhya/snk_check.py
```

Função:

```python
check_sankhya_ecommerce_infos(codprod)
```

Serviço:

```text
CRUDServiceProvider.loadRecords
```

Endpoint efetivo:

```http
GET https://api.sankhya.com.br/gateway/v1/mge/service.sbr?serviceName=CRUDServiceProvider.loadRecords&outputType=json
```

Entidade:

```text
Produto
```

Filtro:

```text
this.CODPROD = {codprod}
```

Campos consultados:

```text
AD_DESCLONGALV
AD_DESCTECNICALV
AD_URLIMGLV
AD_DIFERENCIAISLV
AD_URLDEMATERIAIS
AD_VTEXCATEGORIA
AD_USADOLV
AD_ATIVOLV
ENDIMAGEM
```

## Critérios obrigatórios

O código atualmente exige:

```text
AD_USADOLV
AD_ATIVOLV
AD_VTEXCATEGORIA
```

Os demais campos são coletados, mas não impedem a execução quando vazios.

Resultado:

```text
TRUE  → continua integração
FALSE → interrompe integração
```

---

# 8. Etapa 3 — Verificação do produto na VTEX

Arquivo:

```text
vtex/vtex_utils.py
```

Função:

```python
sankhya_product_exist_no_vtex(codprod)
```

Chamada:

```python
vtex_head(
    f"catalog_system/pvt/products/productgetbyrefid/{codprod}"
)
```

Endpoint:

```http
HEAD /api/catalog_system/pvt/products/productgetbyrefid/{CODPROD}
```

Resultado:

```text
200 → produto existe
outro status → produto considerado inexistente
```

Esse resultado determina o ramo do processo.

---

# 9. Fluxo de criação

Função:

```python
vtex_process_new_product(codprod)
```

Sequência:

```text
vtex_create_product
        │
        ▼
vtex_update_basic_info
        │
        ▼
vtex_update_specifications
        │
        ▼
vtex_create_sku
        │
        ▼
vtex_create_sku_file
```

---

# 10. Consulta das informações básicas

Arquivo:

```text
sankhya/snk_fetch.py
```

Função:

```python
fetch_sankhya_basic_info(codprod)
```

Serviço:

```text
CRUDServiceProvider.loadRecords
```

Campos:

```text
CODPROD
DESCRPROD
MARCA
AD_VTEXCATEGORIA
AD_MODELOREF
AD_DESCLONGALV
```

Transformações:

```text
CODPROD
    → RefId

DESCRPROD
    → Name
    → Title

MARCA
    → BrandName

AD_VTEXCATEGORIA
    → CategoryId

AD_DESCLONGALV
    → Description
```

Também são gerados pelo código:

```text
LinkId
ReleaseDate
MetaTagDescription
IsVisible
IsActive
ShowWithoutStock
Score
```

---

# 11. Criação do produto VTEX

Arquivo:

```text
vtex/vtex_create.py
```

Função:

```python
vtex_create_product(codprod)
```

Endpoint:

```http
POST /api/catalog/pvt/product
```

Payload principal:

```json
{
  "Name": "...",
  "CategoryId": "...",
  "BrandName": "...",
  "RefId": "...",
  "Title": "...",
  "LinkId": "...",
  "Description": "...",
  "ReleaseDate": "...",
  "IsVisible": true,
  "IsActive": true,
  "MetaTagDescription": "...",
  "ShowWithoutStock": false,
  "Score": 1
}
```

---

# 12. Recuperação do Product ID

Arquivo:

```text
vtex/vtex_fetch.py
```

Função:

```python
fetch_vtex_id(codprod)
```

Endpoint:

```http
GET /api/catalog_system/pvt/products/productgetbyrefid/{CODPROD}
```

Retorno utilizado:

```python
result["Id"]
```

Esse valor é armazenado conceitualmente como:

```text
VTEX Product ID
```

---

# 13. Atualização das informações básicas

Arquivo:

```text
vtex/vtex_update.py
```

Função:

```python
vtex_update_basic_info(codprod)
```

Endpoint:

```http
PUT /api/catalog/pvt/product/{ProductId}
```

A função consulta novamente o Sankhya e substitui os dados atuais do produto na VTEX.

---

# 14. Especificações

Função:

```python
vtex_update_specifications(codprod)
```

Consulta Sankhya:

```python
fetch_sankhya_grupo_informacoes_vtex(codprod)
```

Campos:

```text
AD_DESCLONGALV
AD_DESCTECNICALV
AD_URLIMGLV
AD_DIFERENCIAISLV
AD_URLDEMATERIAIS
```

Mapeamento:

| ID | Nome VTEX | Origem |
|---:|---|---|
| 20 | Descrição | `AD_DESCLONGALV` |
| 21 | Diferenciais | `AD_DIFERENCIAISLV` |
| 22 | Características | `AD_DESCTECNICALV` |
| 23 | Download de materiais | `AD_URLDEMATERIAIS` |
| 24 | Imagem da descrição | `AD_URLIMGLV` |

Endpoint:

```http
POST /api/catalog_system/pvt/products/{ProductId}/specification
```

---

# 15. SKU

Arquivo:

```text
sankhya/snk_fetch.py
```

Função de origem:

```python
fetch_sankhya_sku_info(codprod)
```

Campos:

```text
DESCRPROD
CODPROD
AD_URLVIDEOLV
AD_ALTURALV
AD_COMPRIMENTOLV
AD_LARGURALV
AD_PESOLV
M3
AD_UNIDADELV
```

Mapeamento:

```text
DESCRPROD           → Name
CODPROD             → RefId
AD_ALTURALV         → Height / PackagedHeight
AD_COMPRIMENTOLV    → Length / PackagedLength
AD_LARGURALV        → Width / PackagedWidth
AD_PESOLV           → WeightKg / PackagedWeightKg
M3                  → CubicWeight
AD_UNIDADELV        → MeasurementUnit
CODPROD             → ManufacturerCode
AD_URLVIDEOLV       → Videos
```

---

# 16. Criação do SKU

Arquivo:

```text
vtex/vtex_create.py
```

Função:

```python
vtex_create_sku(codprod)
```

Endpoint:

```http
POST /api/catalog/pvt/stockkeepingunit
```

Campos enviados incluem:

```text
ProductId
IsActive
ActivateIfPossible
Name
RefId
PackagedHeight
PackagedLength
PackagedWidth
PackagedWeightKg
Height
Length
Width
WeightKg
CubicWeight
IsKit
CreationDate
ManufacturerCode
CommercialConditionId
MeasurementUnit
UnitMultiplier
```

---

# 17. Recuperação do SKU ID

Função:

```python
fetch_vtex_sku_id(vtex_id)
```

Endpoint:

```http
GET /api/catalog_system/pvt/sku/stockkeepingunitByProductId/{ProductId}
```

O código utiliza:

```python
result[0]["Id"]
```

como `SKUId`.

---

# 18. Verificação da existência do SKU

Função:

```python
vtex_exist_sku_id(codprod)
```

Fluxo:

```text
CODPROD
   │
   ▼
GET Product by RefId
   │
   ▼
ProductId
   │
   ▼
HEAD SKU by ProductId
```

Endpoint:

```http
HEAD /api/catalog_system/pvt/sku/stockkeepingunitByProductId/{ProductId}
```

---

# 19. Atualização do SKU

Função:

```python
vtex_update_sku(codprod)
```

Endpoint:

```http
PUT /api/catalog/pvt/stockkeepingunit/{SKUId}
```

O SKU é atualizado com os dados atuais do Sankhya.

---

# 20. SKU File / imagem

Origem:

```python
fetch_sankhya_sku_file_info(codprod)
```

Campos:

```text
CODPROD
DESCRPROD
ENDIMAGEM
```

Caso não haja URL, o código utiliza:

```text
https://img.casacontente.com.br/{CODPROD}.jpg
```

Criação:

```python
vtex_create_sku_file(codprod)
```

Endpoint:

```http
POST /api/catalog/pvt/stockkeepingunit/{SKUId}/file
```

Payload:

```json
{
  "IsMain": true,
  "Label": "Main",
  "Name": "...",
  "Text": "...",
  "Url": "...",
  "Position": 0
}
```

---

# 21. Atualização de SKU File

Existe uma função específica:

```python
vtex_update_sku_file(codprod)
```

Ela utiliza:

```http
GET /api/catalog/pvt/stockkeepingunit/{SKUId}/file
```

para recuperar o `SKUFileId` e depois:

```http
PUT /api/catalog/pvt/stockkeepingunit/{SKUId}/file/{SKUFileId}
```

Entretanto, **essa função não é chamada pelo fluxo principal atual**.

No caminho de atualização de produto, o `main.py` chama:

```python
vtex_create_sku_file(codprod)
```

e não:

```python
vtex_update_sku_file(codprod)
```

---

# 22. Fluxo completo de criação

```text
CODPROD
   │
   ▼
check_sankhya_ecommerce_infos
   │
   ├── inválido → STOP
   │
   ▼
sankhya_product_exist_no_vtex
   │
   └── não existe
          │
          ▼
vtex_create_product
          │
          ▼
fetch_sankhya_basic_info
          │
          ▼
POST /catalog/pvt/product
          │
          ▼
fetch_vtex_id
          │
          ▼
vtex_update_basic_info
          │
          ▼
PUT /catalog/pvt/product/{id}
          │
          ▼
vtex_update_specifications
          │
          ▼
POST /catalog_system/pvt/products/{id}/specification
          │
          ▼
vtex_create_sku
          │
          ▼
POST /catalog/pvt/stockkeepingunit
          │
          ▼
fetch_vtex_sku_id
          │
          ▼
vtex_create_sku_file
          │
          ▼
POST /catalog/pvt/stockkeepingunit/{sku}/file
```

---

# 23. Fluxo completo de atualização

```text
CODPROD
   │
   ▼
check_sankhya_ecommerce_infos
   │
   ▼
sankhya_product_exist_no_vtex
   │
   └── existe
          │
          ▼
vtex_update_basic_info
          │
          ▼
PUT /catalog/pvt/product/{id}
          │
          ▼
vtex_update_specifications
          │
          ▼
POST /catalog_system/pvt/products/{id}/specification
          │
          ▼
vtex_exist_sku_id
          │
       ┌──┴──┐
       │     │
      SIM   NÃO
       │     │
       ▼     ▼
 update   create
  SKU       SKU
       │     │
       └──┬──┘
          ▼
vtex_create_sku_file
          │
          ▼
POST /catalog/pvt/stockkeepingunit/{sku}/file
```

---

# 24. Tabela completa de endpoints

## Sankhya

| Método | Endpoint | Função no projeto | Finalidade |
|---|---|---|---|
| POST | `https://api.sankhya.com.br/login` | `snk_bearer_token()` | Autenticação |
| GET | `https://api.sankhya.com.br/gateway/v1/mge/service.sbr?serviceName=CRUDServiceProvider.loadRecords&outputType=json` | `snk_get()` | Consultar entidades |
| POST | `https://api.sankhya.com.br/gateway/v1/mge/service.sbr?serviceName=DatasetSP.save&outputType=json` | `snk_post()` | Gravar entidades |

## VTEX

| Método | Endpoint | Função |
|---|---|---|
| HEAD | `/api/catalog_system/pvt/products/productgetbyrefid/{CODPROD}` | `sankhya_product_exist_no_vtex()` |
| GET | `/api/catalog_system/pvt/products/productgetbyrefid/{CODPROD}` | `fetch_vtex_id()` |
| POST | `/api/catalog/pvt/product` | `vtex_create_product()` |
| PUT | `/api/catalog/pvt/product/{ProductId}` | `vtex_update_basic_info()` |
| POST | `/api/catalog_system/pvt/products/{ProductId}/specification` | `vtex_update_specifications()` |
| POST | `/api/catalog/pvt/stockkeepingunit` | `vtex_create_sku()` |
| GET | `/api/catalog_system/pvt/sku/stockkeepingunitByProductId/{ProductId}` | `fetch_vtex_sku_id()` |
| HEAD | `/api/catalog_system/pvt/sku/stockkeepingunitByProductId/{ProductId}` | `vtex_exist_sku_id()` |
| PUT | `/api/catalog/pvt/stockkeepingunit/{SKUId}` | `vtex_update_sku()` |
| POST | `/api/catalog/pvt/stockkeepingunit/{SKUId}/file` | `vtex_create_sku_file()` |
| GET | `/api/catalog/pvt/stockkeepingunit/{SKUId}/file` | `fetch_vtex_sku_file_id()` |
| PUT | `/api/catalog/pvt/stockkeepingunit/{SKUId}/file/{SKUFileId}` | `vtex_update_sku_file()` |
| GET | `/api/catalog_system/pub/category/tree/2` | `get_vtex_category_tree()` |

---

# 25. Sincronização de departamentos

Existe um fluxo separado:

```python
sync_vtex_departments()
```

Arquivo:

```text
vtex/vtex_sync.py
```

Processo:

```text
VTEX category tree
        │
        ▼
GET /api/catalog_system/pub/category/tree/2
        │
        ▼
DataFrame VTEX
        │
        ├──────────────┐
        │              │
        ▼              ▼
DataFrame Sankhya   comparação
        │              │
        └──────┬───────┘
               ▼
         diferenças
               │
               ▼
DatasetSP.save
               │
               ▼
AD_ADVTEXCATEGORIAS
```

Consulta Sankhya:

```text
CRUDServiceProvider.loadRecords
```

Entidade:

```text
AD_ADVTEXCATEGORIAS
```

Campos:

```text
ID_CATEGORIA
ID_CATEGORIAPAI
NOME
GRAU
ANALITICO
```

Gravação:

```text
DatasetSP.save
```

Esse fluxo está disponível no código, mas a chamada no `main.py` está comentada.

---

# 26. Cliente VTEX

Arquivo:

```text
vtex/vtex_client.py
```

Base URL:

```text
https://{VTEX_ACCOUNT_NAME}.vtexcommercestable.com.br/api
```

Headers:

```http
Accept: application/json
Content-Type: application/json
Cache-Control: no-cache
Pragma: no-cache
X-VTEX-API-AppKey: <VTEX_APP_KEY>
X-VTEX-API-AppToken: <VTEX_APP_TOKEN>
```

Funções genéricas:

```python
vtex_head()
vtex_get()
vtex_post()
vtex_put()
```

Todas utilizam uma `requests.Session()` compartilhada.

---

# 27. Retry e resiliência

## Sankhya

As funções de autenticação e consulta usam `tenacity`.

Configuração principal:

```text
5 tentativas
```

Timeout:

```text
30 segundos
```

## VTEX

As funções genéricas utilizam:

```text
10 tentativas
backoff exponencial
máximo de 30 segundos entre tentativas
timeout de 30 segundos
```

A sessão HTTP utiliza:

```text
pool_connections = 100
pool_maxsize = 100
pool_block = True
```

---

# 28. Pontos de atenção técnicos

## 28.1 Preço

Não existe no fluxo principal uma chamada para API de Pricing.

Portanto:

```text
Sankhya preço
      X
VTEX preço
```

não está implementado atualmente.

## 28.2 Estoque

Também não existe no fluxo principal uma chamada para API de estoque/logística.

Portanto:

```text
Sankhya estoque
      X
VTEX estoque
```

não está implementado atualmente.

## 28.3 SKU File no update

A função:

```python
vtex_update_sku_file()
```

existe, mas não é chamada por:

```python
vtex_process_update_product()
```

O update chama:

```python
vtex_create_sku_file()
```

## 28.4 Lista fixa de produtos

O `main.py` possui atualmente:

```python
produtos = [412158]
```

Não existe no fluxo principal atual uma rotina que busque automaticamente todos os produtos do Sankhya.

## 28.5 Idempotência

O processo tenta ser idempotente através da verificação de existência por `RefId`, mas a criação de SKU File merece atenção porque o caminho de atualização utiliza a operação de criação.

---

# 29. Variáveis de ambiente

```text
SANKHYA_TOKEN
SANKHYA_APPKEY
SANKHYA_PASSWORD
SANKHYA_USERNAME

VTEX_APP_KEY
VTEX_APP_TOKEN
VTEX_BASE_URL
VTEX_ACCOUNT_NAME

BOTTOKEN
CHATID

APP_ENV
```

Credenciais reais não devem ser armazenadas no Git.

---

# 30. Referências oficiais

- Sankhya Developer: https://developer.sankhya.com.br/
- VTEX Developers: https://developers.vtex.com/
- Requests: https://requests.readthedocs.io/
- Tenacity: https://tenacity.readthedocs.io/
- Pytest: https://docs.pytest.org/

---

# 31. Resumo executivo

O fluxo efetivo é:

```text
Sankhya
  │
  ├── autentica
  │
  ├── valida produto
  │
  ├── consulta dados do produto
  │
  ├── consulta dados de especificação
  │
  ├── consulta dados do SKU
  │
  └── consulta imagem
          │
          ▼
        Python
          │
          ├── transforma dados
          │
          └── decide CREATE / UPDATE
                    │
                    ▼
                   VTEX
                    │
                    ├── Produto
                    ├── Especificações
                    ├── SKU
                    └── SKU File
```

O `CODPROD` é a chave de correlação entre os sistemas.

O fluxo atualmente é de **catálogo**, não de sincronização completa de comércio eletrônico: **produto, especificações, SKU e imagem são tratados; preço e estoque ainda não são enviados pelo fluxo principal.**
