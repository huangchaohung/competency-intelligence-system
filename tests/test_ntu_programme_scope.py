from types import SimpleNamespace
import pytest
from src.models.domain import Source
from src.scanner.source_router import SourceRouter
from src.core.exceptions import ScanError


def test_robotics_programme_does_not_follow_global_menus():
    url = 'https://www.ntu.edu.sg/engineering/coe-programmes/graduate/coe-programme-detail/master-of-science-%28robotics-and-intelligent-systems%29'
    source = Source(1,'NTU Robotics',url,'NTU')
    assert SourceRouter(SimpleNamespace(is_allowed=lambda u: True)).discover(source) == [url]
    with pytest.raises(ScanError,match='not permitted'):
        SourceRouter(SimpleNamespace(is_allowed=lambda u: False)).discover(source)
