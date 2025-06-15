def fill_with_zeros(number=None):
    """
    Função criada para preencher os números com 3 zeros para bater com o nível de hierarquia do Sankhya
        1 retorna 001
        11 retorna 011
        111 retorna 111
        Nada retonar 000
    :param number:
    :return:
    """
    if number is None:
        return '000'
    return str(number).zfill(3)