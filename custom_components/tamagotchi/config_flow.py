"""Config flow for the Tamagotchi integration."""
from __future__ import annotations

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .const import DOMAIN, CONF_NAME

_NAME_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME, default="Tama"): str,
    }
)


class TamagotchiConfigFlow(ConfigFlow, domain=DOMAIN):
    """Single-step config flow: ask for a pet name."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            name = user_input[CONF_NAME].strip()
            if not name:
                errors[CONF_NAME] = "name_empty"
            else:
                await self.async_set_unique_id(name.lower())
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=name, data={CONF_NAME: name})

        return self.async_show_form(
            step_id="user",
            data_schema=_NAME_SCHEMA,
            errors=errors,
        )
