"""Palette selector entity for the Tamagotchi integration."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, PALETTE_NAMES, DEFAULT_PALETTE
from .coordinator import TamagotchiCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: TamagotchiCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([TamagotchiPaletteSelect(coordinator, entry)])


class TamagotchiPaletteSelect(SelectEntity):
    """Select entity to choose the display colour palette."""

    _attr_has_entity_name = True
    _attr_name = "Palette"
    _attr_options = PALETTE_NAMES
    _attr_icon = "mdi:palette"
    _attr_should_poll = False

    def __init__(self, coordinator: TamagotchiCoordinator, entry: ConfigEntry) -> None:
        self._coordinator = coordinator
        self._attr_unique_id = f"{entry.entry_id}_palette"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": coordinator.name,
            "manufacturer": "Tamagotchi",
            "model": "Virtual Pet",
        }

    @property
    def current_option(self) -> str:
        return self._coordinator.palette

    async def async_select_option(self, option: str) -> None:
        await self._coordinator.async_set_palette(option)
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                self._coordinator.signal_animate,
                self._handle_update,
            )
        )

    @callback
    def _handle_update(self) -> None:
        self.async_write_ha_state()
