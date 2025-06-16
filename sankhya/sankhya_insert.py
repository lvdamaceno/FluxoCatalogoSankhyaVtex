import logging

from sankhya.snk_client import snk_post


def insert_sankhya_departaments(diff):
    service = "DatasetSP.save"
    try:
        for row in diff.itertuples(index=False, name='Linha'):
            ID_CATEGORIA = row[0]
            GRAU = row[1]
            ANALITICO = row[2]
            ID_CATEGORIAPAI = row[3]
            NOME = row[4]

            payload = {
                "serviceName": "br.com.sankhya.menu.adicional.AD_ADVTEXCATEGORIAS",
                "requestBody": {
                    "entityName": "AD_ADVTEXCATEGORIAS",
                    "standAlone": False,
                    "fields": [
                        "ID_CATEGORIA",
                        "GRAU",
                        "ANALITICO",
                        "ID_CATEGORIAPAI",
                        "NOME"
                    ],
                    "records": [
                        {
                            "values": {
                                "0": f"{ID_CATEGORIA}",
                                "1": f"{GRAU}",
                                "2": f"{ANALITICO}",
                                "3": f"{ID_CATEGORIAPAI}",
                                "4": f"{NOME}"
                            }
                        }
                    ]
                }
            }
            snk_post(payload, service)
            logging.info(f"Departamento: {NOME} salvo no Sankhya")
    except Exception as e:
        logging.error(f"Erro ao enviar departamento para o sankhya: {e}")