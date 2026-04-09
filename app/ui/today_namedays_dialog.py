from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton
)
from PyQt5.QtGui import QFont, QIcon
from pathlib import Path
from datetime import datetime

from app.utils import get_logger
from app.constants import RESOURCES_DIR

logger = get_logger(__name__)


class TodayNamedaysDialog(QDialog):
    """Display today's namedays dialog [REQ-0012, REQ-0012a, REQ-0012b]."""
    
    def __init__(self, contact_db, nameday_ref, parent=None):
        super().__init__(parent)
        self.contact_db = contact_db
        self.nameday_ref = nameday_ref
        
        self.setWindowTitle(self.tr("Today's Namedays"))
        
        # Load and set today's namedays icon [REQ-0012]
        icon_path = RESOURCES_DIR / "today.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        self.setGeometry(100, 100, 500, 400)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup UI components [REQ-0012, REQ-0012a, REQ-0012b]."""
        layout = QVBoxLayout()
        
        # Title [REQ-0012]
        title = QLabel(self.tr("Today's Namedays 🎂"))
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # TODAY'S DATE [REQ-0012a]
        today_date = datetime.now().strftime("%m-%d")
        date_label = QLabel(self.tr(f"Date: {today_date}"))
        date_font = QFont()
        date_font.setPointSize(11)
        date_label.setFont(date_font)
        layout.addWidget(date_label)
        
        # List of today's namedays from reference database [REQ-0012b]
        self.namedays_list = QListWidget()
        
        try:
            # Get all namesakes from reference database for today [REQ-0012b]
            today_names = self.nameday_ref.get_names_for_date(today_date)
            
            if today_names:
                for name in today_names:
                    item = QListWidgetItem(name)
                    self.namedays_list.addItem(item)
                logger.info(f"Loaded {len(today_names)} celebrable names for {today_date} [REQ-0012b]")
            else:
                self.namedays_list.addItem(self.tr("No namedays today"))
                logger.info(f"No celebrable names found for {today_date}")
        except Exception as e:
            logger.error(f"Error loading nameday reference data: {e}")
            self.namedays_list.addItem(self.tr("Error loading namedays"))   
        
        layout.addWidget(self.namedays_list)
        
        # Close button
        close_btn = QPushButton(self.tr("Close"))   
        close_btn.clicked.connect(self.accept)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)