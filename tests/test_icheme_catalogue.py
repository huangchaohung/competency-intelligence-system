import json
from unittest.mock import Mock
import pytest
from src.scanner import icheme_catalogue as module
from src.models.domain import Source
from src.core.exceptions import ScanError


def test_api_discovery_bounds_and_filters(monkeypatch):
    response = Mock(status_code=200)
    response.__enter__ = Mock(return_value=response)
    response.__exit__ = Mock(return_value=False)
    response.iter_content.return_value = [json.dumps({'Courses':[
        {'Url':'/training-events/training/courses-a-z/process-safety/'},
        {'Url':'/training-events/training/courses-a-z/process-safety/#top'},
        {'Url':'https://other.example/course'}, {'Url':'/login'}], 'TotalPageCount':1}).encode()]
    get = Mock(return_value=response)
    monkeypatch.setattr(module.requests, 'get', get)
    scanner = Mock(); scanner.is_allowed.return_value = True
    source = Source(1,'IChemE',module.ROOT,'IChemE',max_listing_pages=5)
    assert module.discover(source,scanner) == [module.ROOT+'/process-safety/']
    assert get.call_count == 1 and get.call_args.kwargs['allow_redirects'] is False
    scanner.is_allowed.return_value = False
    with pytest.raises(ScanError,match='not permitted'):
        module.discover(source,scanner)
    assert get.call_count == 1
