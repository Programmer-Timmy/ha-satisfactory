"""The Satisfactory integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, Platform
from homeassistant.exceptions import ConfigEntryAuthFailed
from satisfactory_api_client import APIError, AsyncSatisfactoryAPI
from satisfactory_api_client.data.minimum_privilege_level import MinimumPrivilegeLevel

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

from .const import CONF_SKIP_SSL
from .coordinator import SatisfactoryCoordinator

_PLATFORMS: list[Platform] = [Platform.SENSOR]

type SatisfactoryConfigEntry = ConfigEntry[SatisfactoryCoordinator]


async def async_setup_entry(
    hass: HomeAssistant, entry: SatisfactoryConfigEntry
) -> bool:
    """Set up Satisfactory from a config entry."""
    client = AsyncSatisfactoryAPI(
        host=entry.data[CONF_HOST],
        port=entry.data[CONF_PORT],
        skip_ssl_verification=entry.data.get(CONF_SKIP_SSL, True),
    )

    try:
        await client.password_login(
            MinimumPrivilegeLevel.ADMINISTRATOR, entry.data[CONF_PASSWORD]
        )
    except APIError as err:
        raise ConfigEntryAuthFailed from err

    coordinator = SatisfactoryCoordinator(hass, client)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: SatisfactoryConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
