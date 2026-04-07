#!/usr/bin/env python
"""Test translator loading."""

from PyQt5.QtCore import QTranslator
from pathlib import Path

qm_file = Path("app/i18n/app_hu.qm")

print(f"Testing translator for: {qm_file}")
print(f"File exists: {qm_file.exists()}")

if qm_file.exists():
    print(f"File size: {qm_file.stat().st_size} bytes")
    
    translator = QTranslator()
    result = translator.load(str(qm_file))
    
    print(f"Translator loaded: {result}")
    print(f"Translator is empty: {translator.isEmpty()}")
    
    if result:
        # Try to get a translation
        test_strings = [
            ("AddEditContactDialog", "Edit Contact"),
            ("DatabaseEditorDialog", "Name"),
        ]
        
        for context, source in test_strings:
            translated = translator.translate(context, source)
            print(f"  {context}.{source} -> {translated}")
else:
    print("ERROR: .qm file not found!")
