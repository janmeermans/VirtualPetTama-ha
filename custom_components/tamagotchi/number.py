"""Number entity — palette slider for the Tamagotchi display."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, PALETTE_NAMES
from .coordinator import TamagotchiCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: TamagotchiCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([TamagotchiPaletteSlider(coordinator, entry)])


class TamagotchiPaletteSlider(NumberEntity):
    """Slider (0 – 3) that selects the LCD colour palette.

    Position → palette:
      0 = Classic (Game Boy green)
      1 = Amber   (retro CRT)
      2 = Blue    (ocean)
      3 = Sakura  (cherry blossom)
    """

    _attr_has_entity_name = True
    _attr_name = "Colour Palette"
    _attr_icon = "mdi:palette"
    _attr_should_poll = False

    _attr_native_min_value = 0
    _attr_native_max_value = 3
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER

    def __init__(self, coordinator: TamagotchiCoordinator, entry: ConfigEntry) -> None:
        self._coordinator = coordinator
        self._attr_unique_id = f"{entry.entry_id}_palette_slider"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=coordinator.name,
            manufacturer="Virtual Pet Co.",
            model="Tamagotchi",
        )

    # ------------------------------------------------------------------ value

    @property
    def native_value(self) -> float:
        try:
            return float(PALETTE_NAMES.index(self._coordinator.palette))
        except ValueError:
            return 0.0

    async def async_set_native_value(self, value: float) -> None:
        palette = PALETTE_NAMES[int(value)]
        await self._coordinator.async_set_palette(palette)
        self.async_write_ha_state()

    # --------------------------------------------------------- extra attributes

    @property
    def extra_state_attributes(self) -> dict:
        idx = int(self.native_value)
        return {
            "palette_name": PALETTE_NAMES[idx],
            "palettes": {str(i): name for i, name in enumerate(PALETTE_NAMES)},
        }

    # --------------------------------------------------------- push updates

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
