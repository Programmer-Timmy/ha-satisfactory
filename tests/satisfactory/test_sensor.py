"""Tests for the Satisfactory sensor platform."""

from unittest.mock import MagicMock

import pytest

from custom_components.satisfactory.sensor import (
    SENSOR_DESCRIPTIONS,
    SatisfactorySensorEntity,
    SatisfactorySensorEntityDescription,
)

SAMPLE_DATA = {
    "activeSessionName": "TestSession",
    "numConnectedPlayers": 2,
    "playerLimit": 4,
    "techTier": 3,
    "averageTickRate": 30.0,
    "totalGameDuration": 5,
    "gamePhase": "Phase One",
    "serverHealth": "healthy",
}


@pytest.fixture
def mock_coordinator() -> MagicMock:
    """Return a mock coordinator with sample data."""
    coordinator = MagicMock()
    coordinator.data = SAMPLE_DATA
    return coordinator


@pytest.fixture
def mock_entry() -> MagicMock:
    """Return a mock config entry."""
    entry = MagicMock()
    entry.unique_id = "1.1.1.1:7777"
    entry.entry_id = "test_entry_id"
    entry.title = "Satisfactory (1.1.1.1:7777)"
    entry.data = {"host": "1.1.1.1", "port": 7777}
    return entry


def make_sensor(
    coordinator: MagicMock,
    entry: MagicMock,
    description: SatisfactorySensorEntityDescription,
) -> SatisfactorySensorEntity:
    """Create a SatisfactorySensorEntity, bypassing CoordinatorEntity.__init__."""
    entity = SatisfactorySensorEntity.__new__(SatisfactorySensorEntity)
    entity.coordinator = coordinator
    entity.entity_description = description
    entity._attr_unique_id = f"{entry.unique_id}_{description.key}"  # noqa: SLF001
    return entity


class TestSensorDescriptions:
    """Tests for SENSOR_DESCRIPTIONS."""

    def test_all_descriptions_have_data_key(self) -> None:
        for desc in SENSOR_DESCRIPTIONS:
            assert desc.data_key, f"{desc.key} is missing data_key"

    def test_expected_sensors_present(self) -> None:
        keys = {d.key for d in SENSOR_DESCRIPTIONS}
        assert "num_connected_players" in keys
        assert "player_limit" in keys
        assert "tech_tier" in keys
        assert "average_tick_rate" in keys
        assert "total_game_duration" in keys
        assert "active_session_name" in keys
        assert "game_phase" in keys
        assert "server_health" in keys

    def test_seven_sensors_defined(self) -> None:
        assert len(SENSOR_DESCRIPTIONS) == 8


class TestSatisfactorySensorEntity:
    """Tests for SatisfactorySensorEntity."""

    def test_native_value_returns_coordinator_data(
        self, mock_coordinator: MagicMock, mock_entry: MagicMock
    ) -> None:
        desc = next(d for d in SENSOR_DESCRIPTIONS if d.key == "num_connected_players")
        sensor = make_sensor(mock_coordinator, mock_entry, desc)
        assert sensor.native_value == 2

    def test_native_value_active_session_name(
        self, mock_coordinator: MagicMock, mock_entry: MagicMock
    ) -> None:
        desc = next(d for d in SENSOR_DESCRIPTIONS if d.key == "active_session_name")
        sensor = make_sensor(mock_coordinator, mock_entry, desc)
        assert sensor.native_value == "TestSession"

    def test_native_value_game_phase(
        self, mock_coordinator: MagicMock, mock_entry: MagicMock
    ) -> None:
        desc = next(d for d in SENSOR_DESCRIPTIONS if d.key == "game_phase")
        sensor = make_sensor(mock_coordinator, mock_entry, desc)
        assert sensor.native_value == "Phase One"

    def test_native_value_returns_none_when_key_missing(
        self, mock_entry: MagicMock
    ) -> None:
        coordinator = MagicMock()
        coordinator.data = {}
        desc = next(d for d in SENSOR_DESCRIPTIONS if d.key == "tech_tier")
        sensor = make_sensor(coordinator, mock_entry, desc)
        assert sensor.native_value is None

    def test_unique_id_format(
        self, mock_coordinator: MagicMock, mock_entry: MagicMock
    ) -> None:
        desc = next(d for d in SENSOR_DESCRIPTIONS if d.key == "tech_tier")
        sensor = make_sensor(mock_coordinator, mock_entry, desc)
        assert sensor._attr_unique_id == "1.1.1.1:7777_tech_tier"  # noqa: SLF001

    @pytest.mark.parametrize("desc", SENSOR_DESCRIPTIONS)
    def test_all_sensors_return_correct_value(
        self,
        mock_coordinator: MagicMock,
        mock_entry: MagicMock,
        desc: SatisfactorySensorEntityDescription,
    ) -> None:
        sensor = make_sensor(mock_coordinator, mock_entry, desc)
        assert sensor.native_value == SAMPLE_DATA[desc.data_key]
