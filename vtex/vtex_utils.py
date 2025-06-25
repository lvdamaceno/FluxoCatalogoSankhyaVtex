import logging

from vtex.vtex_client import vtex_head


def sankhya_product_exist_no_vtex(codprod):
    """
        Retorna True se HEAD retornar 200, False se 404 ou erro.
        """
    service = f"catalog_system/pvt/products/productgetbyrefid/{codprod}"
    try:
        if vtex_head(service):
            logging.warning(f"⚠️ Produto {codprod} existe no Vtex")
            return True
        else:
            logging.warning(f"⚠️ Produto não {codprod} existe no Vtex")
            return False
    except Exception as e:
        logging.error(f"❌ Erro ao checar produto {codprod}: {e}")
        return False