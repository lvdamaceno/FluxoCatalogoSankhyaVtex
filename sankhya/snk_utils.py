import logging


def extract_department_id(department):
    """
    :param department: String
    :return: extracted department id
    """
    try:
        extract = department[-3:]
        if extract[0] == '0':
            department_id = extract[1:]
        else:
            department_id = extract
        return department_id
    except Exception as e:
        logging.error(f"❌ Erro ao extrair o departmento para {department}: {e}")


def link_id(description, codprod):
    """

    :param description:
    :param codprod:
    :return:
    """
    try:
        lower_description = description.lower()
        dash_description = lower_description.replace(' ', '-')
        remove_pontuation = dash_description.replace('.', '')
        link = f"{remove_pontuation}-{codprod}"
        return link
    except Exception as e:
        logging.error(f"❌ Erro ao gerar o link para {description}: {e}")


def meta_tag_description(description):
    """

    :param description:
    :return:
    """
    try:
        lower_description = description.lower()
        return lower_description
    except Exception as e:
        logging.error(f"❌ Erro ao extrair o meta tag para {description}: {e}")