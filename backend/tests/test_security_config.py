"""Regression tests for PhantomLink security configuration."""

import pytest

from app.services.security_config import (
    SecurityConfigurationError,
    get_cookie_security_config,
)


@pytest.mark.parametrize(
    "environment,secure_setting,expected",
    [
        ("development", "false", False),
        ("development", "true", True),
        ("test", "false", False),
        ("production", "true", True),
    ],
)
def test_valid_security_configuration(
    environment, secure_setting, expected
):
    config = get_cookie_security_config(
        environment=environment,
        secure_setting=secure_setting,
    )

    assert config["cookie_secure"] is expected
    assert config["cookie_httponly"] is True
    assert config["cookie_samesite"] == "lax"
    assert config["cookie_path"] == "/"


@pytest.mark.parametrize(
    "environment,secure_setting",
    [
        ("production", "false"),
        ("production", "invalid"),
    ],
)
def test_unsafe_production_configuration_rejected(
    environment, secure_setting
):
    with pytest.raises(SecurityConfigurationError):
        get_cookie_security_config(
            environment=environment,
            secure_setting=secure_setting,
        )
