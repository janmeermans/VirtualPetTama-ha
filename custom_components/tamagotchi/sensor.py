"""Sensor entities exposing Tamagotchi stats (0-10 scale)."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorStateClass
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
            TamagotchiStageSensor(coordinator),
            TamagotchiCreatureTypeSensor(coordinator),
            TamagotchiHungerSensor(coordinator),
            TamagotchiHappinessSensor(coordinator),
            TamagotchiHealthSensor(coordinator),
            TamagotchiDisciplineSensor(coordinator),
            TamagotchiWeightSensor(coordinator),
            TamagotchiAgeSensor(coordinator),
            TamagotchiPoopSensor(coordinator),
            TamagotchiCareMistakesSensor(coordinator),
        ]
    )


# ---------------------------------------------------------------------------
# Base class
# ---------------------------------------------------------------------------

class TamagotchiSensorBase(SensorEntity):
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


# ---------------------------------------------------------------------------
# Concrete sensors
# ---------------------------------------------------------------------------

class TamagotchiStageSensor(TamagotchiSensorBase):
    _attr_name = "Stage"
    _attr_icon = "mdi:egg"

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry_id}_stage"

    @property
    def native_value(self):
        return self._tama.stage if self._tama else None

    @property
    def extra_state_attributes(self):
        if not self._tama:
            return {}
        return {"age_hours": round(self._tama.age_hours, 1)}


class TamagotchiCreatureTypeSensor(TamagotchiSensorBase):
    _attr_name = "Creature Type"
    _attr_icon = "mdi:paw"

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry_id}_creature_type"

    @property
    def native_value(self):
        return self._tama.creature_type if self._tama else None


class TamagotchiHungerSensor(TamagotchiSensorBase):
    """Hunger 0-10. 10 = full, 0 = starving."""

    _attr_name = "Hunger"
    _attr_native_unit_of_measurement = "hearts"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:food"

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry_id}_hunger"

    @property
    def native_value(self):
        return self._tama.hunger_int if self._tama else None

    @property
    def extra_state_attributes(self):
        if not self._tama:
            return {}
        return {"value_exact": round(self._tama.hunger, 2)}


class TamagotchiHappinessSensor(TamagotchiSensorBase):
    """Happiness 0-10. 10 = happy, 0 = miserable."""

    _attr_name = "Happiness"
    _attr_native_unit_of_measurement = "hearts"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:emoticon-happy"

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry_id}_happiness"

    @property
    def native_value(self):
        return self._tama.happiness_int if self._tama else None

    @property
    def extra_state_attributes(self):
        if not self._tama:
            return {}
        return {"value_exact": round(self._tama.happiness, 2)}


class TamagotchiHealthSensor(TamagotchiSensorBase):
    """Health 0-10. 10 = healthy, 0 = death."""

    _attr_name = "Health"
    _attr_native_unit_of_measurement = "hearts"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:heart-pulse"

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry_id}_health"

    @property
    def native_value(self):
        return self._tama.health_int if self._tama else None

    @property
    def extra_state_attributes(self):
        if not self._tama:
            return {}
        return {"value_exact": round(self._tama.health, 2)}


class TamagotchiDisciplineSensor(TamagotchiSensorBase):
    """Discipline 0-10. Starts at 0 for each new creature."""

    _attr_name = "Discipline"
    _attr_native_unit_of_measurement = "hearts"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:gavel"

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry_id}_discipline"

    @property
    def native_value(self):
        return self._tama.discipline if self._tama else None


class TamagotchiWeightSensor(TamagotchiSensorBase):
    _attr_name = "Weight"
    _attr_native_unit_of_measurement = "oz"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:scale"

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry_id}_weight"

    @property
    def native_value(self):
        return self._tama.weight if self._tama else None


class TamagotchiAgeSensor(TamagotchiSensorBase):
    _attr_name = "Age"
    _attr_native_unit_of_measurement = "h"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_icon = "mdi:clock-outline"

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry_id}_age"

    @property
    def native_value(self):
        return round(self._tama.age_hours, 1) if self._tama else None


class TamagotchiPoopSensor(TamagotchiSensorBase):
    _attr_name = "Poop Count"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:emoticon-poop"

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry_id}_poop"

    @property
    def native_value(self):
        return self._tama.poop_count if self._tama else None


class TamagotchiCareMistakesSensor(TamagotchiSensorBase):
    _attr_name = "Care Mistakes"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_icon = "mdi:alert-circle"

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry_id}_care_mistakes"

    @property
    def native_value(self):
        return self._tama.care_mistakes if self._tama else None
