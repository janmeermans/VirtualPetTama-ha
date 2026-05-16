"""Coordinator — owns game state, persistence, and scheduling."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.storage import Store
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import (
    DOMAIN,
    STORAGE_KEY,
    STORAGE_VERSION,
    TICK_MINUTES,
    ANIMATE_SECONDS,
    SIGNAL_STATE_UPDATED,
    SIGNAL_ANIMATE,
    DEFAULT_PALETTE,
    PALETTE_NAMES,
)
from .core import TamagotchiCore

_LOGGER = logging.getLogger(__name__)


class TamagotchiCoordinator:
    """Manages one Tamagotchi instance: state, storage, ticks, animations."""

    def __init__(self, hass: HomeAssistant, entry_id: str, name: str) -> None:
        self.hass = hass
        self.entry_id = entry_id
        self.name = name
        self._store = Store(hass, STORAGE_VERSION, f"{STORAGE_KEY}_{entry_id}")
        self.tama: TamagotchiCore | None = None
        self.palette: str = DEFAULT_PALETTE
        self._unsub_tick = None
        self._unsub_animate = None

    # ------------------------------------------------------------------
    # Signal helpers
    # ------------------------------------------------------------------

    @property
    def signal_state(self) -> str:
        return SIGNAL_STATE_UPDATED.format(entry_id=self.entry_id)

    @property
    def signal_animate(self) -> str:
        return SIGNAL_ANIMATE.format(entry_id=self.entry_id)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def async_setup(self) -> None:
        """Load persisted state and start game clock + animation ticker."""
        stored = await self._store.async_load()
        if stored:
            self.tama = TamagotchiCore.from_dict(stored.get("tama", stored))
            self.palette = stored.get("palette", DEFAULT_PALETTE)
            _LOGGER.info("Loaded Tamagotchi '%s' from storage (stage=%s)", self.name, self.tama.stage)
        else:
            self.tama = TamagotchiCore(self.name)
            _LOGGER.info("Created new Tamagotchi '%s'", self.name)

        self._unsub_tick = async_track_time_interval(
            self.hass,
            self._async_tick,
            timedelta(minutes=TICK_MINUTES),
        )
        self._unsub_animate = async_track_time_interval(
            self.hass,
            self._async_animate,
            timedelta(seconds=ANIMATE_SECONDS),
        )

    async def async_shutdown(self) -> None:
        """Stop all scheduled callbacks and persist state."""
        if self._unsub_tick:
            self._unsub_tick()
            self._unsub_tick = None
        if self._unsub_animate:
            self._unsub_animate()
            self._unsub_animate = None
        await self._async_save()

    # ------------------------------------------------------------------
    # Scheduled callbacks
    # ------------------------------------------------------------------

    @callback
    def _async_tick(self, _now) -> None:
        """Game tick every TICK_MINUTES minutes."""
        if self.tama is None:
            return
        events = self.tama.tick(TICK_MINUTES)
        if events:
            _LOGGER.debug("Tamagotchi '%s' events: %s", self.name, events)
        self.hass.async_create_task(self._async_save())
        async_dispatcher_send(self.hass, self.signal_state)

    @callback
    def _async_animate(self, _now) -> None:
        """Animation frame toggle every ANIMATE_SECONDS seconds."""
        if self.tama is None:
            return
        self.tama.animation_frame ^= 1
        async_dispatcher_send(self.hass, self.signal_animate)

    # ------------------------------------------------------------------
    # Actions (called by button entities)
    # ------------------------------------------------------------------

    async def async_action(self, action: str) -> bool:
        """Execute a named game action and persist + notify if it succeeded."""
        if self.tama is None:
            return False

        action_map = {
            "feed_meal":     self.tama.feed_meal,
            "feed_snack":    self.tama.feed_snack,
            "play":          self.tama.play,
            "clean":         self.tama.clean,
            "medicate":      self.tama.medicate,
            "discipline":    self.tama.do_discipline,
            "toggle_light":  self.tama.toggle_light,
        }

        fn = action_map.get(action)
        if fn is None:
            _LOGGER.warning("Unknown action '%s'", action)
            return False

        result = fn()
        if result:
            await self._async_save()
            async_dispatcher_send(self.hass, self.signal_state)
            async_dispatcher_send(self.hass, self.signal_animate)
        return result

    # ------------------------------------------------------------------
    # Palette
    # ------------------------------------------------------------------

    async def async_set_palette(self, palette_name: str) -> None:
        """Set the display colour palette and notify all listeners."""
        if palette_name not in PALETTE_NAMES:
            _LOGGER.warning("Unknown palette '%s'", palette_name)
            return
        self.palette = palette_name
        await self._async_save()
        async_dispatcher_send(self.hass, self.signal_animate)

    # ------------------------------------------------------------------
    # Storage
    # ------------------------------------------------------------------

    async def _async_save(self) -> None:
        if self.tama is not None:
            await self._store.async_save({
                "tama": self.tama.to_dict(),
                "palette": self.palette,
            })
