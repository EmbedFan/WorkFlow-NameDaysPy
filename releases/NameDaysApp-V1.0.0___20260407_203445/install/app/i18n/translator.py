"""
Translation/Localization manager [REQ-0045, REQ-0046].

Handles loading and switching between language translations using Qt .qm files.
"""

from pathlib import Path
from PyQt5.QtCore import QTranslator, QCoreApplication, PYQT_VERSION_STR
from app.utils import get_logger

logger = get_logger(__name__)

TRANSLATIONS_DIR = Path(__file__).parent
TRANSLATION_FILES = {
    "en": "app_en",
    "hu": "app_hu"
}


def load_translator(language: str = "en") -> QTranslator:
    """
    Load and install translator for specified language [REQ-0046].
    
    Args:
        language: Language code ("en" or "hu")
    
    Returns:
        Loaded QTranslator instance
    """
    # Get translation filename
    ts_filename = TRANSLATION_FILES.get(language, "app_en")
    qm_path = TRANSLATIONS_DIR / f"{ts_filename}.qm"
    
    logger.debug(f"Translator: Looking for {language} translation file at {qm_path}")
    logger.info(f"PyQt version: {PYQT_VERSION_STR}")
    
    # Check if file exists
    if not qm_path.exists():
        logger.warning(f"Translation file not found: {qm_path}")
        logger.info(f"Using default language (English)")
        return QTranslator()  # Return empty translator (falls back to English)
    
    # Verify file size
    file_size = qm_path.stat().st_size
    logger.debug(f"Translator: {ts_filename}.qm file size: {file_size} bytes")
    
    if file_size < 50:
        logger.error(f"Translation file is too small (corrupt): {qm_path} ({file_size} bytes)")
        return QTranslator()
    
    # Load translator
    translator = QTranslator()
    translation_loaded = translator.load(str(qm_path))
    
    if translation_loaded:
        logger.info(f"✓ Loaded translation: {language} from {qm_path} ({file_size} bytes)")
        return translator
    else:
        logger.error(f"✗ Failed to load translation: {language} from {qm_path}")
        logger.error(f"  File exists: {qm_path.exists()}, size: {file_size} bytes")
        return QTranslator()


def install_translator(app: QCoreApplication, language: str = "en") -> None:
    """
    Install translator to application [REQ-0046].
    
    Args:
        app: QApplication instance
        language: Language code ("en" or "hu")
    """
    translator = load_translator(language)

    # 🔴 KEEP REFERENCE
    app._translator = translator  

    if not app.installTranslator(translator) :
        logger.error(f"Failed to install translator for language: {language}")
    else:
        logger.info(f"Translator installed: {language} [REQ-0046]")


def switch_language(app: QCoreApplication, language: str) -> None:
    """
    Switch application language at runtime [REQ-0045].
    
    Uninstalls old translator and installs new one for specified language.
    
    Args:
        app: QApplication instance
        language: Language code ("en" or "hu")
    """
    # Remove old translators
    for translator in app.findChildren(QTranslator):
        app.removeTranslator(translator)
    
    # Install new translator
    install_translator(app, language)
    logger.info(f"Language switched to: {language}")