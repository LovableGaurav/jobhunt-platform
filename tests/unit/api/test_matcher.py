from apps.api.core.config import get_settings


def test_match_score_threshold_default():
    get_settings.cache_clear()
    settings = get_settings()
    assert settings.match_score_threshold == 0.7
    assert settings.embedding_dimensions == 1536
