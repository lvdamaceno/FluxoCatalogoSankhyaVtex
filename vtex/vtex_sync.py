import logging

from sankhya.sankhya_insert import insert_sankhya_departaments
from sankhya.snk_fetch import fetch_sankhya_departaments
from vtex.vtex_fetch import fetch_vtex_departaments


def diff_departaments(df1, df2, name1, name2):
    try:
        merged = df1.merge(df2, how='left', indicator=True)
        diff = merged[merged['_merge'] == 'left_only'].drop(columns=['_merge'])
        if len(diff) > 0:
            logging.info(f"📊 Valores que existe no {name1} e não existe no {name2}")
            logging.info(diff)
            return diff
        else:
            logging.info(f"📊 Não há valores diferentes")
    except Exception as e:
        logging.error(f"❌ Erro ao comparar departamentos {e}")


def sync_vtex_departments():
    vtexdf = fetch_vtex_departaments()
    sankhyadf = fetch_sankhya_departaments()

    # Departamentos que existem no vtex e não existem no sankhya
    diff_sankhya = diff_departaments(vtexdf, sankhyadf, 'Vtex', 'Sankhya')

    insert_sankhya_departaments(diff_sankhya)
