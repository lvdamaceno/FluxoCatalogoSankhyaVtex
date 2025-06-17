import logging

import requests

from vtex.vtex_client import vtex_get
from vtex.vtex_df_departaments import parse_categories, create_df_departaments_vtex
from vtex.vtex_get import get_vtex_category_tree


def sankhya_product_exist_no_vtex(codprod):
    try:
        service = f"catalog_system/pvt/products/productgetbyrefid/{codprod}"
        response = vtex_get(service)
        return bool(response)
    except Exception as e:
        logging.error(f"Produto {codprod} não existe no Vtex, {e}")
        return False


def fetch_vtex_departaments():
    try:
        categorias = get_vtex_category_tree()
        linhas = parse_categories(categorias)
        return create_df_departaments_vtex(linhas)
    except requests.exceptions.RequestException as e:
        logging.error(f"Não foi possível capturar a lista de categorias VTEX: {e}")
        return None