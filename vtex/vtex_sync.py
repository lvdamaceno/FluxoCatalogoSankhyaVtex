import json
import logging
import requests
import pandas as pd

from utils.utils import fill_with_zeros
from vtex.vtex_client import vtex_get

def fetch_parent_departament():
    pass

def fetch_vtex_departaments():
    colunas = ['ID_CATEGORIA', 'GRAU', 'ANALITICO', 'ID_CATEGORIAPAI', 'NOME']
    linhas = []
    try:
        response = vtex_get("catalog_system/pub/category/tree/2")
        for resp in response:
            parent_id = fill_with_zeros(resp['id'])
            parent_name = resp['name']
            linhas.append([f"{parent_id}{fill_with_zeros()}", 1, 'N', '-999999999', parent_name])
            for item in resp.get('children', []):
                children_id = fill_with_zeros(item['id'])
                children_name = item['name']
                linhas.append([f"{parent_id}{children_id}", 2, 'S', f"{parent_id}{fill_with_zeros()}", children_name])
        df = pd.DataFrame(linhas, columns=colunas)
        logging.info(df)
        return df
    except requests.exceptions.RequestException as e:
        logging.warning(f"Não foi possível capturar a lista de Ids: {e}")
        return None

def sync_vtex_departments():
    df = fetch_vtex_departaments()
    # comparar o df com a tabela do sankhya
    # se alguma linha nao existir no vtex fazer a criacao
    # se alguma linha nao existir no sankhya fazer a criacao
