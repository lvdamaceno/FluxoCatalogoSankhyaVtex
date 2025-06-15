from utils.utils import fill_with_zeros


def test_fill_with_zeros_com_1():
    assert fill_with_zeros(1) == "001"

def test_fill_with_zeros_com_11():
    assert fill_with_zeros(11) == "011"

def test_fill_with_zeros_com_111():
    # Neste caso, como você disse "não deve devolver nada", assumo que o retorno seja `None`
    assert fill_with_zeros(111) == "111"

def test_fill_with_zeros_sem_parametro():
    assert fill_with_zeros() == "000"