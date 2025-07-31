import logging

from sankhya.snk_fetch import fetch_sankhya_grupo_informacoes_vtex, fetch_sankhya_basic_info, fetch_sankhya_sku_info, \
    fetch_sankhya_sku_file_info
from vtex.vtex_client import vtex_put, vtex_post
from vtex.vtex_create import vtex_create_sku_file
from vtex.vtex_fetch import fetch_vtex_id, vtex_exist_sku_id, fetch_vtex_sku_id, fetch_vtex_sku_file_id


def vtex_update_basic_info(codprod, vtex_id):
    basic_info = fetch_sankhya_basic_info(codprod)
    logging.info(f"🚀 Enviando atualização do cadastro do produto {codprod}, id: {vtex_id}")
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
    service = f'catalog/pvt/product/{vtex_id}'
    vtex_put(service, payload)


def vtex_update_specifications(codprod, vtex_id):
    sankhya_product_info = fetch_sankhya_grupo_informacoes_vtex(codprod)
    logging.info(f"🚀 Enviando atualização do grupo de informações do produto {codprod}, id: {vtex_id}")

    payload = [
        {
            "Value": [f"{sankhya_product_info['Descrição']}"],
            "Id": 20,
            "Name": "Descrição"
        },
        {
            "Value": [f"{sankhya_product_info['Diferenciais']}"],
            "Id": 21,
            "Name": "Diferenciais"
        },
        {
            "Value": [f"{sankhya_product_info['Características']}"],
            "Id": 22,
            "Name": "Características"
        },
        {
            "Value": [f"{sankhya_product_info['Download']}"],
            "Id": 23,
            "Name": "Download  de materiais"
        },
        {
            "Value": [f"{sankhya_product_info['Imagem']}"],
            "Id": 24,
            "Name": "Imagem da descrição"
        }
    ]
    path = f"catalog_system/pvt/products/{vtex_id}/specification"
    vtex_post(path, payload)


def vtex_update_product(codprod):
    logging.info(f"🚀 Atualizando produto {codprod}")
    try:
        vtex_id = fetch_vtex_id(codprod)
        vtex_update_basic_info(codprod, vtex_id)
        vtex_update_specifications(codprod, vtex_id)

    except Exception as e:
        logging.error(f"❌ Erro ao atualizar produto {codprod}: {e}")


def vtex_update_sku(codprod):
    logging.info(f"⚠️ Exist Sku ID: {vtex_exist_sku_id(codprod)}")

    vtex_id = fetch_vtex_id(codprod)
    sku_id = fetch_vtex_sku_id(vtex_id)

    try:
        logging.info(f"🟢 Atualizando sku para o produto {codprod}, id {vtex_id}, sku {sku_id}")
        sku_info = fetch_sankhya_sku_info(codprod)
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
        path = f"catalog/pvt/stockkeepingunit/{sku_id}"
        vtex_put(path, payload)
    except Exception as e:
        logging.error(f" ❌Erro ao atualizar SKU para o produto {codprod}: {e}")


def vtex_update_sku_file(codprod):
    try:
        vtex_id = fetch_vtex_id(codprod)
        sku_id = fetch_vtex_sku_id(vtex_id)

        sku_file_id = fetch_vtex_sku_file_id(codprod)
        path = f"catalog/pvt/stockkeepingunit/{sku_id}/file/{sku_file_id}"

        logging.info(f"🟢 Atualizando sku file para o produto {codprod}, id {vtex_id}, sku {sku_id}")
        sku_file_info = fetch_sankhya_sku_file_info(codprod)
        payload = {
            "IsMain": True,
            "Label": "Main",
            "Name": sku_file_info['Name'],
            "Text": sku_file_info['Name'],
            "Url": sku_file_info['Url'],
            "Position": 0
        }
        vtex_put(path, payload)

    except Exception as e:
        logging.error(f"❌ Erro ao criar Sku File para o produto {codprod}: {e}")
