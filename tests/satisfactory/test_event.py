"""Tests for the Satisfactory event platform."""

from unittest.mock import MagicMock, patch

import pytest

from custom_components.satisfactory.event import SatisfactoryPlayerActivityEventEntity


@pytest.fixture
def mock_coordinator() -> MagicMock:
    """Return a mock coordinator with sample data."""
    coordinator = MagicMock()
    coordinator.data = {"numConnectedPlayers": 2, "playerLimit": 4}
    return coordinator


@pytest.fixture
def entity(
    mock_coordinator: MagicMock,
) -> SatisfactoryPlayerActivityEventEntity:
    """Return a SatisfactoryPlayerActivityEventEntity with mocked dependencies."""
    with patch("homeassistant.helpers.update_coordinator.CoordinatorEntity.__init__"):
        ent = SatisfactoryPlayerActivityEventEntity.__new__(
            SatisfactoryPlayerActivityEventEntity
        )
        ent.coordinator = mock_coordinator
        ent._prev_players = None  # noqa: SLF001
        ent.async_write_ha_state = MagicMock()
        return ent


class TestSatisfactoryPlayerActivityEventEntity:
    """Tests for SatisfactoryPlayerActivityEventEntity."""

    def test_event_types(self, entity: SatisfactoryPlayerActivityEventEntity) -> None:
        assert entity.event_types == ["player_joined", "player_left"]

    def test_player_joined_fires_event(
        self,
        entity: SatisfactoryPlayerActivityEventEntity,
        mock_coordinator: MagicMock,
    ) -> None:
        entity._prev_players = 1  # noqa: SLF001
        mock_coordinator.data = {"numConnectedPlayers": 2, "playerLimit": 4}
        with patch.object(entity, "_trigger_event") as mock_trigger:
            entity._handle_coordinator_update()  # noqa: SLF001
        mock_trigger.assert_called_once_with(
            "player_joined",
            {"num_connected_players": 2, "player_limit": 4},
        )

    def test_player_left_fires_event(
        self,
        entity: SatisfactoryPlayerActivityEventEntity,
        mock_coordinator: MagicMock,
    ) -> None:
        entity._prev_players = 3  # noqa: SLF001
        mock_coordinator.data = {"numConnectedPlayers": 2, "playerLimit": 4}
        with patch.object(entity, "_trigger_event") as mock_trigger:
            entity._handle_coordinator_update()  # noqa: SLF001
        mock_trigger.assert_called_once_with(
            "player_left",
            {"num_connected_players": 2, "player_limit": 4},
        )

    def test_no_event_on_first_update(
        self, entity: SatisfactoryPlayerActivityEventEntity
    ) -> None:
        entity._prev_players = None  # noqa: SLF001
        with patch.object(entity, "_trigger_event") as mock_trigger:
            entity._handle_coordinator_update()  # noqa: SLF001
        mock_trigger.assert_not_called()

    def test_no_event_when_count_unchanged(
        self,
        entity: SatisfactoryPlayerActivityEventEntity,
        mock_coordinator: MagicMock,
    ) -> None:
        entity._prev_players = 2  # noqa: SLF001
        mock_coordinator.data = {"numConnectedPlayers": 2, "playerLimit": 4}
        with patch.object(entity, "_trigger_event") as mock_trigger:
            entity._handle_coordinator_update()  # noqa: SLF001
        mock_trigger.assert_not_called()

    def test_prev_players_updated_after_call(
        self,
        entity: SatisfactoryPlayerActivityEventEntity,
        mock_coordinator: MagicMock,
    ) -> None:
        entity._prev_players = 1  # noqa: SLF001
        mock_coordinator.data = {"numConnectedPlayers": 3, "playerLimit": 4}
        with patch.object(entity, "_trigger_event"):
            entity._handle_coordinator_update()  # noqa: SLF001
        assert entity._prev_players == 3  # noqa: SLF001
