import logging

from sankhya.snk_check import check_sankhya_ecommerce_infos
from vtex.vtex_create import vtex_create_product, vtex_create_sku, vtex_create_sku_file
from vtex.vtex_fetch import vtex_exist_sku_id
from vtex.vtex_utils import sankhya_product_exist_no_vtex
from vtex.vtex_update import vtex_update_sku, vtex_update_basic_info, \
    vtex_update_specifications

logging.basicConfig(
    level=logging.INFO,  # Define o nível mínimo de log que será exibido
    format='[%(asctime)s] [%(levelname)s] [%(filename)s] %(message)s',
    datefmt='%d-%m/%H:%M'
)


def vtex_process_new_product(codprod):
    vtex_create_product(codprod)

    vtex_update_basic_info(codprod)
    vtex_update_specifications(codprod)

    vtex_create_sku(codprod)
    vtex_create_sku_file(codprod)


def vtex_process_update_product(codprod):
    vtex_update_basic_info(codprod)
    vtex_update_specifications(codprod)

    if vtex_exist_sku_id(codprod):
        vtex_update_sku(codprod)
    else:
        vtex_create_sku(codprod)
    # vtex_update_sku_file(codprod)
    vtex_create_sku_file(codprod)


def vtex_process_product(codprod):
    if check_sankhya_ecommerce_infos(codprod):
        # 🟢 Product ready on sankhya
        if sankhya_product_exist_no_vtex(codprod):
            # 🟢 Product exist on vtex
            vtex_process_update_product(codprod)
        else:
            # 🔴 Product dont exist on vtex
            vtex_process_new_product(codprod)
    else:
        logging.info("Revalide os campos obrigatórios do cadastro do produto")


if __name__ == '__main__':
    # Reativar e testar
    # sync_vtex_departments()

    vtex_process_product(417568)
