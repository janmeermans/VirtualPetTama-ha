# Tamagotchi — Game Mechanics Reference

## Lifecycle

| Stage  | Duration   | Notes |
|--------|-----------|-------|
| Egg    | 1 hour    | Hatches into random creature type (Dog or Cat) |
| Baby   | 6 hours   | Very short juvenile phase |
| Child  | 5 days    | First interactive stage |
| Teen   | 5 days    | Growing phase |
| Adult  | 15 days   | Peak lifespan |
| Elder  | 5 days    | Final stage; dies naturally at end |
| Dead   | —         | Tombstone shown; all actions disabled |

**Total natural lifespan:** ~30 days 7 hours from birth.

---

## Stats (all 0 – 10)

| Stat       | Start | Max | Meaning |
|------------|-------|-----|---------|
| Hunger     | 10    | 10  | 10 = full, 0 = starving |
| Happiness  | 10    | 10  | 10 = happy, 0 = miserable |
| Health     | 10    | 10  | 10 = healthy, 0 = death |
| Discipline | 0     | 10  | Starts at 0 for every new creature |

---

## Stat Decay (while awake)

| Stat      | Rate                   | Per 5-min tick |
|-----------|------------------------|----------------|
| Hunger    | −1 per hour            | −0.083         |
| Happiness | −0.5 per hour          | −0.042         |
| Health    | −1 per 2 h × poop count| −0.042 × poops |

> **Sleep pauses all decay.** No stat changes while the creature sleeps.

---

## Actions

### Feed Meal
- Hunger **+2** (capped at 10)
- Weight **+1**

### Feed Snack
- Hunger **+1** (capped at 10)
- Happiness **+2** (capped at 10)
- Health **−1** (snacks are junk food)
- Weight **+1**

### Play
- Happiness **+1** (capped at 10)
- Weight **−5 %** (rounded down)

### Clean
- Removes all poop piles
- Prevents poop-related health loss

### Medicate
- Cures sickness
- Restores **+2 Health** (capped at 10)
- Only available when the creature is sick

### Discipline
- Discipline **+1** (capped at 10)

### Toggle Light
- Manually forces sleep / wake outside automatic hours

---

## Poop

- **1 pile appears every 6 hours** (random probability per tick)
- **Maximum: 3 piles**
- Each pile present → **−1 Health per 2 hours** (cumulative)
  - 1 pile: −0.5 Health/hour
  - 2 piles: −1.0 Health/hour
  - 3 piles: −1.5 Health/hour
- Use **Clean** to remove all piles immediately

---

## Sickness

- Occurs **randomly**, approximately **once per week** on average
- Probability per tick ≈ 5 / (7 × 24 × 60) ≈ 0.05 % per 5-min tick
- While sick: Happiness decays at **double** the normal rate
- Cured by: **Medicate** (+2 Health restored)
- Shown on display: **X-eyes + sad mouth** (built into sprite)

---

## Sleep

| Mode | Trigger |
|------|---------|
| Automatic | 21:00 – 09:00 (server local time) |
| Manual | Toggle Light button (overrides schedule) |

While sleeping:
- **All stat decay paused**
- Display switches to **inverted colour scheme** (dark background, light creature)
- **ZZZ** overlay shown in top-right corner
- Poop and attention overlays hidden

---

## Attention

The creature raises a **!** flag (right edge of display) when:
- Hunger < 2 hearts  
- Happiness < 2 hearts  
- 2 or more poop piles present  
- Creature is sick

Ignoring the flag while hunger or happiness is ≤ 0 increments **Care Mistakes**, which can affect evolution quality.

---

## Creature Types

Two creature types exist; the type is **randomly chosen** when the egg hatches:

| Type | Distinguishing features |
|------|------------------------|
| **Dog** | Floppy ears, hair tuft (teen+), arms |
| **Cat** | Pointed ears, visible tail |

Both share the same **Egg** and **Baby** sprites. From **Child** onwards the sprites diverge.

---

## Evolution

Evolution to the next stage is automatic when the current stage's time elapses. The transition from **Elder** to **Dead** is a natural death.

Evolution quality (future feature): influenced by discipline level and care mistakes accumulated during the creature's life.

---

## Death

The creature dies if any of the following occur:

| Cause | Condition |
|-------|-----------|
| Starvation | Hunger = 0 for an extended period (25 % chance per hour) |
| Illness neglect | Health reaches 0 |
| Old age | Elder stage lifecycle completes (natural death) |

---

## Display & Palettes

The 16 × 16 LCD display is rendered at 8 × scale (144 × 144 px). Four colour palettes are available:

| Name    | Background      | Body colour     | Theme |
|---------|----------------|-----------------|-------|
| Classic | `#9bbc0f` green| `#0f380f` dark  | Game Boy original |
| Amber   | `#ffd27f` amber| `#6b2d00` brown | Retro CRT |
| Blue    | `#a0d8f0` sky  | `#0d3050` navy  | Ocean |
| Sakura  | `#ffd6e7` pink | `#5c1a3c` rose  | Cherry blossom |
