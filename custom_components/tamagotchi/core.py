"""Tamagotchi game logic — no HA dependencies."""
from __future__ import annotations

import random
from datetime import datetime

from .const import (
    STAGE_EGG, STAGE_BABY, STAGE_CHILD, STAGE_TEEN,
    STAGE_ADULT, STAGE_ELDER, STAGE_DEAD,
    STAGES, STAGE_HOURS, STAT_MAX, CREATURE_TYPES,
)


class TamagotchiCore:
    """Pure-Python virtual pet state machine.

    All stats (hunger, happiness, health) use a 0.0–10.0 float range.
    Discipline uses a 0–10 integer range, starting at 0.
    Values are displayed to the user as integers (floor).
    """

    def __init__(self, name: str = "Tama") -> None:
        self.name: str = name

        # --- Life state ---
        self.stage: str = STAGE_EGG
        self.age_hours: float = 0.0
        self.stage_start_age: float = 0.0

        # --- Stats (0.0 – 10.0) ---
        self.hunger: float    = STAT_MAX   # 10 = full
        self.happiness: float = STAT_MAX   # 10 = happy
        self.health: float    = STAT_MAX   # 10 = healthy; 0 = death

        # --- Integer stats ---
        self.discipline: int = 0           # 0–10, starts at 0
        self.weight: int     = 5

        # --- Status flags ---
        self.poop_count: int     = 0
        self.care_mistakes: int  = 0
        self.is_sick: bool       = False
        self.is_sleeping: bool   = False
        self.is_alive: bool      = True
        self.needs_attention: bool = False

        # --- Creature identity (assigned when egg hatches) ---
        self.creature_type: str = "dog"    # "dog" | "cat"

        # --- Animation ---
        self.animation_frame: int = 0

        # --- Sleep schedule ---
        self.sleep_start_hour: int = 21
        self.sleep_end_hour: int   = 9

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
    # Game tick  (called every TICK_MINUTES minutes)
    # ------------------------------------------------------------------

    def tick(self, elapsed_minutes: float) -> list[str]:
        """Advance the game clock. Returns a list of event strings."""
        if not self.is_alive:
            return []

        events: list[str] = []
        now_hour = datetime.now().hour

        # ---- Auto sleep ----
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

        # Sleeping pauses all decay
        if self.is_sleeping:
            return events

        # ---- Age ----
        self.age_hours += elapsed_minutes / 60.0

        # ---- Hunger: −1 per hour ----
        self.hunger = max(0.0, self.hunger - elapsed_minutes / 60.0)

        # ---- Happiness: −0.5 per hour (double when sick) ----
        happiness_rate = 1.0 if self.is_sick else 0.5
        self.happiness = max(0.0, self.happiness - happiness_rate * elapsed_minutes / 60.0)

        # ---- Health from poop: −1 per 2 hours per pile ----
        if self.poop_count > 0:
            self.health = max(
                0.0,
                self.health - self.poop_count * elapsed_minutes / 120.0,
            )

        # ---- Poop: 1 pile every ~6 hours, max 3 ----
        if self.poop_count < 3:
            poop_prob = elapsed_minutes / (6.0 * 60.0)
            if random.random() < poop_prob:
                self.poop_count += 1
                events.append("pooped")

        # ---- Sickness: ~once per week ----
        if not self.is_sick and self.stage not in (STAGE_EGG, STAGE_BABY):
            sick_prob = elapsed_minutes / (7.0 * 24.0 * 60.0)
            if random.random() < sick_prob:
                self.is_sick = True
                events.append("got_sick")

        # ---- Attention flag ----
        wants = (
            self.hunger < 2.0
            or self.happiness < 2.0
            or self.poop_count >= 2
            or self.is_sick
        )
        if wants and not self.needs_attention:
            self.needs_attention = True
            events.append("needs_attention")

        # ---- Care mistakes: incremented when ignored while critical ----
        if self.needs_attention and (self.hunger < 1.0 or self.happiness < 1.0):
            self.care_mistakes += 1

        # ---- Death: health depleted ----
        if self.health <= 0.0:
            self._die(events)
            return events

        # ---- Death: starvation ----
        if self.hunger <= 0.0 and self.age_hours > 1.0:
            if random.random() < 0.25 * (elapsed_minutes / 60.0):
                self._die(events)
                return events

        # ---- Evolution ----
        self._check_evolution(events)

        return events

    def _check_evolution(self, events: list[str]) -> None:
        if self.stage == STAGE_DEAD or self.stage not in STAGE_HOURS:
            return
        stage_age = self.age_hours - self.stage_start_age
        if stage_age < STAGE_HOURS[self.stage]:
            return

        if self.stage == STAGE_ELDER:
            # Natural death at end of elder stage
            self._die(events)
            events.append("natural_death")
            return

        idx = STAGES.index(self.stage)
        if idx + 1 < len(STAGES):
            old = self.stage
            self.stage = STAGES[idx + 1]
            self.stage_start_age = self.age_hours

            # Assign creature type when hatching from egg
            if old == STAGE_EGG:
                self.creature_type = random.choice(CREATURE_TYPES)

            events.append(f"evolved:{old}:{self.stage}")

    def _die(self, events: list[str]) -> None:
        self.is_alive = False
        self.stage = STAGE_DEAD
        events.append("died")

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def feed_meal(self) -> bool:
        """Meal: hunger +2, weight +1."""
        if not self._can_act() or self.stage == STAGE_EGG:
            return False
        if self.hunger >= STAT_MAX:
            return False
        self.hunger = min(STAT_MAX, self.hunger + 2.0)
        self.weight = min(99, self.weight + 1)
        self._update_attention()
        return True

    def feed_snack(self) -> bool:
        """Snack: hunger +1, happiness +2, health −1, weight +1."""
        if not self._can_act() or self.stage == STAGE_EGG:
            return False
        self.hunger    = min(STAT_MAX, self.hunger    + 1.0)
        self.happiness = min(STAT_MAX, self.happiness + 2.0)
        self.health    = max(0.0,      self.health    - 1.0)
        self.weight    = min(99, self.weight + 1)
        self._update_attention()
        return True

    def play(self) -> bool:
        """Play: happiness +1, weight −5 %."""
        if not self._can_act() or self.stage == STAGE_EGG:
            return False
        self.happiness = min(STAT_MAX, self.happiness + 1.0)
        self.weight    = max(1, int(self.weight * 0.95))
        self._update_attention()
        return True

    def clean(self) -> bool:
        """Remove all poop piles."""
        if not self.is_alive or self.poop_count == 0:
            return False
        self.poop_count = 0
        self._update_attention()
        return True

    def medicate(self) -> bool:
        """Cure sickness; restore 2 health."""
        if not self.is_alive or not self.is_sick:
            return False
        self.is_sick = False
        self.health  = min(STAT_MAX, self.health + 2.0)
        self._update_attention()
        return True

    def do_discipline(self) -> bool:
        """Discipline +1 (max 10)."""
        if not self._can_act():
            return False
        self.discipline = min(10, self.discipline + 1)
        return True

    def toggle_light(self) -> bool:
        """Manually override sleep state."""
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
            self.hunger    < 2.0
            or self.happiness < 2.0
            or self.poop_count >= 2
            or self.is_sick
        )

    # --- Display-friendly integer accessors ---

    @property
    def hunger_int(self) -> int:
        return int(self.hunger)

    @property
    def happiness_int(self) -> int:
        return int(self.happiness)

    @property
    def health_int(self) -> int:
        return int(self.health)
