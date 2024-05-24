from os import environ as env

# URLs
PUBLIC_URL = env.get("HTV_BACKEND_PUBLIC_URL", "")
FRONTEND_PUBLIC_URL = env.get("HTV_FRONTEND_PUBLIC_URL", "")
FRONTEND_PRIVATE_URL = env.get("HTV_FRONTEND_PRIVATE_URL", "")

# Database
DATABASE_URI = env.get(
    "HTV_BACKEND_DATABASE_URI", "sqlite:////howtheyvote/database/database.sqlite3"
)
USERS_DATABASE_URI = env.get(
    "HTV_BACKEND_USERS_DATABASE_URI", "sqlite:////howtheyvote/database/users.sqlite3"
)

# File storage
FILES_DIR = env.get("HTV_BACKEND_FILES_DIR", "/howtheyvote/files")

# Meilisearch
MEILI_URL = env.get("MEILI_URL")
MEILI_MASTER_KEY = env.get("MEILI_MASTER_KEY")

# Request configuration
REQUEST_TIMEOUT = 10
REQUEST_SLEEP = 0.25

# Misc
CURRENT_TERM = 9
TIMEZONE = "Europe/Brussels"
WORKER_PROMETHEUS_PORT = 3000
SEARCH_INDEX_PREFIX = env.get("HTV_SEARCH_INDEX_PREFIX", None)
