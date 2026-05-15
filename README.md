# Tamagotchi for Home Assistant

A virtual pet that lives inside Home Assistant. Care for it using sensors and buttons — watch it grow on a 16×16 LCD-style display.

## Features

- **16×16 pixel LCD display** rendered as an animated image entity
- **Life stages**: Egg → Baby → Child → Teen → Adult → Senior → (death)
- **Stats exposed as sensors**: hunger, happiness, discipline, weight, age, poop count, care mistakes
- **Boolean sensors**: is_sick, is_sleeping, needs_attention, is_alive
- **Action buttons**: Feed Meal, Feed Snack, Play, Clean, Medicate, Discipline, Toggle Light
- **Persistent state** — survives HA restarts
- **Automatic sleep** based on real-world time (9 PM – 9 AM by default)
- **Evolution quality** influenced by care mistakes and discipline

## Installation via HACS

1. In HACS → Integrations → ⋮ → Custom repositories
2. Add `https://github.com/janmeermans/ha-tamagotchi` as **Integration**
3. Install **Tamagotchi** and restart HA
4. Settings → Devices & Services → Add Integration → **Tamagotchi**
5. Give your pet a name and enjoy

## Manual Installation

Copy `custom_components/tamagotchi/` into your HA `custom_components/` directory and restart.

## Dashboard

Add the **image entity** (`image.tamagotchi_<name>_display`) to a card to see your pet.  
Use **button cards** linked to the button entities for feeding, playing, and cleaning.

A minimal Lovelace card config:

```yaml
type: vertical-stack
cards:
  - type: picture-entity
    entity: image.tamagotchi_tama_display
    show_name: false
    show_state: false
  - type: glance
    entities:
      - entity: sensor.tamagotchi_tama_hunger
      - entity: sensor.tamagotchi_tama_happiness
      - entity: sensor.tamagotchi_tama_stage
      - entity: binary_sensor.tamagotchi_tama_is_sick
  - type: horizontal-stack
    cards:
      - type: button
        entity: button.tamagotchi_tama_feed_meal
      - type: button
        entity: button.tamagotchi_tama_play
      - type: button
        entity: button.tamagotchi_tama_clean
```

## Game Mechanics

| Stat | Range | Notes |
|------|-------|-------|
| Hunger | 0–4 hearts | Decreases ~1/30 min; 0 = starvation risk |
| Happiness | 0–4 hearts | Decreases ~1/60 min |
| Weight | 1–99 | Meals +1, snacks +2, playing -1 |
| Discipline | 0–100 % | Raised by the Discipline button |
| Poop | 0–4 piles | Auto-cleans needed; piles ≥3 → sick risk |

Neglecting the pet (hunger=0, happiness=0, or uncleaned poop) increments **care mistakes**, which affects evolution quality.
