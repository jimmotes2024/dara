#!/usr/bin/env python3
"""
Dara Config - Centralized configuration for all Dara components.
Single source of truth for paths, settings, and constants.
"""

from pathlib import Path

# Base directory - all Dara files live here
BASE_DIR = Path("/Users/jimmotes/dara")

# Core file paths
PATHS = {
    'soul': BASE_DIR / 'DARA_SOUL.md',
    'memory': BASE_DIR / 'DARA_MEMORY.md',
    'journal': BASE_DIR / 'DARA_JOURNAL.md',
    'parking': BASE_DIR / 'DARA_PARKING_LOT.md',
    'startup': BASE_DIR / 'DARA_STARTUP.md',
    'user': BASE_DIR / 'DARA_USER.md',
    'vector_index': BASE_DIR / 'dara_memory.index',
    'vector_meta': BASE_DIR / 'dara_memory_meta.json',
    'chroma_path': Path.home() / '.dara' / 'chroma_db',
}

# Settings
SETTINGS = {
    'default_search_k': 5,
    'journal_preview_chars': 800,
    'rich_theme': 'blue',
    'auto_canary_on_start': True,
    'heartbeat_default_nap': True,
    'version': '0.2.0',  # Updated with CLI improvements
}

def get_path(key):
    """Get a configured path by key."""
    return PATHS.get(key)

def get_setting(key):
    """Get a setting by key."""
    return SETTINGS.get(key)

if __name__ == '__main__':
    print("Dara Config loaded.")
    print(f"Base directory: {BASE_DIR}")
    print(f"Version: {SETTINGS['version']}")
