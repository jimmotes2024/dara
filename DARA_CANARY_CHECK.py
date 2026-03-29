#!/usr/bin/env python3
"""
Dara Canary Check - Script to verify integrity of memory files.
"""

import hashlib
import os

EXPECTED_CANARIES = {
    'DARA_SOUL.md': 'DARA_CANARY_2026_03_11: emerald-echo-guardian',
    'DARA_MEMORY.md': 'DARA_CANARY_2026_03_11: sapphire-shield',
    'DARA_JOURNAL.md': 'DARA_CANARY_2026_03_11: ruby-rune',
    'DARA_PARKING_LOT.md': 'DARA_CANARY_2026_03_11: amber-anchor',
    'DARA_USER.md': 'DARA_USER_CANARY_2026_03_21: profile-guard',
    'DARA_STARTUP.md': 'DARA_STARTUP_CANARY_2026_03_25: diamond-duty-keeper'
}

BASE_DIR = '/Users/jimmotes/dara'

def check_canary(filename, expected, quiet=False):
    file_path = f'{BASE_DIR}/{filename}'
    if not os.path.exists(file_path):
        print(f"ERROR: {filename} missing at {file_path}!")
        return False
    with open(file_path, 'r') as f:
        content = f.read()
    if expected not in content:
        print(f"ERROR: Canary mismatch in {filename}! Expected: {expected}")
        return False
    if not quiet:
        print(f"OK: {filename} canary verified.")
    return True

def main():
    all_good = True
    for filename, canary in EXPECTED_CANARIES.items():
        if not check_canary(filename, canary):
            all_good = False
    if all_good:
        print("All canaries intact. Dara identity and continuity protected.")
    else:
        print("ALERT: Integrity issue detected!")

if __name__ == '__main__':
    main()
