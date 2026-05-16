"""Image entity — the animated 16×16 LCD display."""
from __future__ import annotations

from homeassistant.components.image import ImageEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import homeassistant.util.dt as dt_util

from .const import DOMAIN
from .coordinator import TamagotchiCoordinator
from .renderer import render


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: TamagotchiCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([TamagotchiDisplay(coordinator, hass)])


class TamagotchiDisplay(ImageEntity):
    """16×16 LCD-style display rendered as a 144×144 PNG."""

    _attr_has_entity_name = True
    _attr_name = "Display"
    _attr_content_type = "image/png"
    _attr_should_poll = False

    def __init__(self, coordinator: TamagotchiCoordinator, hass: HomeAssistant) -> None:
        super().__init__(hass)
        self.coordinator = coordinator
        self._attr_unique_id = f"{coordinator.entry_id}_display"
        self._attr_image_last_updated = dt_util.utcnow()
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.entry_id)},
            name=coordinator.name,
            manufacturer="Virtual Pet Co.",
            model="Tamagotchi",
        )

    async def async_added_to_hass(self) -> None:
        # State updates (hunger/happiness/stage changed) → redraw
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                self.coordinator.signal_state,
                self._handle_update,
            )
        )
        # Animation ticks → toggle frame, redraw
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                self.coordinator.signal_animate,
                self._handle_animate,
            )
        )

    @callback
    def _handle_update(self) -> None:
        self._attr_image_last_updated = dt_util.utcnow()
        self.async_write_ha_state()

    @callback
    def _handle_animate(self) -> None:
        self._attr_image_last_updated = dt_util.utcnow()
        self.async_write_ha_state()

    async def async_image(self) -> bytes | None:
        """Return PNG bytes for the current frame."""
        if self.coordinator.tama is None:
            return None
        return render(self.coordinator.tama, palette_name=self.coordinator.palette)
