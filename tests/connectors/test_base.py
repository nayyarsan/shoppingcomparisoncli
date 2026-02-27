import pytest
from connectors.base import BaseConnector
from models import Product


def test_base_connector_is_abstract():
    with pytest.raises(TypeError):
        BaseConnector()


def test_concrete_connector_must_implement_search():
    class Incomplete(BaseConnector):
        name = "Incomplete"
    with pytest.raises(TypeError):
        Incomplete()
