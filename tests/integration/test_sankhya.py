import pytest

from sankhya.snk_client import snk_bearer_token

pytestmark = pytest.mark.integration

def test_snk_bearer_token():
    token = snk_bearer_token()
    assert isinstance(token, str), "Token não é string"
    assert token.strip(), "Token está vazio"
    parts = token.split('.')
    assert len(parts) == 3, "Token não parece um JWT"