import requests
import os
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

load_dotenv()

LOGIN_URL = "https://api.sankhya.com.br/login"
BASE_URL = "https://api.sankhya.com.br/gateway/v1/mge/service.sbr?serviceName="


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(requests.exceptions.RequestException)
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
    response = requests.post(url, headers=headers, params=params, timeout=30)
    token = response.json()['bearerToken']
    return token


def snk_get(payload, service):
    url = f"{BASE_URL}{service}&outputType=json"
    token = snk_bearer_token()
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    response = requests.get(url, headers=headers, json=payload, timeout=30)
    return response.json()