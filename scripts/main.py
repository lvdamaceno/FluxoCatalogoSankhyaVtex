from sankhya.snk_fetch import sankhya_fetch_products_list, vtex_update_product_info, vtex_update_product_inventory, \
    vtex_update_product_price
from sankhya.vtex_create import vtex_create_product_info, vtex_create_product_price, vtex_create_product_inventory
from vtex.vtex_fetch import fetch_id_vtex, fetch_sku_vtex
from vtex.vtex_sync import vtex_sync_department


def main():
    """
        1. Conferir os departamentos, atualizar se necessário
        2. Pesquisar no Sankhya produto marcados para enviar para o Vtex
        4. Criar uma lista com os produtos
        5. Conferir cada produto se existe no Vtex
        Caso exista
            - Atualizar cadastro do id e do sku
            - Atualizar estoque
            - Atualizar preço de venda
        Caso não exista
            - Criar o cadastro do id e do sku
            - Criar estoque
            - Criar preço de venda
    """
    vtex_sync_department()

    sankhya_products_list = sankhya_fetch_products_list()

    for sankhya_product in sankhya_products_list:
        id_vtex = fetch_id_vtex(sankhya_product)
        sku_vtex = fetch_sku_vtex(sankhya_product)

        if id_vtex:
            vtex_update_product_info(id_vtex, sku_vtex)
            vtex_update_product_inventory(id_vtex, sku_vtex)
            vtex_update_product_price(id_vtex, sku_vtex)

        vtex_create_product_info(id_vtex, sku_vtex)
        vtex_create_product_inventory(id_vtex, sku_vtex)
        vtex_create_product_price(id_vtex, sku_vtex)


if __name__ == '__main__':
    main()