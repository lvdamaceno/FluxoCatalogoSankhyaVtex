import os
import pytest
from dotenv import load_dotenv, dotenv_values
from pathlib import Path

load_dotenv()

def test_all_env_vars_are_tested():
    env_path = Path(__file__).resolve().parent.parent / ".env"
    actual_vars = dotenv_values(dotenv_path=env_path)

    tested_vars = {
        "SANKHYA_TOKEN", "SANKHYA_APPKEY", "SANKHYA_USERNAME", "SANKHYA_PASSWORD",
        "VTEX_APP_KEY", "VTEX_APP_TOKEN", "VTEX_BASE_URL", "VTEX_ACCOUNT_NAME",
        "BOTTOKEN", "CHATID", "APP_ENV"
    }

    all_env_keys = set(actual_vars.keys())
    not_covered = all_env_keys - tested_vars

    assert not not_covered, f"As seguintes variáveis estão no .env mas não foram cobertas nos testes: {not_covered}"

@pytest.mark.parametrize("env_var", [
    "SANKHYA_TOKEN",
    "SANKHYA_APPKEY",
    "SANKHYA_USERNAME",
    "SANKHYA_PASSWORD",
    "VTEX_APP_KEY",
    "VTEX_APP_TOKEN",
    "VTEX_BASE_URL",
    "VTEX_ACCOUNT_NAME",
    "BOTTOKEN",
    "CHATID",
    "APP_ENV"
])

def test_env_var_is_set(env_var):
    """
    Usando @pytest.mark.parametrize faz com que o pytest crie um teste separado por variável, facilitando o diagnóstico se uma delas falhar.
    :param env_var:
    :return:
    """
    assert os.getenv(env_var) is not None, f"{env_var} não está definida no .env"
