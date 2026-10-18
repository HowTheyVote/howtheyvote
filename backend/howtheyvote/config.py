from os import environ as env

ENV = env.get("HTV_ENV", "prod")

# URLs
PUBLIC_URL = env.get("HTV_BACKEND_PUBLIC_URL", "")
FRONTEND_PUBLIC_URL = env.get("HTV_FRONTEND_PUBLIC_URL", "")
CADDY_PRIVATE_URL = env.get("HTV_CADDY_PRIVATE_URL", "")

# Database
DATABASE_URI = env.get(
    "HTV_BACKEND_DATABASE_URI", "sqlite:////howtheyvote/database/database.sqlite3"
)
SCOWL_DATABASE_URI = "sqlite:////usr/local/share/esdb/scowl.db"

# File storage
FILES_DIR = env.get("HTV_BACKEND_FILES_DIR", "/howtheyvote/files")

# Request configuration
REQUEST_TIMEOUT = float(env.get("HTV_BACKEND_REQUEST_TIMEOUT", 20))
REQUEST_SLEEP = float(env.get("HTV_BACKEND_REQUEST_SLEEP", 2.5))
TOKEN_RENEWAL_SLEEP = 600

# Headless Chromium
CHROMIUM_HOST = "chromium"
CHROMIUM_PORT = 9222

# Misc
CURRENT_TERM = 10
TIMEZONE = "Europe/Brussels"

# Search
SEARCH_INDEX_PREFIX = env.get("HTV_SEARCH_INDEX_PREFIX", None)
SEARCH_INDEX_DIR = env.get("HTV_SEARCH_INDEX_DIR", "/howtheyvote/index")

# Number of documents that are at least checked for every search query. A higher
# number results in better estimates of the total result count, but also increases
# query processing time. See: https://trac.xapian.org/wiki/FAQ/MoreAccurateEstimates
SEARCH_CHECK_AT_LEAST = 1_000

# Setting `SEARCH_CHECK_AT_LEAST` to a high value can lead to longer query processing
# times. Search results will be returned after `SEARCH_TIME_LIMIT` seconds, even if
# fewer than `SEARCH_CHECK_AT_LEAST` documents have been checked.
SEARCH_TIME_LIMIT = 3

# The Alpine package `xapian-core` installs stop word lists in this location
SEARCH_STOPWORDS_PATH = "/usr/local/share/xapian-core/stopwords/english.list"

# List of synonym pairs. Synonyms are unidirectional. For example, given the synonym
# `corona:covid`, searching for `corona` would also find votes containing `covid`,
# but not the other way around.
SEARCH_SYNONYMS = env.get("HTV_SEARCH_SYNONYMS", "")

# Pushover
PUSHOVER_API_TOKEN = env.get("PUSHOVER_API_TOKEN")
PUSHOVER_USER_KEY = env.get("PUSHOVER_USER_KEY")
