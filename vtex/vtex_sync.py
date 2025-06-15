import json
import logging
import requests
import pandas as pd

from sankhya.snk_fetch import fetch_sankhya_departaments
from utils.utils import fill_with_zeros
from vtex.vtex_client import vtex_get


def get_vtex_category_tree():
    """Obtém a árvore completa de categorias (nível 2) da VTEX."""
    return vtex_get("catalog_system/pub/category/tree/2")


def parse_categories(categorias):
    """Converte a árvore de categorias em linhas para o DataFrame."""
    linhas = []

    for categoria in categorias:
        parent_id = fill_with_zeros(categoria['id'])
        parent_name = categoria['name']
        parent_key = f"{parent_id}{fill_with_zeros()}"  # Ex: 001000

        # Categorias pais
        linhas.append([parent_key, 1, 'N', '-999999999', parent_name])

        # Categorias filhas
        for child in categoria.get('children', []):
            child_id = fill_with_zeros(child['id'])
            child_name = child['name']
            child_key = f"{parent_id}{child_id}"
            linhas.append([child_key, 2, 'S', parent_key, child_name])

    return linhas


def create_df_departaments_vtex(linhas):
    colunas = ['ID_CATEGORIA', 'GRAU', 'ANALITICO', 'ID_CATEGORIAPAI', 'NOME']
    df = pd.DataFrame(linhas, columns=colunas)
    logging.info(df)
    return df


def fetch_vtex_departaments():
    try:
        categorias = get_vtex_category_tree()
        linhas = parse_categories(categorias)
        return create_df_departaments_vtex(linhas)
    except requests.exceptions.RequestException as e:
        logging.warning(f"Não foi possível capturar a lista de categorias VTEX: {e}")
        return None


def sync_vtex_departments():
    # fetch_vtex_departaments()
    fetch_sankhya_departaments()

    # comparar o df com a tabela do sankhya
    # se alguma linha nao existir no vtex fazer a criacao
    # se alguma linha nao existir no sankhya fazer a criacao
