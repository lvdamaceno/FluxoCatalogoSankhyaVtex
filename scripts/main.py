import logging
from sankhya.snk_fetch import fetch_sankhya_products
from vtex.vtex_create import create_vtex_product
from vtex.vtex_fetch import get_vtex_id, get_vtex_sku
from vtex.vtex_sync import sync_vtex_departments
from vtex.vtex_update import update_vtex_product

logging.basicConfig(
    level=logging.INFO,  # Define o nível mínimo de log que será exibido
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    """Orquestra a sincronização Sankhya ↔ VTEX."""
    try:
        sync_vtex_departments()

        sankhya_products_list = fetch_sankhya_products()

        for sankhya_product in sankhya_products_list:
            id_vtex = get_vtex_id(sankhya_product)
            sku_vtex = get_vtex_sku(sankhya_product)

            if id_vtex:
                update_vtex_product(id_vtex, sku_vtex)
            else:
                create_vtex_product(id_vtex, sku_vtex)
    except Exception as e:
        logging.error(f"Erro na funcao Main: {e}")


if __name__ == '__main__':
    main()