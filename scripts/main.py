import logging
from sankhya.snk_fetch import fetch_sankhya_products
from vtex.vtex_fetch import sankhya_product_exist_no_vtex

logging.basicConfig(
    level=logging.INFO,  # Define o nível mínimo de log que será exibido
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    """Orquestra a sincronização Sankhya ↔ VTEX."""
    # sync_vtex_departments()

    sankhya_products_list = fetch_sankhya_products()
    for product in sankhya_products_list:
        print(product, sankhya_product_exist_no_vtex(product))




if __name__ == '__main__':
    main()