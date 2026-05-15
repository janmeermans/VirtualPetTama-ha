"""Binary sensor entities for boolean Tamagotchi states."""
from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
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
            TamagotchiAliveSensor(coordinator),
            TamagotchiSickSensor(coordinator),
            TamagotchiSleepingSensor(coordinator),
            TamagotchiAttentionSensor(coordinator),
        ]
    )


class TamagotchiBinarySensorBase(BinarySensorEntity):
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, coordinator: TamagotchiCoordinator) -> None:
        self.coordinator = coordinator
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.entry_id)},
            name=coordinator.name,
            manufacturer="Virtual Pet Co.",
            model="Tamagotchi",
        )

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                self.coordinator.signal_state,
                self._handle_update,
            )
        )

    @callback
    def _handle_update(self) -> None:
        self.async_write_ha_state()

    @property
    def _tama(self):
        return self.coordinator.tama


class TamagotchiAliveSensor(TamagotchiBinarySensorBase):
    _attr_name = "Is Alive"
    _attr_icon = "mdi:heart"

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry_id}_is_alive"

    @property
    def is_on(self):
        return self._tama.is_alive if self._tama else False


class TamagotchiSickSensor(TamagotchiBinarySensorBase):
    _attr_name = "Is Sick"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_icon = "mdi:medical-bag"

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry_id}_is_sick"

    @property
    def is_on(self):
        return self._tama.is_sick if self._tama else False


class TamagotchiSleepingSensor(TamagotchiBinarySensorBase):
    _attr_name = "Is Sleeping"
    _attr_icon = "mdi:sleep"

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry_id}_is_sleeping"

    @property
    def is_on(self):
        return self._tama.is_sleeping if self._tama else False


class TamagotchiAttentionSensor(TamagotchiBinarySensorBase):
    _attr_name = "Needs Attention"
    _attr_device_class = BinarySensorDeviceClass.OCCUPANCY
    _attr_icon = "mdi:bell-ring"

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry_id}_needs_attention"

    @property
    def is_on(self):
        return self._tama.needs_attention if self._tama else False
