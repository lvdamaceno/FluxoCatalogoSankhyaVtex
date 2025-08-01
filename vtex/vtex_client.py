import json
import logging
import requests
from requests.adapters import HTTPAdapter
import os
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, before_sleep_log, wait_exponential

load_dotenv()

logger = logging.getLogger(__name__)

account_name = os.getenv("VTEX_ACCOUNT_NAME")
app_key = os.getenv("VTEX_APP_KEY")
app_token = os.getenv("VTEX_APP_TOKEN")
headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    # controle de cache
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
    'X-VTEX-API-AppKey': app_key,
    'X-VTEX-API-AppToken': app_token
}

assert account_name, "VTEX_ACCOUNT_NAME não definido"
assert app_key, "VTEX_APP_KEY não definido"
assert app_token, "VTEX_APP_TOKEN não definido"

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
    stop=stop_after_attempt(10),
    wait=wait_exponential(multiplier=1, max=30),
    retry_error_callback=lambda state: None,
    before_sleep=before_sleep_log(logger, logging.INFO)
)
def vtex_head(path):
    try:
        url = f"{BASE_URL}/{path}"
        resp = session.head(url, headers=headers, timeout=30)
        logging.info(f"📊 HEAD {resp.status_code}")
        if resp.status_code == 200:
            return True
        else:
            resp.raise_for_status()
            return False
    except requests.exceptions.RequestException:
        logger.error(f"HEAD request failed with status code {resp.status_code}")



@retry(
    stop=stop_after_attempt(10),
    wait=wait_exponential(multiplier=1, max=30),
    retry_error_callback=lambda state: None,
    before_sleep=before_sleep_log(logger, logging.INFO)
)
def vtex_get(path, params=None):
    """Função genérica para requisições GET na VTEX."""
    try:
        url = f"{BASE_URL}/{path}"
        logging.info(f"🔗 GET url {url}")
        response = session.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
    except requests.HTTPError as e:
        logging.error(f"❌ Erro: {e}")
        logging.error(f"VTEX retornou no get {response.status_code}: {response.text}")
        raise requests.HTTPError(
            f"Erro ao chamar VTEX API [{response.status_code}]: {response.text}"
        ) from e
    return response.json()


@retry(
    stop=stop_after_attempt(10),
    wait=wait_exponential(multiplier=1, max=30),
    retry_error_callback=lambda state: None,
    before_sleep=before_sleep_log(logger, logging.INFO)
)
def vtex_post(path, payload):
    """Função genérica para requisições POST na VTEX."""
    try:
        url = f"{BASE_URL}/{path}"
        logging.info(f"🔗 POST url {url}")
        response = session.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
    except requests.HTTPError as e:
        logging.error(f"❌ Erro: {e}")
        logging.error(f"VTEX retornou no post {response.status_code}: {response.text}")
        logging.error(f"🔍 Payload enviado: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        raise requests.HTTPError(
            f"Erro ao chamar VTEX API [{response.status_code}]: {response.text}"
        ) from e
    return response.json()


@retry(
    stop=stop_after_attempt(10),
    wait=wait_exponential(multiplier=1, max=30),
    retry_error_callback=lambda state: None,
    before_sleep=before_sleep_log(logger, logging.INFO)
)
def vtex_put(path, payload):
    """Função genérica para requisições PUT na VTEX."""
    try:
        url = f"{BASE_URL}/{path}"
        logging.info(f"🔗 PUT url {url}")
        response = session.put(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
    except requests.HTTPError as e:
        logging.error(f"❌ Erro: {e}")
        logging.error(f"❌ VTEX retornou no put {response.status_code}: {response.text}")
        logging.error(f"🔍 Payload enviado: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        raise requests.HTTPError(
            f"Erro ao chamar VTEX API [{response.status_code}]: {response.text}"
        ) from e
    return response.json()
