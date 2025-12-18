import pytest

from app.config import Settings, SettingsValidationError


def test_cors_origins_parsing():
    settings = Settings(cors_origins="https://a.example, http://localhost:3000")
    assert settings.cors_origins == ["https://a.example", "http://localhost:3000"]


def test_validate_runtime_production_requires_secret_key():
    settings = Settings(environment="production", debug=False, secret_key="change-this-in-production")
    with pytest.raises(SettingsValidationError):
        settings.validate_runtime()
