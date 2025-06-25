import logging

from vtex.vtex_create import vtex_create_product, vtex_create_sku, vtex_create_sku_file
from vtex.vtex_utils import sankhya_product_exist_no_vtex
from vtex.vtex_update import vtex_update_product, vtex_update_sku, vtex_update_sku_file

logging.basicConfig(
    level=logging.INFO,  # Define o nível mínimo de log que será exibido
    format='[%(asctime)s] [%(levelname)s] [%(filename)s] \n %(message)s',
    datefmt='%d-%m/%H:%M'
)

def main():
    """
    Orquestra a sincronização Sankhya ↔ VTEX.
    442008,442268,438737,422948,423304,436935,439881,439882,441855,420909,442082,440445,441624,423304,428945,431123,
    432580,436290,442068,442069
    """
    codprod = 438737
    try:
        # Reativar e testar
        # sync_vtex_departments()

        if sankhya_product_exist_no_vtex(codprod):
            #🟢 if product exist on vtex
            vtex_update_product(codprod)
            vtex_update_sku(codprod)
            vtex_update_sku_file(codprod)
        else:
            #🔴 if product dont exist on vtex
            vtex_create_product(codprod)
            vtex_update_product(codprod)
            vtex_create_sku(codprod)
            vtex_create_sku_file(codprod)
    except Exception as e:
        logging.error(f"❌ Erro no módulo main: {e}")

if __name__ == '__main__':
    main()