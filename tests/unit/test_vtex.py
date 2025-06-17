from unittest.mock import patch

from vtex.vtex_fetch import sankhya_product_exist_no_vtex


def test_sankhya_product_exist_no_vtex():
    assert sankhya_product_exist_no_vtex(427051) == True
    assert sankhya_product_exist_no_vtex(1) == False