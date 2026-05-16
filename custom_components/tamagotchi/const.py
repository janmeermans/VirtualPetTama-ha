"""Constants for the Tamagotchi integration."""

DOMAIN = "tamagotchi"

PLATFORMS = ["sensor", "binary_sensor", "button", "image", "select"]

STORAGE_KEY = "tamagotchi"
STORAGE_VERSION = 1

CONF_NAME = "name"

# Dispatcher signals
SIGNAL_STATE_UPDATED = f"{DOMAIN}_state_updated_{{entry_id}}"
SIGNAL_ANIMATE = f"{DOMAIN}_animate_{{entry_id}}"

# ---------------------------------------------------------------------------
# Life stages
# ---------------------------------------------------------------------------
STAGE_EGG    = "egg"
STAGE_BABY   = "baby"
STAGE_CHILD  = "child"
STAGE_TEEN   = "teen"
STAGE_ADULT  = "adult"
STAGE_ELDER  = "elder"
STAGE_DEAD   = "dead"

STAGES = [STAGE_EGG, STAGE_BABY, STAGE_CHILD, STAGE_TEEN, STAGE_ADULT, STAGE_ELDER]

# Hours spent at each stage before evolving to the next
STAGE_HOURS = {
    STAGE_EGG:   1,       # 1 hour
    STAGE_BABY:  6,       # 6 hours
    STAGE_CHILD: 120,     # 5 days
    STAGE_TEEN:  120,     # 5 days
    STAGE_ADULT: 360,     # 15 days
    STAGE_ELDER: 120,     # 5 days  → then natural death
}

# ---------------------------------------------------------------------------
# Creature types
# ---------------------------------------------------------------------------
CREATURE_TYPES = ["dog", "cat"]

# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------
STAT_MAX = 10.0
STAT_MIN = 0.0

TICK_MINUTES  = 5    # game tick interval
ANIMATE_SECONDS = 2  # animation frame interval

# ---------------------------------------------------------------------------
# Colour palettes  {name: (bg_rgb, dark_rgb, mid_rgb, border_rgb)}
# ---------------------------------------------------------------------------
PALETTES: dict[str, dict[str, tuple]] = {
    "classic": {
        "bg":     (155, 188,  15),   # Game Boy green
        "dark":   ( 15,  56,  15),
        "mid":    ( 48,  98,  48),
        "border": ( 80, 120,  10),
    },
    "amber": {
        "bg":     (255, 210, 127),   # retro amber CRT
        "dark":   (107,  45,   0),
        "mid":    (204, 122,   0),
        "border": (139,  69,   0),
    },
    "blue": {
        "bg":     (160, 216, 240),   # ocean / cool blue
        "dark":   ( 13,  48,  80),
        "mid":    ( 64, 144, 184),
        "border": ( 26,  64,  96),
    },
    "sakura": {
        "bg":     (255, 214, 231),   # cherry blossom pink
        "dark":   ( 92,  26,  60),
        "mid":    (194,  90, 138),
        "border": (139,  58,  96),
    },
}

PALETTE_NAMES   = list(PALETTES.keys())
DEFAULT_PALETTE = "classic"
