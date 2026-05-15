"""Constants for the Tamagotchi integration."""

DOMAIN = "tamagotchi"

PLATFORMS = ["sensor", "binary_sensor", "button", "image"]

STORAGE_KEY = "tamagotchi"
STORAGE_VERSION = 1

CONF_NAME = "name"

# Dispatcher signals
SIGNAL_STATE_UPDATED = f"{DOMAIN}_state_updated_{{entry_id}}"
SIGNAL_ANIMATE = f"{DOMAIN}_animate_{{entry_id}}"

# Life stages
STAGE_EGG = "egg"
STAGE_BABY = "baby"
STAGE_CHILD = "child"
STAGE_TEEN = "teen"
STAGE_ADULT = "adult"
STAGE_SENIOR = "senior"
STAGE_DEAD = "dead"

STAGES = [STAGE_EGG, STAGE_BABY, STAGE_CHILD, STAGE_TEEN, STAGE_ADULT, STAGE_SENIOR]

# Hours at each stage before evolution to the next
STAGE_HOURS = {
    STAGE_EGG: 1,
    STAGE_BABY: 3,
    STAGE_CHILD: 10,
    STAGE_TEEN: 20,
    STAGE_ADULT: 72,
}

# Game tick (minutes)
TICK_MINUTES = 5
ANIMATE_SECONDS = 2

# Hunger/happiness range
STAT_MAX = 4.0
STAT_MIN = 0.0
