import os

# Root project directory
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Data storage paths
DATA_DIR = os.path.join(ROOT_DIR, "data")
PROFILES_DIR = os.path.join(DATA_DIR, "profiles")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

# Ensure folders exist
os.makedirs(PROFILES_DIR, exist_ok=True)

# Default Application Constants
DEFAULT_DELAY_SEC = 3
DEFAULT_BATCH_SIZE = 5
DEFAULT_BATCH_REST = 15
DEFAULT_WATCH_TIME = 10
DEFAULT_WINDOW_WIDTH = 1100
DEFAULT_WINDOW_HEIGHT = 700
