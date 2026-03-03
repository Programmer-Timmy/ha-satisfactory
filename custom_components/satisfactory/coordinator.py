"""DataUpdateCoordinator for the Satisfactory integration."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from satisfactory_api_client.exceptions import APIError

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from satisfactory_api_client import AsyncSatisfactoryAPI

_LOGGER = logging.getLogger(__name__)


class SatisfactoryCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to poll the Satisfactory Dedicated Server API."""

    def __init__(self, hass: HomeAssistant, client: AsyncSatisfactoryAPI) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.client = client

    def _sanitise_game_phase(self, game_phase: str) -> str:
        """Convert the game phase string from the API into a more user-friendly format."""  # noqa: E501
        if not game_phase:
            return ""
        return (
            game_phase.rsplit("/", maxsplit=1)[-1]
            .rsplit(".", maxsplit=1)[-1]
            .replace("_", " ")
            .replace("'", "")
        )

    def _sanitise_average_tick_rate(self, tick_rate: float) -> float:
        """Round the average tick rate to 2 decimal places."""
        return round(tick_rate, 2)

    def _sanitise_total_game_duration(self, duration: int) -> int:
        """Convert total game duration from seconds to hours."""
        return duration // 3600

    def _sanitise_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """Sanitise the raw data from the API."""
        return {
            "activeSessionName": data.get("activeSessionName", ""),
            "numConnectedPlayers": data.get("numConnectedPlayers", 0),
            "playerLimit": data.get("playerLimit", 0),
            "techTier": data.get("techTier", 0),
            "averageTickRate": self._sanitise_average_tick_rate(
                data.get("averageTickRate", 0.0)
            ),
            "totalGameDuration": self._sanitise_total_game_duration(
                data.get("totalGameDuration", 0)
            ),
            "gamePhase": self._sanitise_game_phase(data.get("gamePhase", "")),
        }

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the Satisfactory server."""
        try:
            state_response = await self.client.query_server_state()
            health_response = await self.client.health_check()
        except APIError as err:
            raise ConfigEntryAuthFailed from err
        except Exception as err:
            msg = f"Unexpected error: {err}"
            raise UpdateFailed(msg) from err

        _LOGGER.debug("Satisfactory server response: %s", state_response)

        data = self._sanitise_data(state_response.data.get("serverGameState", {}))
        data["serverHealth"] = health_response.data.get("health", "unknown")
        return data
