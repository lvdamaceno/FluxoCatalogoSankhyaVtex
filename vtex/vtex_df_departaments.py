import logging

import pandas as pd
import requests

from utils.utils import fill_with_zeros


def parse_categories(categorias):
    """Converte a árvore de categorias em linhas para o DataFrame."""
    linhas = []

    for categoria in categorias:
        parent_id = categoria['id']
        parent_name = categoria['name']
        parent_key = f"{parent_id}{fill_with_zeros()}"  # Ex: 001000

        # Categorias pais
        linhas.append([parent_key, '1', 'N', '-999999999', parent_name])

        # Categorias filhas
        for child in categoria.get('children', []):
            child_id = fill_with_zeros(child['id'])
            child_name = child['name']
            child_key = f"{parent_id}{child_id}"
            linhas.append([child_key, '2', 'S', parent_key, child_name])

    return linhas


def create_df_departaments_vtex(linhas):
    try:
        colunas = ['ID_CATEGORIA', 'GRAU', 'ANALITICO', 'ID_CATEGORIAPAI', 'NOME']
        df = pd.DataFrame(linhas, columns=colunas)
        df['NOME'] = df['NOME'].str.upper()
        logging.info(f"🟢 Vtex departaments DataFrame creation {df}")
        return df
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Erro ao criar df de departamentos: {e}")
