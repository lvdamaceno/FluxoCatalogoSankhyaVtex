import logging
import requests
from sankhya.snk_client import snk_get
import pandas as pd


def fetch_sankhya_products():
    try:
        all_entities = []
        offset_page = 0
        service = "CRUDServiceProvider.loadRecords"

        while True:
            # monta o payload com a página atual
            payload = {
                "serviceName": "CRUDServiceProvider.loadRecords",
                "requestBody": {
                    "dataSet": {
                        "rootEntity": "Produto",
                        "offsetPage": str(offset_page),
                        "criteria": {
                            "expression": {
                                "$": "AD_USADOLV = 'S'"
                            }
                        },
                        "entity": [
                            {
                                "fieldset": {
                                    "list": "CODPROD"
                                }
                            }
                        ]
                    }
                }
            }

            # faz a requisição
            response = snk_get(payload, service)
            entities = response \
                .get("responseBody", {}) \
                .get("entities", {}) \
                .get("entity", [])

            # agrega os resultados
            all_entities.extend(entities)

            # verifica se há mais páginas
            has_more = response \
                           .get("responseBody", {}) \
                           .get("entities", {}) \
                           .get("hasMoreResult", "false") \
                           .lower() == "true"

            logging.info(f"Página {offset_page} trouxe {len(entities)} registros; hasMoreResult={has_more}")

            if not has_more:
                break

            offset_page += 1

        # retorna um único JSON com todas as entidades
        products = []
        for product in all_entities:
            products.append(product['f0']['$'])
        return products
    except requests.exceptions.RequestException as e:
        logging.error("Erro na requisição Sankhya:", exc_info=e)
        return None


def get_sankhya_departaments():
    try:
        all_entities = []
        offset_page = 0
        service = "CRUDServiceProvider.loadRecords"

        while True:
            # monta o payload com a página atual
            payload = {
                "serviceName": "br.com.sankhya.menu.adicional.AD_ADVTEXCATEGORIAS",
                "requestBody": {
                    "dataSet": {
                        "rootEntity": "AD_ADVTEXCATEGORIAS",
                        "offsetPage": str(offset_page),
                        "entity": [
                            {
                                "fieldset": {
                                    "list": "ID_CATEGORIA, ID_CATEGORIAPAI, NOME, GRAU, ANALITICO"
                                }
                            }
                        ]
                    }
                }
            }

            # faz a requisição
            response = snk_get(payload, service)
            entities = response \
                .get("responseBody", {}) \
                .get("entities", {}) \
                .get("entity", [])

            # agrega os resultados
            all_entities.extend(entities)

            # verifica se há mais páginas
            has_more = response \
                           .get("responseBody", {}) \
                           .get("entities", {}) \
                           .get("hasMoreResult", "false") \
                           .lower() == "true"

            logging.info(f"Página {offset_page} trouxe {len(entities)} registros; hasMoreResult={has_more}")

            if not has_more:
                break

            offset_page += 1

        # retorna um único JSON com todas as entidades
        return all_entities
    except requests.exceptions.RequestException as e:
        logging.error("Erro na requisição Sankhya:", exc_info=e)
        return None


def fetch_sankhya_departaments():
    try:
        colunas = ['ID_CATEGORIA', 'GRAU', 'ANALITICO', 'ID_CATEGORIAPAI', 'NOME']
        sankhya_departaments = get_sankhya_departaments()
        linhas = []
        for departamento in sankhya_departaments:
            id_categoria = departamento.get("f0").get("$")
            grau = departamento.get("f3").get("$")
            analitico = departamento.get("f4").get("$")
            id_categoria_pai = departamento.get("f1").get("$")
            nome = departamento.get("f2").get("$")
            linhas.append([id_categoria, grau, analitico, id_categoria_pai, nome])
        df = pd.DataFrame(linhas, columns=colunas)
        logging.info(f"Sankhya departaments DataFrame creation {df}")
        return df
    except requests.exceptions.RequestException as e:
        logging.error(e)
