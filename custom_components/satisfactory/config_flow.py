"""Config flow for the Satisfactory integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT
from homeassistant.exceptions import HomeAssistantError
from satisfactory_api_client import APIError, AsyncSatisfactoryAPI
from satisfactory_api_client.data import MinimumPrivilegeLevel

from .const import CONF_SKIP_SSL, DEFAULT_PORT, DOMAIN

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
        vol.Required(CONF_PASSWORD): str,
        vol.Required(CONF_SKIP_SSL, default=True): bool,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:  # noqa: ARG001
    """Validate the user input allows us to connect."""
    client = AsyncSatisfactoryAPI(
        host=data[CONF_HOST],
        port=data[CONF_PORT],
        skip_ssl_verification=data[CONF_SKIP_SSL],
    )

    try:
        await client.password_login(
            MinimumPrivilegeLevel.ADMINISTRATOR, data[CONF_PASSWORD]
        )
    except APIError as err:
        _LOGGER.debug("Authentication failed: %s", err)
        raise InvalidAuthError from err
    except Exception as err:
        _LOGGER.debug("Cannot connect to Satisfactory server: %s", err)
        raise CannotConnectError from err

    return {"title": f"Satisfactory ({data[CONF_HOST]}:{data[CONF_PORT]})"}


class SatisfactoryConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Satisfactory."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            await self.async_set_unique_id(
                f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}"
            )
            self._abort_if_unique_id_configured()

            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnectError:
                errors["base"] = "cannot_connect"
            except InvalidAuthError:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnectError(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuthError(HomeAssistantError):
    """Error to indicate there is invalid auth."""
