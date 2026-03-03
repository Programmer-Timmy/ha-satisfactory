"""Tests for the Satisfactory coordinator."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.helpers.update_coordinator import UpdateFailed
from satisfactory_api_client.exceptions import APIError

from custom_components.satisfactory.coordinator import SatisfactoryCoordinator
from custom_components.satisfactory.const import DEFAULT_SCAN_INTERVAL, DOMAIN


@pytest.fixture
def mock_hass() -> MagicMock:
    """Return a mock HomeAssistant instance."""
    return MagicMock()


@pytest.fixture
def mock_client() -> AsyncMock:
    """Return a mock AsyncSatisfactoryAPI client."""
    return AsyncMock()


@pytest.fixture
def coordinator(mock_hass: MagicMock, mock_client: AsyncMock) -> SatisfactoryCoordinator:
    """Return a SatisfactoryCoordinator with mocked dependencies."""
    with patch("homeassistant.helpers.update_coordinator.DataUpdateCoordinator.__init__"):
        coord = SatisfactoryCoordinator.__new__(SatisfactoryCoordinator)
        coord.client = mock_client
        coord.data = {}
        coord.logger = MagicMock()
        coord.hass = mock_hass
        return coord


# --- _sanitise_game_phase ---

class TestSanitiseGamePhase:
    """Tests for _sanitise_game_phase."""

    def test_empty_string(self, coordinator: SatisfactoryCoordinator) -> None:
        assert coordinator._sanitise_game_phase("") == ""  # noqa: SLF001

    def test_strips_path_prefix(self, coordinator: SatisfactoryCoordinator) -> None:
        result = coordinator._sanitise_game_phase(  # noqa: SLF001
            "/Game/FactoryGame/GamePhases/GP_Project_Assembly_Phase_1.GP_Project_Assembly_Phase_1"
        )
        assert result == "GP Project Assembly Phase 1"

    def test_replaces_underscores(self, coordinator: SatisfactoryCoordinator) -> None:
        result = coordinator._sanitise_game_phase("Foo/Bar.Some_Phase_Name")  # noqa: SLF001
        assert result == "Some Phase Name"

    def test_removes_apostrophes(self, coordinator: SatisfactoryCoordinator) -> None:
        result = coordinator._sanitise_game_phase("Foo/Bar.Don't_Stop")  # noqa: SLF001
        assert result == "Dont Stop"

    def test_no_slash_no_dot(self, coordinator: SatisfactoryCoordinator) -> None:
        result = coordinator._sanitise_game_phase("SimplePhase")  # noqa: SLF001
        assert result == "SimplePhase"


# --- _sanitise_average_tick_rate ---

class TestSanitiseAverageTickRate:
    """Tests for _sanitise_average_tick_rate."""

    def test_rounds_to_two_decimals(self, coordinator: SatisfactoryCoordinator) -> None:
        assert coordinator._sanitise_average_tick_rate(30.12345) == 30.12  # noqa: SLF001

    def test_already_rounded(self, coordinator: SatisfactoryCoordinator) -> None:
        assert coordinator._sanitise_average_tick_rate(30.0) == 30.0  # noqa: SLF001

    def test_zero(self, coordinator: SatisfactoryCoordinator) -> None:
        assert coordinator._sanitise_average_tick_rate(0.0) == 0.0  # noqa: SLF001


# --- _sanitise_total_game_duration ---

class TestSanitiseTotalGameDuration:
    """Tests for _sanitise_total_game_duration."""

    def test_converts_seconds_to_hours(self, coordinator: SatisfactoryCoordinator) -> None:
        assert coordinator._sanitise_total_game_duration(7200) == 2  # noqa: SLF001

    def test_truncates_partial_hours(self, coordinator: SatisfactoryCoordinator) -> None:
        assert coordinator._sanitise_total_game_duration(3700) == 1  # noqa: SLF001

    def test_zero(self, coordinator: SatisfactoryCoordinator) -> None:
        assert coordinator._sanitise_total_game_duration(0) == 0  # noqa: SLF001


# --- _sanitise_data ---

class TestSanitiseData:
    """Tests for _sanitise_data."""

    def test_full_data(self, coordinator: SatisfactoryCoordinator) -> None:
        raw = {
            "activeSessionName": "MyGame",
            "numConnectedPlayers": 3,
            "playerLimit": 4,
            "techTier": 5,
            "averageTickRate": 29.9876,
            "totalGameDuration": 10800,
            "gamePhase": "Foo/Bar.Phase_One",
        }
        result = coordinator._sanitise_data(raw)  # noqa: SLF001
        assert result["activeSessionName"] == "MyGame"
        assert result["numConnectedPlayers"] == 3
        assert result["playerLimit"] == 4
        assert result["techTier"] == 5
        assert result["averageTickRate"] == 29.99
        assert result["totalGameDuration"] == 3
        assert result["gamePhase"] == "Phase One"

    def test_missing_keys_use_defaults(self, coordinator: SatisfactoryCoordinator) -> None:
        result = coordinator._sanitise_data({})  # noqa: SLF001
        assert result["activeSessionName"] == ""
        assert result["numConnectedPlayers"] == 0
        assert result["playerLimit"] == 0
        assert result["techTier"] == 0
        assert result["averageTickRate"] == 0.0
        assert result["totalGameDuration"] == 0
        assert result["gamePhase"] == ""


# --- _async_update_data ---

class TestAsyncUpdateData:
    """Tests for _async_update_data."""

    async def test_success(
        self, coordinator: SatisfactoryCoordinator, mock_client: AsyncMock
    ) -> None:
        mock_response = MagicMock()
        mock_response.data = {
            "serverGameState": {
                "activeSessionName": "TestSession",
                "numConnectedPlayers": 2,
                "playerLimit": 4,
                "techTier": 3,
                "averageTickRate": 30.0,
                "totalGameDuration": 3600,
                "gamePhase": "Foo/Bar.Phase_One",
            }
        }
        mock_client.query_server_state.return_value = mock_response

        result = await coordinator._async_update_data()  # noqa: SLF001

        assert result["activeSessionName"] == "TestSession"
        assert result["numConnectedPlayers"] == 2
        assert result["totalGameDuration"] == 1

    async def test_api_error_raises_update_failed(
        self, coordinator: SatisfactoryCoordinator, mock_client: AsyncMock
    ) -> None:
        mock_client.query_server_state.side_effect = APIError("ERR", "server error")

        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()  # noqa: SLF001

    async def test_generic_error_raises_update_failed(
        self, coordinator: SatisfactoryCoordinator, mock_client: AsyncMock
    ) -> None:
        mock_client.query_server_state.side_effect = ConnectionError("timeout")

        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()  # noqa: SLF001

    async def test_empty_server_game_state(
        self, coordinator: SatisfactoryCoordinator, mock_client: AsyncMock
    ) -> None:
        mock_response = MagicMock()
        mock_response.data = {}
        mock_client.query_server_state.return_value = mock_response

        result = await coordinator._async_update_data()  # noqa: SLF001
        assert result["numConnectedPlayers"] == 0
