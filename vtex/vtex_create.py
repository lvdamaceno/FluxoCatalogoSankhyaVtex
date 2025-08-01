import json
import logging

from sankhya.snk_fetch import fetch_sankhya_basic_info, fetch_sankhya_sku_info, fetch_sankhya_sku_file_info
from vtex.vtex_client import vtex_post
from vtex.vtex_fetch import fetch_vtex_id, vtex_exist_sku_id, fetch_vtex_sku_id


def vtex_create_product(codprod):
    logging.info(f"🟢 Criando produto {codprod}")
    try:
        basic_info = fetch_sankhya_basic_info(codprod)
        payload = {
            "Name": basic_info["Name"],  # ajuste nomes
            "CategoryId": basic_info["CategoryId"],  # ou CategoryPath
            "BrandName": basic_info["BrandName"],
            "RefId": basic_info["RefId"],
            "Title": basic_info["Title"],
            "LinkId": basic_info["LinkId"],
            "Description": basic_info["Description"],
            "ReleaseDate": basic_info["ReleaseDate"],  # ISO 8601
            "IsVisible": True,
            "IsActive": True,
            "MetaTagDescription": basic_info["MetaTagDescription"],
            "ShowWithoutStock": True,
            "Score": basic_info.get("score", 1)
        }
        service = 'catalog/pvt/product'
        logging.info(f"🚀 Enviando cadastro do produto {codprod}")
        vtex_post(service, payload)
    except Exception as e:
        logging.error(f"❌ Erro ao enviar cadastro do produto {codprod}: {e}")


def vtex_create_sku(codprod):
    logging.info(f"🟢 Criando SKU {codprod}")
    try:
        vtex_id = fetch_vtex_id(codprod)
        sku_info = fetch_sankhya_sku_info(codprod)
        logging.info(f"🟢 Id: {codprod}")
        payload = {
            "ProductId": vtex_id,
            "IsActive": False,
            "ActivateIfPossible": True,
            "Name": sku_info['Name'],
            "RefId": sku_info['RefId'],
            "PackagedHeight": sku_info['PackagedHeight'],
            "PackagedLength": sku_info['PackagedLength'],
            "PackagedWidth": sku_info['PackagedWidth'],
            "PackagedWeightKg": sku_info['PackagedWeightKg'],
            "Height": sku_info['Height'],
            "Length": sku_info['Length'],
            "Width": sku_info['Width'],
            "WeightKg": sku_info['WeightKg'],
            "CubicWeight": sku_info['CubicWeight'],
            "IsKit": False,
            "CreationDate": sku_info['CreationDate'],
            "RewardValue": 1,
            "ManufacturerCode": sku_info['ManufacturerCode'],
            "CommercialConditionId": 1,
            "MeasurementUnit": sku_info['MeasurementUnit'],
            "UnitMultiplier": 2,
        }
        logging.info(f"📊 Payload create sku: {json.dumps(payload, indent=4)}")

        path = 'catalog/pvt/stockkeepingunit'
        vtex_post(path, payload)

    except Exception as e:
        logging.error(f"❌ Erro ao criar Sku para o produto {codprod}: {e}")


def vtex_create_sku_file(codprod):
    logging.info(f"🟢 Criando sku file para o produto {codprod}")
    try:
        vtex_id = fetch_vtex_id(codprod)
        sku_id = fetch_vtex_sku_id(vtex_id)
        logging.info(f"🟢 Id: {codprod}, SkuID: {sku_id}")
        sku_file_info = fetch_sankhya_sku_file_info(codprod)

        path = f"catalog/pvt/stockkeepingunit/{sku_id}/file"
        payload = {
            "IsMain": True,
            "Label": "Main",
            "Name": sku_file_info['Name'],
            "Text": sku_file_info['Name'],
            "Url": sku_file_info['Url'],
            "Position": 0
        }
        logging.info(f"📊 Payload create sku file: {json.dumps(payload, indent=4)}")

        vtex_post(path, payload)

    except Exception as e:
        logging.error(f"❌ Erro ao criar Sku File para o produto {codprod}: {e}")
