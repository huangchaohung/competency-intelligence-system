import sqlite3
import pytest

from src.core.database import initialise
from src.repositories.source_url_recommendation_repository import SourceURLRecommendationRepository


def test_source_url_recommendation_repository_allows_only_one_result_per_batch(tmp_path) -> None:
    connection = sqlite3.connect(tmp_path / "test.db")
    connection.row_factory = sqlite3.Row
    initialise(connection)
    repository = SourceURLRecommendationRepository(connection)
    row = repository.add(3, 7, "COMPLETED", [{"Organisation": "NUS"}], {"recommendations": []})
    assert row["recommendation_batch_id"] == 7
    assert repository.get_for_batch(7)["status"] == "COMPLETED"
    with pytest.raises(ValueError, match="already exists"):
        repository.add(3, 7, "COMPLETED", [], {})
