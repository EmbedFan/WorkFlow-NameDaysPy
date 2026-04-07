#!/usr/bin/env python
"""
Extract translatable strings from app source code.
Creates .ts (translation source) files for localization.
"""

import subprocess
import sys
from pathlib import Path

# Get all Python files in app directory
app_dir = Path("app")
py_files = list(app_dir.rglob("*.py"))

if not py_files:
    print("Error: No Python files found in app/ directory")
    sys.exit(1)

print(f"Found {len(py_files)} Python files")

# Build pylupdate5 command
cmd = [
    "pylupdate5",
    "-noobsolete",
    *[str(f) for f in py_files],
    "-ts",
    "app/i18n/app_en.ts"
]

print(f"Running: {' '.join(cmd)}")
result = subprocess.run(cmd)
sys.exit(result.returncode)
