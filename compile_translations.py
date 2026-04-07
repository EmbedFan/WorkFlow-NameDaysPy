#!/usr/bin/env python
"""
Compile .ts translation files to .qm binary format.
Uses Qt Linguist tools to properly compile translations.
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

def find_lrelease():
    """Find lrelease executable in common locations."""
    # Possible locations
    possibilities = [
        "lrelease",
        "lrelease.exe",
        os.path.join(os.environ.get('QTDIR', ''), 'bin', 'lrelease'),
        os.path.join(os.environ.get('QTDIR', ''), 'bin', 'lrelease.exe'),
    ]
    
    for cmd in possibilities:
        if shutil.which(cmd):
            return cmd
    
    return None

def compile_ts_to_qm(ts_file):
    """Compile a .ts file to .qm using lrelease tool."""
    ts_path = Path(ts_file)
    qm_path = ts_path.with_suffix('.qm')
    
    # Find lrelease
    lrelease = find_lrelease()
    
    if lrelease:
        try:
            print(f"Using lrelease: {lrelease}")
            result = subprocess.run([
                lrelease,
                str(ts_path)
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and qm_path.exists():
                size = qm_path.stat().st_size
                print(f"✓ Successfully compiled: {ts_file}")
                print(f"  Output: {qm_path} ({size} bytes)")
                return True
            else:
                print(f"✗ lrelease failed or no output")
                if result.stderr:
                    print(f"  Error: {result.stderr}")
        except Exception as e:
            print(f"✗ Error: {e}")
    else:
        print(f"⚠ lrelease not found. Install it with:")
        print(f"  pip install --upgrade pyqt5-tools")
        print(f"  OR on Windows: choco install qt5-base")
    
    return False

def main():
    """Compile all .ts files in app/i18n directory."""
    i18n_dir = Path("app/i18n")
    ts_files = sorted(i18n_dir.glob("*.ts"))
    
    if not ts_files:
        print("Error: No .ts files found in app/i18n/")
        sys.exit(1)
    
    print(f"Found {len(ts_files)} translation files:")
    for ts_file in ts_files:
        print(f"  - {ts_file}")
    
    print("\n" + "="*60)
    print("Compiling translations...\n")
    
    # Check if lrelease is available
    lrelease = find_lrelease()
    if not lrelease:
        print("ERROR: lrelease tool not found!")
        print("\nTo fix this, install Qt Linguist tools:")
        print("\n  Option 1 - Using pip (recommended for Python):")
        print("  -----------")
        print("  pip install --upgrade pyqt5-tools")
        print("  pip install lrelease")
        print("\n  Option 2 - Using Chocolatey (Windows):")
        print("  -----------")
        print("  choco install qt5-base")
        print("\n  Option 3 - Using System Qt Installation:")
        print("  -----------")
        print("  Download from: https://www.qt.io/download-open-source")
        print("  Add Qt bin folder to PATH")
        print("\nAfter installation, run this script again.")
        sys.exit(1)
    
    results = []
    for ts_file in ts_files:
        print(f"Compiling {ts_file.name}...")
        result = compile_ts_to_qm(str(ts_file))
        results.append((ts_file.name, result))
        print()
    
    print("="*60)
    print("Compilation Results:")
    print("="*60)
    for filename, success in results:
        status = "✓ OK" if success else "✗ FAILED"
        print(f"{status}: {filename}")
    
    if all(r[1] for r in results):
        print("\n✓ All translations compiled successfully!")
        sys.exit(0)
    else:
        print("\n✗ Some translations failed to compile.")
        sys.exit(1)

if __name__ == "__main__":
    main()
