import pytest

from src.core.exceptions import RecommendationError
from src.services.source_url_recommendation import parse_replacement_url_response


def test_replacement_url_response_preserves_organisation_and_https_urls() -> None:
    result = parse_replacement_url_response(
        '{"organisation":"NUS","recommendations":[{"url":"https://news.nus.edu.sg/research","reason":"Official research news hub"}]}',
        "NUS",
    )
    assert result["organisation"] == "NUS"
    assert result["recommendations"][0]["url"].startswith("https://")


def test_replacement_url_response_rejects_cross_organisation_or_invalid_url() -> None:
    with pytest.raises(RecommendationError, match="changed the organisation"):
        parse_replacement_url_response('{"organisation":"Other","recommendations":[]}', "NUS")
    with pytest.raises(RecommendationError, match="valid HTTPS URL"):
        parse_replacement_url_response('{"organisation":"NUS","recommendations":[{"url":"javascript:bad","reason":"x"}]}', "NUS")
