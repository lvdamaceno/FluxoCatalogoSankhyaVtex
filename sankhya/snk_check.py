import logging
import requests
from sankhya.snk_client import snk_get


def check_sankhya_ecommerce_infos(codprod):
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
                                "AD_URLDEMATERIAIS,"
                                "AD_VTEXCATEGORIA,"
                                "AD_USADOLV,"
                                "AD_ATIVOLV,"
                                "ENDIMAGEM"
                        }
                    }
                }
            }
        }
        result = snk_get(payload, service)
        entidade = result.get("responseBody", {}).get("entities", {}).get("entity", {})
        infos = {
            "Descrição": entidade.get("f0", {}).get("$") or "",
            "Características": entidade.get("f1", {}).get("$") or "",
            "Imagem Descrição": entidade.get("f2", {}).get("$") or "",
            "Diferenciais": entidade.get("f3", {}).get("$") or "",
            "Download": entidade.get("f4", {}).get("$") or "",
            "Categoria Vtex": entidade.get("f5", {}).get("$") or "",
            "Usado no Ecommerce": entidade.get("f6", {}).get("$") or "",
            "Situação no Ecommerce": entidade.get("f7", {}).get("$") or "",
            "Imagem Principal": entidade.get("f8", {}).get("$") or ""
        }
        decricao = bool(infos.get('Descrição'))
        caracteristicas = bool(infos.get('Características'))
        imagem_descricao = bool(infos.get('Imagem Descrição'))
        usado = bool(infos.get('Usado no Ecommerce'))
        situacao = bool(infos.get('Situação no Ecommerce'))
        categoria = bool(infos.get('Categoria Vtex'))
        # imagem_principal = bool(infos.get('Imagem Principal'))

        valid_flags = {
            # 'Descrição': decricao,
            # 'Características': caracteristicas,
            # 'Imagem Descrição': imagem_descricao,
            'Usado no Ecommerce': usado,
            'Situação no Ecommerce': situacao,
            'Categoria Vtex': categoria,
            # 'Imagem Principal': imagem_principal,
        }

        if all(valid_flags.values()):
            logging.info('✅ Produto validado')
            return True
        else:
            faltando = [campo for campo, ok in valid_flags.items() if not ok]
            logging.info(f"❌ Produto invalidado — campos faltando/zerados: {', '.join(faltando)}")
            return False

    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Falha ao capturar informacoes de checagem do produto {codprod}", e)
