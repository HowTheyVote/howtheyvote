from os import environ as env

# URLs
PUBLIC_URL = env.get("HTV_BACKEND_PUBLIC_URL", "")
FRONTEND_PUBLIC_URL = env.get("HTV_FRONTEND_PUBLIC_URL", "")
FRONTEND_PRIVATE_URL = env.get("HTV_FRONTEND_PRIVATE_URL", "")

# Database
DATABASE_URI = env.get(
    "HTV_BACKEND_DATABASE_URI", "sqlite:////howtheyvote/database/database.sqlite3"
)

# File storage
FILES_DIR = env.get("HTV_BACKEND_FILES_DIR", "/howtheyvote/files")

# Request configuration
REQUEST_TIMEOUT = 20
REQUEST_SLEEP = 0.25

# Misc
CURRENT_TERM = 10
TIMEZONE = "Europe/Brussels"
WORKER_PROMETHEUS_PORT = 3000
SEARCH_INDEX_PREFIX = env.get("HTV_SEARCH_INDEX_PREFIX", None)
SEARCH_INDEX_DIR = env.get("HTV_SEARCH_INDEX_DIR", "/howtheyvote/index")

# The Alpine package `xapian-core` installs stop word lists in this location
SEARCH_STOPWORDS_PATH = "/usr/share/xapian-core/stopwords/english.list"
