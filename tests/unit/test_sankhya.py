import requests

from sankhya.snk_client import snk_bearer_token


def test_mock_token(monkeypatch):
    # Mocking test
    class FakeResp:
        def json(self): return {'bearerToken':'XYZ'}
    monkeypatch.setattr(requests, 'post', lambda *args, **kwargs: FakeResp())
    assert snk_bearer_token() == 'XYZ'
