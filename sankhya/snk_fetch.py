import json
import logging
import requests
from sankhya.snk_client import snk_get
from datetime import date
import pandas as pd

from sankhya.snk_utils import extract_department_id, link_id, meta_tag_description
from utils.utils import now_iso8601_7


def sankhya_departaments():
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

            logging.info(f"📊 Página {offset_page} trouxe {len(entities)} registros; hasMoreResult={has_more}")

            if not has_more:
                break

            offset_page += 1

        # retorna um único JSON com todas as entidades
        return all_entities
    except requests.exceptions.RequestException as e:
        logging.error("❌ Erro na requisição Sankhya:", exc_info=e)
        return None


def fetch_sankhya_departaments():
    try:
        colunas = ['ID_CATEGORIA', 'GRAU', 'ANALITICO', 'ID_CATEGORIAPAI', 'NOME']
        departaments = sankhya_departaments()
        linhas = []
        for departamento in departaments:
            id_categoria = departamento.get("f0").get("$")
            grau = departamento.get("f3").get("$")
            analitico = departamento.get("f4").get("$")
            id_categoria_pai = departamento.get("f1").get("$")
            nome = departamento.get("f2").get("$")
            linhas.append([id_categoria, grau, analitico, id_categoria_pai, nome])
        df = pd.DataFrame(linhas, columns=colunas)
        logging.info(f"🗂️ Sankhya departaments DataFrame creation {df}")
        return df
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Erro ao buscar departamentos: {e}")


def fetch_sankhya_grupo_informacoes_vtex(codprod):
    try:
        service = "CRUDServiceProvider.loadRecords"
        payload = {
            "serviceName": "CRUDServiceProvider.loadRecords",
            "requestBody": {
                "dataSet": {
                    "rootEntity": "Produto",
                    "includePresentationFields": "N",
                    "offsetPage": "0",
                    "criteria": {
                        "expression": {
                            "$": f"this.CODPROD = {codprod}"
                        }
                    },
                    "entity": {
                        "fieldset": {
                            "list":
                                    "AD_DESCLONGALV,"
                                    "AD_DESCTECNICALV,"
                                    "AD_URLIMGLV,"
                                    "AD_DIFERENCIAISLV,"
                                    "AD_URLDEMATERIAIS"
                        }
                    }
                }
            }
        }
        result = snk_get(payload, service)
        entidade = result.get("responseBody", {}).get("entities", {}).get("entity", {})
        info = {
            "Descrição": entidade.get("f0", {}).get("$") or "",
            "Características": entidade.get("f1", {}).get("$") or "",
            "Imagem": entidade.get("f2", {}).get("$") or f"https://img.casacontente.com.br/{codprod}.jpg",
            "Diferenciais": entidade.get("f3", {}).get("$") or "",
            "Download": entidade.get("f4", {}).get("$") or ""
        }
        logging.info(f"📊 Info: {info}")
        return info
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Falha ao capturar informacoes do produto {codprod}", e)


def fetch_sankhya_basic_info(codprod):
    try:
        service = "CRUDServiceProvider.loadRecords"
        payload = {
            "serviceName": "CRUDServiceProvider.loadRecords",
            "requestBody": {
                "dataSet": {
                    "rootEntity": "Produto",
                    "includePresentationFields": "N",
                    "offsetPage": "0",
                    "criteria": {
                        "expression": {
                            "$": f"this.CODPROD = {codprod}"
                        }
                    },
                    "entity": {
                        "fieldset": {
                            "list": "CODPROD, DESCRPROD, MARCA, AD_VTEXCATEGORIA, AD_MODELOREF, AD_DESCLONGALV"
                        }
                    }
                }
            }
        }
        result = snk_get(payload, service)
        entidade = result.get("responseBody", {}).get("entities", {}).get("entity", {})

        name = entidade.get("f1", {}).get("$") or ""
        refid = entidade.get("f0", {}).get("$") or ""
        department_id = extract_department_id(entidade.get("f3", {}).get("$") or "")
        brand_name = entidade.get("f2", {}).get("$") or ""
        description = entidade.get("f5", {}).get("$") or ""

        info = {
            "Name": name.replace("/", ""),
            "CategoryId": department_id,
            "BrandName": brand_name,
            "RefId": refid,
            "Title": name.replace("/", ""),
            "LinkId": link_id(name, refid).replace("/", ""),
            "Description": description,
            "ReleaseDate": date.today().isoformat(),
            "IsVisible": True,
            "IsActive": True,
            "MetaTagDescription": meta_tag_description(name).replace("/", ""),
            "ShowWithoutStock": False,
            "Score": 1
        }
        logging.info(f"📊 Info: {json.dumps(info, indent=4, ensure_ascii=False)}")
        return info
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Falha ao capturar informacoes básicas do produto {codprod}", e)


def fetch_sankhya_sku_info(codprod):
    try:
        service = "CRUDServiceProvider.loadRecords"
        payload = {
            "serviceName": "CRUDServiceProvider.loadRecords",
            "requestBody": {
                "dataSet": {
                    "rootEntity": "Produto",
                    "includePresentationFields": "N",
                    "offsetPage": "0",
                    "criteria": {
                        "expression": {
                            "$": f"this.CODPROD = {codprod}"
                        }
                    },
                    "entity": {
                        "fieldset": {
                            "list": "DESCRPROD, CODPROD, AD_URLVIDEOLV, AD_ALTURALV, AD_COMPRIMENTOLV, AD_LARGURALV, "
                                    "AD_PESOLV, M3, AD_UNIDADELV"
                        }
                    }
                }
            }
        }
        result = snk_get(payload, service)
        entidade = result.get("responseBody", {}).get("entities", {}).get("entity", {})

        name = entidade.get("f0", {}).get("$") or ""
        refid = entidade.get("f1", {}).get("$") or ""
        video = entidade.get("f2", {}).get("$") or ""
        altura = entidade.get("f3", {}).get("$") or ""
        comprimento = entidade.get("f4", {}).get("$") or ""
        largura = entidade.get("f5", {}).get("$") or ""
        peso = entidade.get("f6", {}).get("$") or ""
        cubagem = entidade.get("f7", {}).get("$") or ""
        unidade = entidade.get("f8", {}).get("$") or ""
        creation_date = now_iso8601_7()

        info = {
            "Name": name,
            "RefId": refid,
            "PackagedHeight": altura,
            "PackagedLength": comprimento,
            "PackagedWidth": largura,
            "PackagedWeightKg": peso,
            "Height": altura,
            "Length": comprimento,
            "Width": largura,
            "WeightKg": peso,
            "CubicWeight": cubagem,
            "CreationDate": creation_date,
            "ManufacturerCode": refid,
            "MeasurementUnit": unidade,
            "Videos": [video]
        }
        logging.info(f"📊 Info: {json.dumps(info, indent=4, ensure_ascii=False)}")
        return info
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Falha ao capturar informacoes de sku do produto {codprod}", e)


def fetch_sankhya_sku_file_info(codprod):
    try:
        service = "CRUDServiceProvider.loadRecords"
        payload = {
            "serviceName": "CRUDServiceProvider.loadRecords",
            "requestBody": {
                "dataSet": {
                    "rootEntity": "Produto",
                    "includePresentationFields": "N",
                    "offsetPage": "0",
                    "criteria": {
                        "expression": {
                            "$": f"this.CODPROD = {codprod}"
                        }
                    },
                    "entity": {
                        "fieldset": {
                            "list": "CODPROD, DESCRPROD, ENDIMAGEM"
                        }
                    }
                }
            }
        }
        result = snk_get(payload, service)
        entidade = result.get("responseBody", {}).get("entities", {}).get("entity", {})

        codprod = entidade.get("f0", {}).get("$") or ""
        name = entidade.get("f1", {}).get("$") or ""
        endimagem = entidade.get("f2", {}).get("$") or f"https://img.casacontente.com.br/{codprod}.jpg"

        info = {
            "IsMain": True,
            "Label": "Main",
            "Name": link_id(name, codprod),
            "Text": link_id(name, codprod),
            "Url": endimagem,
            "Position": 0
        }
        logging.info(f"📊 Sku file info: {json.dumps(info, indent=4, ensure_ascii=False)}")
        return info

    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Falha ao capturar informacoes de sku file do produto {codprod}", e)