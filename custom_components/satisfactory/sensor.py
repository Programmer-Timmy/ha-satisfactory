"""Sensor platform for the Satisfactory integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import CONF_HOST, CONF_PORT, EntityCategory, UnitOfTime
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SatisfactoryCoordinator

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

PARALLEL_UPDATES = 0


@dataclass(frozen=True, kw_only=True)
class SatisfactorySensorEntityDescription(SensorEntityDescription):
    """Describes a Satisfactory sensor."""

    data_key: str


SENSOR_DESCRIPTIONS: tuple[SatisfactorySensorEntityDescription, ...] = (
    SatisfactorySensorEntityDescription(
        key="num_connected_players",
        data_key="numConnectedPlayers",
        translation_key="num_connected_players",
        native_unit_of_measurement="players",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=None,
    ),
    SatisfactorySensorEntityDescription(
        key="player_limit",
        data_key="playerLimit",
        translation_key="player_limit",
        native_unit_of_measurement="players",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SatisfactorySensorEntityDescription(
        key="tech_tier",
        data_key="techTier",
        translation_key="tech_tier",
    ),
    SatisfactorySensorEntityDescription(
        key="average_tick_rate",
        data_key="averageTickRate",
        translation_key="average_tick_rate",
        native_unit_of_measurement="ticks/s",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    SatisfactorySensorEntityDescription(
        key="total_game_duration",
        data_key="totalGameDuration",
        translation_key="total_game_duration",
        native_unit_of_measurement=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SatisfactorySensorEntityDescription(
        key="active_session_name",
        data_key="activeSessionName",
        translation_key="active_session_name",
    ),
    SatisfactorySensorEntityDescription(
        key="game_phase",
        data_key="gamePhase",
        translation_key="game_phase",
    ),
    SatisfactorySensorEntityDescription(
        key="server_health",
        data_key="serverHealth",
        translation_key="server_health",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Satisfactory sensors from a config entry."""
    coordinator: SatisfactoryCoordinator = entry.runtime_data

    async_add_entities(
        SatisfactorySensorEntity(coordinator, entry, description)
        for description in SENSOR_DESCRIPTIONS
    )


class SatisfactorySensorEntity(
    CoordinatorEntity[SatisfactoryCoordinator], SensorEntity
):
    """Representation of a Satisfactory sensor."""

    entity_description: SatisfactorySensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SatisfactoryCoordinator,
        entry: ConfigEntry,
        description: SatisfactorySensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.unique_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.unique_id or entry.entry_id)},
            name=entry.title,
            manufacturer="Coffee Stain Studios",
            model="Satisfactory Dedicated Server",
            configuration_url=f"https://{entry.data[CONF_HOST]}:{entry.data[CONF_PORT]}",
        )

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        return self.coordinator.data.get(self.entity_description.data_key)
