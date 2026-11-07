import pytest
from fastapi import HTTPException

from hybrid_rag_api import main


def test_liveness_does_not_depend_on_database() -> None:
    assert main.live() == {"status": "live"}


def test_readiness_reports_database_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    class UnavailableEngine:
        def connect(self):
            raise main.SQLAlchemyError("database unavailable")

    monkeypatch.setattr(main, "engine", UnavailableEngine())

    with pytest.raises(HTTPException) as error:
        main.ready()

    assert error.value.status_code == 503
    assert error.value.detail == {"status": "not_ready", "database": "unavailable"}
