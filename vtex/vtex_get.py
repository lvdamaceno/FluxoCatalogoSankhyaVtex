from vtex.vtex_client import vtex_get


def get_vtex_category_tree():
    """Obtém a árvore completa de categorias (nível 2) da VTEX."""
    return vtex_get("catalog_system/pub/category/tree/2")