import pytest
from pydantic import ValidationError

from hybrid_rag_api.config import Settings


def test_settings_accept_valid_local_urls() -> None:
    settings = Settings(
        api_port=8000,
        database_url="postgresql+psycopg://rag:local@localhost:5432/rag",
        redis_url="redis://localhost:6379/0",
    )

    assert settings.api_port == 8000


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("api_port", 0),
        ("api_port", 65536),
        ("database_url", "sqlite:///not-postgres.db"),
        ("database_url", "postgresql://missing-database"),
        ("redis_url", "http://localhost:6379"),
    ],
)
def test_settings_reject_invalid_values(field: str, value: object) -> None:
    with pytest.raises(ValidationError):
        Settings(**{field: value})
