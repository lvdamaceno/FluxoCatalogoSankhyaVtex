import logging
import time
import requests
from requests.adapters import HTTPAdapter
import os
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, wait_fixed, before_sleep_log

load_dotenv()

logger = logging.getLogger(__name__)

account_name = os.getenv("VTEX_ACCOUNT_NAME")
app_key = os.getenv("VTEX_APP_KEY")
app_token = os.getenv("VTEX_APP_TOKEN")
headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'X-VTEX-API-AppKey': app_key,
    'X-VTEX-API-AppToken': app_token
}

BASE_URL = f"https://{account_name}.vtexcommercestable.com.br/api"

# 1) Session global para manter conexões vivas
session = requests.Session()
adapter = requests.adapters.HTTPAdapter(
    pool_connections=100,
    pool_maxsize=100,
    max_retries=0,
    pool_block=True
)
session.mount("https://", adapter)
session.mount("http://", adapter)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(0),
    retry_error_callback=lambda state: None,
    before_sleep=before_sleep_log(logger, logging.INFO)
)
def vtex_head(path: str) -> int:
    """
    Executa HEAD para verificar existência.
    Retorna status_code ou lança erro.
    """
    url = f"{BASE_URL}/{path}"
    resp = session.head(url, headers=headers, timeout=5)
    logging.info(f"📊 HEAD {resp.status_code}")
    try:
        if resp.status_code == 200:
            return True
        else:
            resp.raise_for_status()
            return False
    except requests.exceptions.RequestException:
        logger.error(f"HEAD request failed with status code {resp.status_code}")


@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(0),
    retry_error_callback=lambda state: None,
    before_sleep=before_sleep_log(logger, logging.INFO)
)
def vtex_get(path, params=None):
    """Função genérica para requisições GET na VTEX."""
    url = f"{BASE_URL}/{path}"
    time.sleep(1)
    response = session.get(url, headers=headers, params=params, timeout=5)
    response.raise_for_status()
    return response.json()


@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(0),
    retry_error_callback=lambda state: None,
    before_sleep=before_sleep_log(logger, logging.INFO)
)
def vtex_post(path, payload):
    """Função genérica para requisições POST na VTEX."""
    url = f"{BASE_URL}/{path}"
    time.sleep(1)
    response = session.post(url, headers=headers, json=payload, timeout=5)
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        logging.error(f"❌ Erro: {e}")
        logging.error(f"VTEX retornou {response.status_code}: {response.text}")
        raise
    return response.json()


@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(0),
    retry_error_callback=lambda state: None,
    before_sleep=before_sleep_log(logger, logging.INFO)
)
def vtex_put(path, payload):
    """Função genérica para requisições PUT na VTEX."""
    url = f"{BASE_URL}/{path}"
    time.sleep(1)
    response = session.put(url, headers=headers, json=payload, timeout=5)
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        logging.error(f"❌ Erro: {e}")
        logging.error(f"❌ VTEX retornou {response.status_code}: {response.text}")
        raise
    return response.json()
