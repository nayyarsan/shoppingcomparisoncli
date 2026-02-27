import os
import importlib


def test_config_loads_keys_from_env(monkeypatch):
    monkeypatch.setenv("BESTBUY_API_KEY", "bb-test-key")
    monkeypatch.setenv("SERPAPI_API_KEY", "serp-test-key")
    import config
    importlib.reload(config)
    assert config.BESTBUY_API_KEY == "bb-test-key"
    assert config.SERPAPI_API_KEY == "serp-test-key"


def test_config_defaults_to_empty_string(monkeypatch):
    monkeypatch.delenv("GOUPC_API_KEY", raising=False)
    import config
    importlib.reload(config)
    assert config.GOUPC_API_KEY == ""
