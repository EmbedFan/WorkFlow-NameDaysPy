from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem
)
from PyQt5.QtGui import QIcon
from pathlib import Path

from app.utils import get_logger
from app.constants import RESOURCES_DIR

logger = get_logger(__name__)


class QueryDialog(QDialog):
    """Query/search contacts dialog."""
    
    def __init__(self, contact_db, parent=None):
        super().__init__(parent)
        self.contact_db = contact_db
        
        self.setWindowTitle(self.tr("Search Contacts"))
        
        # Load and set query icon [REQ-0040]
        icon_path = RESOURCES_DIR / "query.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        self.setGeometry(100, 100, 400, 400)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout()
        
        # Search input
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel(self.tr("Search:")))
        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self._on_search)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Results list
        self.results_list = QListWidget()
        layout.addWidget(self.results_list)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def _on_search(self):
        """Perform search - clear results when query is empty [REQ-0064]."""
        query = self.search_input.text().lower()
        logger.info(f"Searching for: {query}")
        
        self.results_list.clear()
        
        # If query is empty, don't search - show empty list [REQ-0064]
        if not query:
            logger.debug("Search query is empty, clearing results [REQ-0064]")
            return
        
        contacts = self.contact_db.read_contacts()
        
        for contact in contacts:
            if query in contact.name.lower() or query in contact.recipient.lower():
                item = QListWidgetItem(f"{contact.name} ({contact.recipient})")
                self.results_list.addItem(item)