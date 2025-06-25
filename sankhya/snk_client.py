import logging
import requests
from requests.adapters import HTTPAdapter
import os
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log, wait_fixed

load_dotenv()

logger = logging.getLogger(__name__)

LOGIN_URL = "https://api.sankhya.com.br/login"
BASE_URL = "https://api.sankhya.com.br/gateway/v1/mge/service.sbr?serviceName="

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
    stop=stop_after_attempt(5),
    wait=wait_fixed(0),
    retry_error_callback=lambda state: None,
    before_sleep=before_sleep_log(logger, logging.INFO)
)
def snk_bearer_token(params=None):
    """Função para fazer login na API do Sankhya."""
    token = os.getenv("SANKHYA_TOKEN")
    app_key = os.getenv("SANKHYA_APPKEY")
    password = os.getenv("SANKHYA_PASSWORD")
    username = os.getenv("SANKHYA_USERNAME")
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'token': token,
        'appkey': app_key,
        'password': password,
        'username': username
    }
    url = f"{LOGIN_URL}"
    response = session.post(url, headers=headers, params=params, timeout=30)
    token = response.json()['bearerToken']
    return token


@retry(
    stop=stop_after_attempt(5),
    wait=wait_fixed(0),
    retry_error_callback=lambda state: None,
    before_sleep=before_sleep_log(logger, logging.INFO)
)
def snk_get(payload, service):
    url = f"{BASE_URL}{service}&outputType=json"
    token = snk_bearer_token()
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    response = session.get(url, headers=headers, json=payload, timeout=30)
    return response.json()


@retry(
    stop=stop_after_attempt(5),
    wait=wait_fixed(0),
    retry=retry_if_exception_type(requests.exceptions.RequestException),
    before_sleep=before_sleep_log(logger, logging.INFO)
)
def snk_post(payload, service):
    url = f"{BASE_URL}{service}&outputType=json"
    token = snk_bearer_token()
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    response = session.post(url, headers=headers, json=payload, timeout=30)
    return response.json()