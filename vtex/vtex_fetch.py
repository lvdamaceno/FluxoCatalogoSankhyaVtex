import logging

import requests

from vtex.vtex_df_departaments import parse_categories, create_df_departaments_vtex
from vtex.vtex_get import get_vtex_category_tree


def get_vtex_sku(sankhya_product):
    """
    :param sankhya_product:
    :return: sku_vtex or None
    """
    pass

def get_vtex_id(sankhya_product):
    """
    :param sankhya_product:
    :return: id_vtex or None
    """
    pass

def fetch_vtex_departaments():
    try:
        categorias = get_vtex_category_tree()
        linhas = parse_categories(categorias)
        return create_df_departaments_vtex(linhas)
    except requests.exceptions.RequestException as e:
        logging.warning(f"Não foi possível capturar a lista de categorias VTEX: {e}")
        return None