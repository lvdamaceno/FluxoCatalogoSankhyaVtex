import pytest
from vtex.vtex_client import vtex_get

def test_vtex_get_funciona():
    resultado = vtex_get("catalog_system/pub/category/tree/2")
    assert isinstance(resultado, list), "Resposta não é uma lista"
    assert len(resultado) > 0, "Lista de marcas veio vazia"
