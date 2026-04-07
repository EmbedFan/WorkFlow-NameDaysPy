#!/usr/bin/env python
"""
Convert .ts translation files to JSON format for Python-based translation system.
This avoids issues with Qt .qm binary format and is easier to debug.
"""

import json
import xml.etree.ElementTree as ET
from pathlib import Path
import sys

def ts_to_json(ts_file: str, json_file: str = None) -> bool:
    """Convert .ts file to JSON format."""
    ts_path = Path(ts_file)
    
    if json_file is None:
        json_file = ts_path.with_suffix('.json')
    
    try:
        # Parse .ts XML file
        tree = ET.parse(ts_file)
        root = tree.getroot()
        
        # Extract language
        language = root.get('language', 'en_US')
        
        # Build translation dictionary
        translations = {}
        total_messages = 0
        translated_messages = 0
        
        for context_elem in root.findall('context'):
            context_name_elem = context_elem.find('name')
            context_name = context_name_elem.text if context_name_elem is not None and context_name_elem.text else ""
            
            if context_name not in translations:
                translations[context_name] = {}
            
            for message in context_elem.findall('message'):
                source_elem = message.find('source')
                trans_elem = message.find('translation')
                
                if source_elem is not None:
                    source = source_elem.text or ""
                    translation = ""
                    
                    if trans_elem is not None and trans_elem.text:
                        translation = trans_elem.text
                        translated_messages += 1
                    
                    total_messages += 1
                    
                    # Store translation
                    translations[context_name][source] = translation
        
        # Write JSON file
        output = {
            "language": language,
            "total_messages": total_messages,
            "translated_messages": translated_messages,
            "translations": translations
        }
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        file_size = Path(json_file).stat().st_size
        print(f"✓ Converted: {ts_file}")
        print(f"  Language: {language}")
        print(f"  Total messages: {total_messages}")
        print(f"  Translated: {translated_messages}")
        print(f"  Output: {json_file} ({file_size} bytes)")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to convert {ts_file}: {e}")
        return False

def main():
    """Convert all .ts files to JSON."""
    i18n_dir = Path("app/i18n")
    
    if not i18n_dir.exists():
        print("Error: app/i18n directory not found")
        return False
    
    ts_files = sorted(i18n_dir.glob("*.ts"))
    
    if not ts_files:
        print("Error: No .ts files found in app/i18n/")
        return False
    
    print(f"Found {len(ts_files)} translation files:")
    for ts_file in ts_files:
        print(f"  - {ts_file}")
    
    print("\n" + "="*60)
    print("Converting translations to JSON format...\n")
    
    all_ok = True
    for ts_file in ts_files:
        json_file = ts_file.with_suffix('.json')
        result = ts_to_json(str(ts_file), str(json_file))
        if not result:
            all_ok = False
        print()
    
    print("="*60)
    if all_ok:
        print("✓ All translations converted successfully!")
        print("\nNote: You can now delete the .qm files (they're not used)")
        return True
    else:
        print("✗ Some translations failed to convert.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
