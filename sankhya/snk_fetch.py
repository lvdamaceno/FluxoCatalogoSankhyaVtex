import json
import logging

from sankhya.snk_client import snk_get


def fetch_sankhya_products():
    products_list = []
    return products_list

def fetch_sankhya_departaments():
    payload = {
        "serviceName": "br.com.sankhya.menu.adicional.AD_ADVTEXCATEGORIAS",
        "requestBody": {
            "dataSet": {
                "rootEntity": "AD_ADVTEXCATEGORIAS",
                "offsetPage": "0",
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
    service = "CRUDServiceProvider.loadRecords"
    response = snk_get(payload, service)
    logging.info(f"Sankhya Departaments: {json.dumps(response, indent=4, ensure_ascii=False)}")