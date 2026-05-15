"""Button entities for Tamagotchi actions."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import TamagotchiCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: TamagotchiCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            TamagotchiButton(coordinator, "feed_meal",    "Feed Meal",    "mdi:food-drumstick"),
            TamagotchiButton(coordinator, "feed_snack",   "Feed Snack",   "mdi:candy"),
            TamagotchiButton(coordinator, "play",         "Play",         "mdi:gamepad-variant"),
            TamagotchiButton(coordinator, "clean",        "Clean",        "mdi:broom"),
            TamagotchiButton(coordinator, "medicate",     "Medicate",     "mdi:pill"),
            TamagotchiButton(coordinator, "discipline",   "Discipline",   "mdi:gavel"),
            TamagotchiButton(coordinator, "toggle_light", "Toggle Light", "mdi:lightbulb"),
        ]
    )


class TamagotchiButton(ButtonEntity):
    """A single action button for the Tamagotchi."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(
        self,
        coordinator: TamagotchiCoordinator,
        action: str,
        name: str,
        icon: str,
    ) -> None:
        self.coordinator = coordinator
        self._action = action
        self._attr_name = name
        self._attr_icon = icon
        self._attr_unique_id = f"{coordinator.entry_id}_{action}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.entry_id)},
            name=coordinator.name,
            manufacturer="Virtual Pet Co.",
            model="Tamagotchi",
        )

    async def async_press(self) -> None:
        await self.coordinator.async_action(self._action)
