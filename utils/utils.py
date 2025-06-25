from datetime import datetime
import time


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


def now_iso8601_7():
    # 1) pega a parte de segundos como datetime
    now = datetime.now()
    # 2) pega nanosegundos desde a epoch e isola os nanosegundos desta fração de segundo
    nanosegundos = time.time_ns() % 1_000_000_000
    # 3) converte em unidades de 100 ns (7 dígitos)
    ticks7 = nanosegundos // 100
    # 4) formata string final
    base = now.strftime("%Y-%m-%dT%H:%M:%S")
    return f"{base}.{ticks7:07d}"