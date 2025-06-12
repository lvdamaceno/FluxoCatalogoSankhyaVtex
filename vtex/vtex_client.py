import time
import requests
import os
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

load_dotenv()

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

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(requests.exceptions.RequestException)
)
def vtex_get(path, params=None):
    """Função genérica para requisições GET na VTEX."""
    url = f"{BASE_URL}/{path}"
    time.sleep(1)
    response = requests.get(url, headers=headers, params=params, timeout=5)
    response.raise_for_status()
    return response.json()