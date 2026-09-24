from src.llm.source_url_recommender import OpenAISourceURLRecommender


def test_source_url_recommender_prompt_is_fixed_and_organisation_preserving() -> None:
    prompt = OpenAISourceURLRecommender._build_prompt([{"Organisation": "NUS", "Source URL": "https://news.nus.edu.sg"}])
    assert "Do not change organisations" in prompt
    assert "Do not invent URLs" in prompt
    assert "https://news.nus.edu.sg" in prompt
