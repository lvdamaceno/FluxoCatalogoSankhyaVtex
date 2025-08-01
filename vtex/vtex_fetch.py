import json
import logging
import requests

from vtex.vtex_client import vtex_get, vtex_head
from vtex.vtex_df_departaments import parse_categories, create_df_departaments_vtex
from vtex.vtex_get import get_vtex_category_tree

def fetch_vtex_departaments():
    try:
        categorias = get_vtex_category_tree()
        linhas = parse_categories(categorias)
        return create_df_departaments_vtex(linhas)
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Não foi possível capturar a lista de categorias VTEX: {e}")
        return None


def fetch_vtex_id(codprod):
    logging.info(f"📊 Buscando Vtex Id")
    service = f"catalog_system/pvt/products/productgetbyrefid/{codprod}"
    try:
        result = vtex_get(service)
        logging.info(f"📊 Fetch Vtex Id: {json.dumps(result, indent=4)}")
        vtex_id = result["Id"]
        logging.info(f"📊 VTEX ID: {vtex_id}")
        return vtex_id
    except requests.exceptions.RequestException as e:
        logging.error(f"🔴 Falha ao capturar o id do produto {codprod}: {e}")
        return None


def fetch_vtex_sku_id(vtex_id):
    service = f"catalog_system/pvt/sku/stockkeepingunitByProductId/{vtex_id}"
    try:
        result = vtex_get(service)
        sku_id = result[0]['Id']
        logging.info(f"📊 SKU ID: {sku_id}")
        return sku_id
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Falha ao capturar o sku do id {vtex_id}: {e}")
        return None


def vtex_exist_sku_id(codprod):
    logging.info(f"🟢 Checando se existe sku para o produto {codprod}")
    vtex_id = fetch_vtex_id(codprod)
    path = f'catalog_system/pvt/sku/stockkeepingunitByProductId/{vtex_id}'
    if vtex_head(path):
        logging.warning(f"⚠️ Produto {codprod} já tem um sku")
        return True
    else:
        logging.warning(f"⚠️ Produto {codprod} não tem um sku")
        return False


def fetch_vtex_sku_file_id(codprod):
    vtex_id = fetch_vtex_id(codprod)
    sku_id = fetch_vtex_sku_id(vtex_id)
    path = f"catalog/pvt/stockkeepingunit/{sku_id}/file"
    try:
        result = vtex_get(path)
        if result:
            sku_file_id = result[0]['Id']
            logging.info(f"📊 SKU file ID: {sku_file_id}")
            return sku_file_id
        else:
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Falha ao capturar o sku file do id {vtex_id}: {e}")
        return None