import logging
import time
import requests
import os
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

load_dotenv()

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

LOGIN_URL = "https://api.sankhya.com.br/login"
# BASE_URL = f"https://{account_name}.vtexcommercestable.com.br/api"


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(requests.exceptions.RequestException)
)
def snk_bearer_token(params=None):
    """Função genérica para requisições GET na VTEX."""
    url = f"{LOGIN_URL}"
    response = requests.post(url, headers=headers, params=params, timeout=5)
    print(response.status_code)
    response.raise_for_status()
    logging.info(f"{response.json().get('bearerToken')}")
    return response.json()


def snk_get():
    pass