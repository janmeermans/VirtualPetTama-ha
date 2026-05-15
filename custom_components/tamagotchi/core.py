"""Tamagotchi game logic — no HA dependencies."""
from __future__ import annotations

import random
from datetime import datetime

from .const import (
    STAGE_EGG, STAGE_BABY, STAGE_CHILD, STAGE_TEEN,
    STAGE_ADULT, STAGE_SENIOR, STAGE_DEAD,
    STAGES, STAGE_HOURS, STAT_MAX,
)


class TamagotchiCore:
    """Pure-Python virtual pet state machine."""

    def __init__(self, name: str = "Tama") -> None:
        self.name: str = name
        self.stage: str = STAGE_EGG
        self.age_hours: float = 0.0
        self.stage_start_age: float = 0.0   # age_hours when current stage began

        # Stats: 0.0 – 4.0 (hearts)
        self.hunger: float = 4.0      # 4 = full, 0 = starving
        self.happiness: float = 4.0   # 4 = happy, 0 = miserable

        self.discipline: int = 50     # 0–100 %
        self.weight: int = 5          # arbitrary units
        self.poop_count: int = 0      # 0–4
        self.care_mistakes: int = 0

        self.is_sick: bool = False
        self.is_sleeping: bool = False
        self.is_alive: bool = True
        self.needs_attention: bool = False

        # Visual animation frame (0 or 1), toggled by coordinator
        self.animation_frame: int = 0

        # Configurable sleep window (24-h clock)
        self.sleep_start_hour: int = 21
        self.sleep_end_hour: int = 9

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}

    @classmethod
    def from_dict(cls, data: dict) -> "TamagotchiCore":
        obj = cls(data.get("name", "Tama"))
        for key, val in data.items():
            if hasattr(obj, key):
                setattr(obj, key, val)
        return obj

    # ------------------------------------------------------------------
    # Game tick
    # ------------------------------------------------------------------

    def tick(self, elapsed_minutes: float) -> list[str]:
        """Advance the game by *elapsed_minutes*. Returns a list of event strings."""
        if not self.is_alive:
            return []

        events: list[str] = []
        now_hour = datetime.now().hour

        # ---- Sleep ----
        if self.stage not in (STAGE_EGG, STAGE_DEAD):
            should_sleep = (
                now_hour >= self.sleep_start_hour or now_hour < self.sleep_end_hour
            )
            if should_sleep and not self.is_sleeping:
                self.is_sleeping = True
                events.append("sleeping")
            elif not should_sleep and self.is_sleeping:
                self.is_sleeping = False
                events.append("woke_up")

        if self.is_sleeping:
            return events

        # ---- Age ----
        self.age_hours += elapsed_minutes / 60.0

        # ---- Stat decay ----
        # Hunger: lose 1 heart per 30 min
        self.hunger = max(0.0, self.hunger - elapsed_minutes / 30.0)
        # Happiness: lose 1 heart per 60 min
        self.happiness = max(0.0, self.happiness - elapsed_minutes / 60.0)

        # ---- Poop ----
        if self.poop_count < 4 and random.random() < elapsed_minutes / 90.0:
            self.poop_count += 1
            events.append("pooped")

        # ---- Sickness ----
        if not self.is_sick:
            if self.poop_count >= 3 and random.random() < 0.4 * (elapsed_minutes / 60.0):
                self.is_sick = True
                events.append("got_sick")
            elif self.weight > 10 and random.random() < 0.15 * (elapsed_minutes / 60.0):
                self.is_sick = True
                events.append("got_sick")

        if self.is_sick:
            # Extra happiness drain when ill
            self.happiness = max(0.0, self.happiness - elapsed_minutes / 30.0)

        # ---- Attention flag ----
        wants = (
            self.hunger < 1.0
            or self.happiness < 1.0
            or self.poop_count >= 2
            or self.is_sick
        )
        if wants and not self.needs_attention:
            self.needs_attention = True
            events.append("needs_attention")

        # ---- Care mistakes ----
        if self.needs_attention and (self.hunger < 0.5 or self.happiness < 0.5):
            self.care_mistakes += 1

        # ---- Death from starvation ----
        if self.hunger <= 0.0 and self.age_hours > 1.0:
            if random.random() < 0.25 * (elapsed_minutes / 60.0):
                self._die(events)
                return events

        # ---- Evolution ----
        self._check_evolution(events)

        return events

    def _check_evolution(self, events: list[str]) -> None:
        if self.stage in (STAGE_DEAD, STAGE_SENIOR) or self.stage not in STAGE_HOURS:
            return
        stage_age = self.age_hours - self.stage_start_age
        if stage_age >= STAGE_HOURS[self.stage]:
            idx = STAGES.index(self.stage)
            if idx + 1 < len(STAGES):
                old = self.stage
                self.stage = STAGES[idx + 1]
                self.stage_start_age = self.age_hours
                events.append(f"evolved:{old}:{self.stage}")

    def _die(self, events: list[str]) -> None:
        self.is_alive = False
        self.stage = STAGE_DEAD
        events.append("died")

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def feed_meal(self) -> bool:
        if not self._can_act() or self.stage == STAGE_EGG:
            return False
        if self.hunger >= STAT_MAX:
            return False
        self.hunger = min(STAT_MAX, self.hunger + 1.0)
        self.weight = min(99, self.weight + 1)
        self._update_attention()
        return True

    def feed_snack(self) -> bool:
        if not self._can_act() or self.stage == STAGE_EGG:
            return False
        self.hunger = min(STAT_MAX, self.hunger + 0.5)
        self.happiness = min(STAT_MAX, self.happiness + 0.5)
        self.weight = min(99, self.weight + 2)
        self._update_attention()
        return True

    def play(self) -> bool:
        if not self._can_act() or self.stage == STAGE_EGG:
            return False
        self.happiness = min(STAT_MAX, self.happiness + 1.0)
        self.weight = max(1, self.weight - 1)
        self._update_attention()
        return True

    def clean(self) -> bool:
        if not self.is_alive or self.poop_count == 0:
            return False
        self.poop_count = 0
        self._update_attention()
        return True

    def medicate(self) -> bool:
        if not self.is_alive or not self.is_sick:
            return False
        self.is_sick = False
        self._update_attention()
        return True

    def do_discipline(self) -> bool:
        if not self._can_act():
            return False
        self.discipline = min(100, self.discipline + 10)
        return True

    def toggle_light(self) -> bool:
        if not self.is_alive:
            return False
        self.is_sleeping = not self.is_sleeping
        return True

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _can_act(self) -> bool:
        return self.is_alive and not self.is_sleeping

    def _update_attention(self) -> None:
        self.needs_attention = (
            self.hunger < 1.0
            or self.happiness < 1.0
            or self.poop_count >= 2
            or self.is_sick
        )

    @property
    def hunger_pct(self) -> int:
        return round(self.hunger / STAT_MAX * 100)

    @property
    def happiness_pct(self) -> int:
        return round(self.happiness / STAT_MAX * 100)

    @property
    def health_score(self) -> int:
        """Derived health 0-100 for display purposes."""
        if not self.is_alive:
            return 0
        score = 100
        score -= max(0, (4 - self.hunger) * 10)
        score -= max(0, (4 - self.happiness) * 5)
        score -= self.poop_count * 5
        score -= 20 if self.is_sick else 0
        score -= min(30, self.care_mistakes * 2)
        return max(0, score)
