import os

# Project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Logs directory
LOGS_DIR = os.path.join(PROJECT_ROOT, "var", "logs")

# Config directory
CONFIG_DIR = os.path.join(PROJECT_ROOT, "config")

# Logging config file
LOGGING_CONFIG_FILE = os.path.join(CONFIG_DIR, "logging.ini")