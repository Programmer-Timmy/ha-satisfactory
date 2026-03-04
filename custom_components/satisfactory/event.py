"""Event platform for the Satisfactory integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.event import EventEntity
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SatisfactoryCoordinator

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Satisfactory event entities from a config entry."""
    coordinator: SatisfactoryCoordinator = entry.runtime_data
    async_add_entities([SatisfactoryPlayerActivityEventEntity(coordinator, entry)])


class SatisfactoryPlayerActivityEventEntity(
    CoordinatorEntity[SatisfactoryCoordinator], EventEntity
):
    """Event entity that fires when players join or leave the server."""

    _attr_event_types: list[str] = ["player_joined", "player_left"]  # noqa: RUF012
    _attr_translation_key = "player_activity"
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SatisfactoryCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the event entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{(entry.unique_id or entry.entry_id)}_player_activity"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.unique_id or entry.entry_id)},
            name=entry.title,
            manufacturer="Coffee Stain Studios",
            model="Satisfactory Dedicated Server",
            configuration_url=entry.data.get("configuration_url")
            if isinstance(entry.data, dict)
            else None,
        )
        self._prev_players: int | None = None

    @callback
    def _handle_coordinator_update(self) -> None:
        """Trigger a player event when the connected player count changes."""
        new_players: int = self.coordinator.data.get("numConnectedPlayers", 0)
        player_limit: int = self.coordinator.data.get("playerLimit", 0)

        if self._prev_players is not None:
            if new_players > self._prev_players:
                self._trigger_event(
                    "player_joined",
                    {
                        "num_connected_players": new_players,
                        "player_limit": player_limit,
                    },
                )
            elif new_players < self._prev_players:
                self._trigger_event(
                    "player_left",
                    {
                        "num_connected_players": new_players,
                        "player_limit": player_limit,
                    },
                )

        self._prev_players = new_players
        super()._handle_coordinator_update()
