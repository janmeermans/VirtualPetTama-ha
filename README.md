# Tamagotchi for Home Assistant

A virtual pet that lives inside Home Assistant. Care for it using sensors and buttons — watch it grow on a 16×16 LCD-style display.

## Features

- **16×16 pixel LCD display** rendered as an animated image entity (144×144 px at 8× scale)
- **Two creature types** — Dog or Cat, randomly chosen when the egg hatches
- **Life stages**: Egg → Baby → Child → Teen → Adult → Elder → (natural death)
- **Stats on a 0–10 scale**: hunger, happiness, health, discipline
- **Sensors**: hunger, happiness, health, discipline, weight, age, stage, creature type, poop count, care mistakes
- **Boolean sensors**: is_alive, is_sick, is_sleeping, needs_attention
- **Action buttons**: Feed Meal, Feed Snack, Play, Clean, Medicate, Discipline, Toggle Light
- **4 colour palettes**: Classic (Game Boy), Amber (CRT), Blue (Ocean), Sakura (Cherry) — switchable live via a Select entity
- **Persistent state** — survives HA restarts
- **Automatic sleep** based on real-world time (9 PM – 9 AM by default)

## Installation via HACS

1. In HACS → Integrations → ⋮ → Custom repositories
2. Add `https://github.com/janmeermans/VirtualPetTama-ha` as **Integration**
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
      - entity: sensor.tamagotchi_tama_health
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

<img width="1603" height="1083" alt="image" src="https://github.com/user-attachments/assets/11423573-5731-47b7-923b-03f016c4aa1b" />


## Game Mechanics

### Lifecycle

| Stage  | Duration | Notes |
|--------|----------|-------|
| Egg    | 1 hour   | Hatches into Dog or Cat (random) |
| Baby   | 6 hours  | Shared sprite for both creatures |
| Child  | 5 days   | Sprites diverge: Dog vs Cat |
| Teen   | 5 days   | Dog gains hair tuft; Cat gains taller ears |
| Adult  | 15 days  | Peak stage |
| Elder  | 5 days   | Dies naturally at the end |

**Total natural lifespan:** ~30 days 7 hours.

### Stats (all 0–10)

| Stat       | Start | Meaning |
|------------|-------|---------|
| Hunger     | 10    | 10 = full, 0 = starving |
| Happiness  | 10    | 10 = happy, 0 = miserable |
| Health     | 10    | 10 = healthy, 0 = death |
| Discipline | 0     | Starts at 0 for each new creature |

### Stat Decay (while awake)

| Stat      | Rate                    |
|-----------|-------------------------|
| Hunger    | −1 per hour             |
| Happiness | −0.5 per hour (double when sick) |
| Health    | −1 per 2 h × poop piles |

> **Sleep pauses all decay.**

### Actions

| Button       | Effect |
|--------------|--------|
| Feed Meal    | Hunger +2, Weight +1 |
| Feed Snack   | Hunger +1, Happiness +2, Health −1, Weight +1 |
| Play         | Happiness +1, Weight −5 % |
| Clean        | Removes all poop piles |
| Medicate     | Cures sickness, Health +2 |
| Discipline   | Discipline +1 (max 10) |
| Toggle Light | Manually force sleep / wake |

See [GAME_MECHANICS.md](GAME_MECHANICS.md) for the full reference.
