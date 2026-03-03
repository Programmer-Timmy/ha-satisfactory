"""Test the Satisfactory config flow."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.satisfactory.config_flow import (
    CannotConnectError,
    InvalidAuthError,
    SatisfactoryConfigFlow,
    validate_input,
)
from custom_components.satisfactory.const import CONF_SKIP_SSL, DEFAULT_PORT

TEST_INPUT = {
    "host": "1.1.1.1",
    "port": DEFAULT_PORT,
    "password": "test-password",
    CONF_SKIP_SSL: True,
}


@pytest.fixture
def mock_hass() -> MagicMock:
    """Return a mock HomeAssistant instance."""
    hass = MagicMock()
    hass.config_entries = MagicMock()
    return hass


@pytest.fixture
def flow(mock_hass: MagicMock) -> SatisfactoryConfigFlow:
    """Return a SatisfactoryConfigFlow instance with a mock hass."""
    f = SatisfactoryConfigFlow()
    f.hass = mock_hass
    f.context = {"source": "user"}
    f._async_set_unique_id = AsyncMock()  # noqa: SLF001
    f._abort_if_unique_id_configured = MagicMock()  # noqa: SLF001
    f.async_create_entry = MagicMock(
        return_value={"type": "create_entry", "title": "", "data": {}}
    )
    f.async_show_form = MagicMock(return_value={"type": "form", "errors": {}})
    return f


@pytest.mark.asyncio
async def test_validate_input_success() -> None:
    """Test validate_input returns title on successful login."""
    mock_client = AsyncMock()
    with patch(
        "custom_components.satisfactory.config_flow.AsyncSatisfactoryAPI",
        return_value=mock_client,
    ):
        result = await validate_input(MagicMock(), TEST_INPUT)

    assert result == {
        "title": f"Satisfactory ({TEST_INPUT['host']}:{TEST_INPUT['port']})"
    }
    mock_client.password_login.assert_awaited_once()


@pytest.mark.asyncio
async def test_validate_input_invalid_auth() -> None:
    """Test validate_input raises InvalidAuthError on APIError."""
    from satisfactory_api_client import APIError  # noqa: PLC0415

    mock_client = AsyncMock()
    mock_client.password_login.side_effect = APIError("AUTH_FAILED", "auth failed")
    with (
        patch(
            "custom_components.satisfactory.config_flow.AsyncSatisfactoryAPI",
            return_value=mock_client,
        ),
        pytest.raises(InvalidAuthError),
    ):
        await validate_input(MagicMock(), TEST_INPUT)


@pytest.mark.asyncio
async def test_validate_input_cannot_connect() -> None:
    """Test validate_input raises CannotConnectError on generic exception."""
    mock_client = AsyncMock()
    mock_client.password_login.side_effect = ConnectionError("timeout")
    with (
        patch(
            "custom_components.satisfactory.config_flow.AsyncSatisfactoryAPI",
            return_value=mock_client,
        ),
        pytest.raises(CannotConnectError),
    ):
        await validate_input(MagicMock(), TEST_INPUT)


@pytest.mark.asyncio
async def test_step_user_shows_form(flow: SatisfactoryConfigFlow) -> None:
    """Test that step_user with no input shows a form."""
    await flow.async_step_user(None)
    flow.async_show_form.assert_called_once()


@pytest.mark.asyncio
async def test_step_user_success(flow: SatisfactoryConfigFlow) -> None:
    """Test step_user creates entry on successful validate_input."""
    with patch(
        "custom_components.satisfactory.config_flow.validate_input",
        return_value={
            "title": f"Satisfactory ({TEST_INPUT['host']}:{TEST_INPUT['port']})"
        },
    ):
        await flow.async_step_user(TEST_INPUT)

    flow.async_create_entry.assert_called_once_with(
        title=f"Satisfactory ({TEST_INPUT['host']}:{TEST_INPUT['port']})",
        data=TEST_INPUT,
    )


@pytest.mark.asyncio
async def test_step_user_invalid_auth(flow: SatisfactoryConfigFlow) -> None:
    """Test step_user shows form with invalid_auth error."""
    with patch(
        "custom_components.satisfactory.config_flow.validate_input",
        side_effect=InvalidAuthError,
    ):
        await flow.async_step_user(TEST_INPUT)

    flow.async_show_form.assert_called_once()
    _, kwargs = flow.async_show_form.call_args
    assert kwargs["errors"] == {"base": "invalid_auth"}


@pytest.mark.asyncio
async def test_step_user_cannot_connect(flow: SatisfactoryConfigFlow) -> None:
    """Test step_user shows form with cannot_connect error."""
    with patch(
        "custom_components.satisfactory.config_flow.validate_input",
        side_effect=CannotConnectError,
    ):
        await flow.async_step_user(TEST_INPUT)

    flow.async_show_form.assert_called_once()
    _, kwargs = flow.async_show_form.call_args
    assert kwargs["errors"] == {"base": "cannot_connect"}
