#!/usr/bin/env python3
"""
Release Package Creator for Name Days Monitoring App [REQ-0066]

This tool manages file associations between install/ and source files.
It can:
  - List all file associations
  - Verify files match between install/ and source
  - Sync files from source to install/
  - Create release packages
  - Generate detailed reports

Usage:
  python tools/create_release.py list         # List all file associations
  python tools/create_release.py verify       # Verify files match
  python tools/create_release.py sync         # Sync from source to install/
  python tools/create_release.py package      # Create release package
  python tools/create_release.py report       # Generate detailed report
"""

import sys
import hashlib
import shutil
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class FileMapping:
    """File association mapping."""
    install_path: str  # Path in install/
    source_path: str   # Path in source (root)
    file_type: str     # 'py', 'csv', 'ts', 'qm', 'qss', 'png', 'ico', 'json', 'md', 'bat', 'vbs'.
    module: str        # 'root', 'app', 'resources', 'i18n', etc.


class ReleaseManager:
    """Manages release package creation and file synchronization."""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.install_dir = self.root_dir / "install"
        self.source_dir = self.root_dir
        
        # Define all 47 file associations discovered in install/
        self.file_mappings = self._build_file_mappings()
    
    def _build_file_mappings(self) -> List[FileMapping]:
        """Build complete file mapping from install/ to source files."""
        mappings = [
            # ROOT FILES (4)
            FileMapping("main.py", "main.py", "py", "root"),
            FileMapping("setup.py", "setup.py", "py", "root"),
            FileMapping("README.md", "README.md", "md", "root"),
            FileMapping("requirements.txt", "requirements.txt", "txt", "root"),
            FileMapping("run_hidden.vbs", "run_hidden.vbs", "vbs", "root"),
            FileMapping("run_hidden.bat", "run_hidden.bat", "bat", "root"),
            
            # APP CORE (5)
            FileMapping("app/__init__.py", "app/__init__.py", "py", "app"),
            FileMapping("app/constants.py", "app/constants.py", "py", "app"),
            FileMapping("app/exceptions.py", "app/exceptions.py", "py", "app"),
            FileMapping("app/main.py", "app/main.py", "py", "app"),
            FileMapping("app/types.py", "app/types.py", "py", "app"),
            
            # APP CORE MODULE (4)
            FileMapping("app/core/__init__.py", "app/core/__init__.py", "py", "core"),
            FileMapping("app/core/monitoring_engine.py", "app/core/monitoring_engine.py", "py", "core"),
            FileMapping("app/core/notification_manager.py", "app/core/notification_manager.py", "py", "core"),
            FileMapping("app/core/notification_queue.py", "app/core/notification_queue.py", "py", "core"),
            
            # APP I18N MODULE (6)
            FileMapping("app/i18n/__init__.py", "app/i18n/__init__.py", "py", "i18n"),
            FileMapping("app/i18n/translator.py", "app/i18n/translator.py", "py", "i18n"),
#            FileMapping("app/i18n/app_en.ts", "app/i18n/app_en.ts", "ts", "i18n"),
#            FileMapping("app/i18n/app_hu.ts", "app/i18n/app_hu.ts", "ts", "i18n"),
            FileMapping("app/i18n/app_hu.qm", "app/i18n/app_hu.qm", "qm", "i18n"),
            FileMapping("app/i18n/app_en.json", "app/i18n/app_en.json", "json", "i18n"),
            FileMapping("app/i18n/app_hu.json", "app/i18n/app_hu.json", "json", "i18n"),
            
            # APP MANAGERS MODULE (4)
            FileMapping("app/managers/__init__.py", "app/managers/__init__.py", "py", "managers"),
            FileMapping("app/managers/contact_db_manager.py", "app/managers/contact_db_manager.py", "py", "managers"),
            FileMapping("app/managers/nameday_reference_manager.py", "app/managers/nameday_reference_manager.py", "py", "managers"),
            FileMapping("app/managers/settings_manager.py", "app/managers/settings_manager.py", "py", "managers"),
            
            # APP SERVICES MODULE (4)
            FileMapping("app/services/__init__.py", "app/services/__init__.py", "py", "services"),
            FileMapping("app/services/data_validator.py", "app/services/data_validator.py", "py", "services"),
            FileMapping("app/services/email_service.py", "app/services/email_service.py", "py", "services"),
            FileMapping("app/services/windows_startup.py", "app/services/windows_startup.py", "py", "services"),
            
            # APP UI MODULE (8)
            FileMapping("app/ui/__init__.py", "app/ui/__init__.py", "py", "ui"),
            FileMapping("app/ui/database_editor_dialog.py", "app/ui/database_editor_dialog.py", "py", "ui"),
            FileMapping("app/ui/notification_modal.py", "app/ui/notification_modal.py", "py", "ui"),
            FileMapping("app/ui/query_dialog.py", "app/ui/query_dialog.py", "py", "ui"),
            FileMapping("app/ui/settings_dialog.py", "app/ui/settings_dialog.py", "py", "ui"),
            FileMapping("app/ui/system_tray.py", "app/ui/system_tray.py", "py", "ui"),
            FileMapping("app/ui/today_namedays_dialog.py", "app/ui/today_namedays_dialog.py", "py", "ui"),
            FileMapping("app/ui/add_edit_contact_dialog.py", "app/ui/add_edit_contact_dialog.py", "py", "ui"),
            
            # APP UTILS MODULE (5)
            FileMapping("app/utils/__init__.py", "app/utils/__init__.py", "py", "utils"),
            FileMapping("app/utils/date_utils.py", "app/utils/date_utils.py", "py", "utils"),
            FileMapping("app/utils/error_handler.py", "app/utils/error_handler.py", "py", "utils"),
            FileMapping("app/utils/file_utils.py", "app/utils/file_utils.py", "py", "utils"),
            FileMapping("app/utils/logger.py", "app/utils/logger.py", "py", "utils"),
            
            # RESOURCES (5)
            FileMapping("resources/namedays.csv", "resources/namedays.csv", "csv", "resources"),
            FileMapping("resources/app.ico", "resources/app.ico", "ico", "resources"),
            FileMapping("resources/app_icon.png", "resources/app_icon.png", "png", "resources"),
            FileMapping("resources/tray_icon.png", "resources/tray_icon.png", "png", "resources"),
            FileMapping("resources/settings.png", "resources/settings.png", "png", "resources"),
            FileMapping("resources/today.png", "resources/today.png", "png", "resources"),
            FileMapping("resources/reload.png", "resources/reload.png", "png", "resources"),
            FileMapping("resources/query.png", "resources/query.png", "png", "resources"),
            FileMapping("resources/exit.png", "resources/exit.png", "png", "resources"),
            FileMapping("resources/database.png", "resources/database.png", "png", "resources"),
            FileMapping("resources/styles/default.qss", "resources/styles/default.qss", "qss", "resources")
            
#            # SPECIAL FILES
#            FileMapping("app/app.pro", "app/app.pro", "pro", "app"),
        ]
        return mappings
    
    def _get_file_hash(self, file_path: Path) -> Optional[str]:
        """Calculate SHA256 hash of file."""
        if not file_path.exists():
            return None
        
        try:
            sha256 = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception as e:
            print(f"Error hashing {file_path}: {e}")
            return None
    
    def _file_matches(self, install_path: Path, source_path: Path) -> bool:
        """Check if install and source files match."""
        if not install_path.exists() or not source_path.exists():
            return False
        
        # For binary files, compare hashes
        if install_path.suffix in ['.ico', '.png', '.qm']:
            return self._get_file_hash(install_path) == self._get_file_hash(source_path)
        
        # For text files, compare content
        try:
            return install_path.read_text(encoding='utf-8') == source_path.read_text(encoding='utf-8')
        except:
            # Fallback to hash comparison for text files with encoding issues
            return self._get_file_hash(install_path) == self._get_file_hash(source_path)
    
    def list_files(self) -> None:
        """List all file associations."""
        print("\n" + "="*80)
        print("FILE ASSOCIATIONS - Install/ to Source Mapping")
        print("="*80 + "\n")
        
        # Group by module
        by_module = {}
        for mapping in self.file_mappings:
            if mapping.module not in by_module:
                by_module[mapping.module] = []
            by_module[mapping.module].append(mapping)
        
        # Sort and display
        for module in sorted(by_module.keys()):
            mappings = by_module[module]
            print(f"\n[{module.upper()}] - {len(mappings)} files")
            print("-" * 80)
            
            for mapping in sorted(mappings, key=lambda m: m.install_path):
                source_full = self.source_dir / mapping.source_path
                install_full = self.install_dir / mapping.install_path
                exists_source = "✓" if source_full.exists() else "✗"
                exists_install = "✓" if install_full.exists() else "✗"
                
                print(f"  [{mapping.file_type:4}] {exists_source} {exists_install} "
                      f"{mapping.install_path:45} <- {mapping.source_path}")
        
        print("\n" + "="*80)
        print(f"TOTAL: {len(self.file_mappings)} files")
        print("="*80 + "\n")
    
    def verify_files(self) -> Tuple[int, int, int]:
        """Verify if install/ files match source files."""
        print("\n" + "="*80)
        print("FILE VERIFICATION - Checking Install/ vs Source")
        print("="*80 + "\n")
        
        total = len(self.file_mappings)
        matched = 0
        missing = 0
        mismatched = 0
        
        for mapping in self.file_mappings:
            install_path = self.install_dir / mapping.install_path
            source_path = self.source_dir / mapping.source_path
            
            if not source_path.exists():
                print(f"✗ SOURCE MISSING: {mapping.source_path}")
                missing += 1
            elif not install_path.exists():
                print(f"⚠ INSTALL MISSING: {mapping.install_path}")
                missing += 1
            elif self._file_matches(install_path, source_path):
                print(f"✓ MATCH: {mapping.install_path}")
                matched += 1
            else:
                print(f"✗ MISMATCH: {mapping.install_path} != {mapping.source_path}")
                mismatched += 1
        
        print("\n" + "="*80)
        print(f"RESULTS: {matched} matched, {mismatched} mismatched, {missing} missing")
        print(f"COVERAGE: {matched}/{total} ({matched*100//total}%)")
        print("="*80 + "\n")
        
        return matched, mismatched, missing
    
    def sync_files(self) -> None:
        """Sync files from source to install/."""
        print("\n" + "="*80)
        print("FILE SYNC - Updating Install/ from Source")
        print("="*80 + "\n")
        
        copied = 0
        skipped = 0
        errors = 0
        
        for mapping in self.file_mappings:
            install_path = self.install_dir / mapping.install_path
            source_path = self.source_dir / mapping.source_path
            
            if not source_path.exists():
                print(f"✗ SKIP (source missing): {mapping.source_path}")
                skipped += 1
                continue
            
            # Create parent directories if needed
            install_path.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                # Only copy if files don't match
                if install_path.exists() and self._file_matches(install_path, source_path):
                    print(f"✓ SKIP (already matches): {mapping.install_path}")
                    skipped += 1
                else:
                    shutil.copy2(source_path, install_path)
                    print(f"✓ COPIED: {mapping.install_path}")
                    copied += 1
            except Exception as e:
                print(f"✗ ERROR: {mapping.install_path} - {e}")
                errors += 1
        
        print("\n" + "="*80)
        print(f"SYNC COMPLETE: {copied} copied, {skipped} skipped, {errors} errors")
        print("="*80 + "\n")
    
    def create_package(self, package_name: str = "NameDaysApp-Release") -> None:
        """Create release package from install/ directory."""
        print("\n" + "="*80)
        print("PACKAGE CREATION")
        print("="*80 + "\n")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        package_dir = self.source_dir / "releases" / f"{package_name}_{timestamp}"
        
        try:
            # Create package directory
            package_dir.mkdir(parents=True, exist_ok=True)
            print(f"Created package directory: {package_dir.relative_to(self.source_dir)}\n")
            
            # Copy install/ to package
            install_dest = package_dir / "install"
            if install_dest.exists():
                shutil.rmtree(install_dest)
            shutil.copytree(self.install_dir, install_dest)
            print(f"Copied install/ directory")
            
            # Create manifest
            manifest = {
                "name": package_name,
                "created": datetime.now().isoformat(),
                "files": len(self.file_mappings),
                "version": "1.0.0",
                "mappings": [asdict(m) for m in self.file_mappings]
            }
            
            manifest_path = package_dir / "MANIFEST.json"
            with open(manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2)
            print(f"Created manifest: MANIFEST.json")
            
            # Create README
            readme_path = package_dir / "PACKAGE_README.md"
            with open(readme_path, 'w') as f:
                f.write(f"""# {package_name} Release Package

Created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Version: 1.0.0

## Contents

This package contains the complete application files ready for distribution.

### File Structure
""")
            
            print(f"Created README: PACKAGE_README.md")
            
            # Create release package
            print(f"Created release package: {package_dir}")
            
        except Exception as e:
            print(f"✗ ERROR: {e}")
            raise
    
    def generate_report(self) -> None:
        """Generate detailed release report."""
        print("\n" + "=" * 80)
        print("RELEASE REPORT")
        print("=" * 80 + "\n")
        
        # Summary
        total_files = len(self.file_mappings)
        matched, mismatched, missing = self.verify_files()
        
        print("\nFILE STATISTICS:")
        print(f"  Total expected files: {total_files}")
        print(f"  Matched files:       {matched}")
        print(f"  Mismatched files:    {mismatched}")
        print(f"  Missing files:       {missing}")
        if total_files > 0:
            print(f"  Coverage:            {matched*100//total_files}%\n")
        else:
            print(f"  Coverage:            0%\n")
        
        # By module
        by_module = {}
        for mapping in self.file_mappings:
            if mapping.module not in by_module:
                by_module[mapping.module] = 0
            by_module[mapping.module] += 1
        
        print("BREAKDOWN BY MODULE:")
        for module in sorted(by_module.keys()):
            count = by_module[module]
            print(f"  {module:15} {count:3} files")
        
        print("\n" + "=" * 80 + "\n")


def main():
    """Main CLI interface."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1].lower()
    manager = ReleaseManager()
    
    if command == "list":
        manager.list_files()
    elif command == "verify":
        manager.verify_files()
    elif command == "sync":
        manager.sync_files()
    elif command == "package":
        pkg_name = sys.argv[2] if len(sys.argv) > 2 else "NameDaysApp-Release"
        manager.create_package(pkg_name)
    elif command == "report":
        manager.generate_report()
    elif command == "--help" or command == "-h":
        print(__doc__)
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
