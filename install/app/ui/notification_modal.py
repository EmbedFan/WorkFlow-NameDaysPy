"""
Notification modal dialog [REQ-0005, REQ-0043, REQ-0044].

Displays nameday notifications with action buttons.
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from app.types import Notification, Contact
from app.utils import get_logger
from app.constants import (
    NOTIFICATION_MODAL_WIDTH, NOTIFICATION_MODAL_HEIGHT,
    NOTIFICATION_MODAL_ALWAYS_ON_TOP, NOTIFICATION_MODAL_BLOCKING,
    BUTTON_LATER, BUTTON_MAIL, BUTTON_DONE
)

logger = get_logger(__name__)


class NotificationModal(QDialog):
    """
    Notification modal dialog [REQ-0005, REQ-0043, REQ-0044].
    
    Displays nameday notification with contact information.
    Modal is focused and blocking [REQ-0005].
    Three action buttons: Later [REQ-0006], Mail [REQ-0007], Done [REQ-0008].
    """
    
    # Signals for actions
    later_clicked = pyqtSignal(object)  # Notification
    mail_clicked = pyqtSignal(object)   # Contact
    done_clicked = pyqtSignal(object)   # Contact
    
    def __init__(self, notification: Notification, parent=None):
        """
        Initialize notification modal [REQ-0005, REQ-0043, REQ-0044].
        
        Args:
            notification: Notification to display
            parent: Parent widget
        """
        super().__init__(parent)
        self.notification = notification
        self.contact = notification.contact
        
        # Set modal properties [REQ-0005, REQ-0043, REQ-0044]
        self.setWindowTitle(f"Nameday: {self.contact.name}")
        self.setModal(NOTIFICATION_MODAL_BLOCKING)
        self.setGeometry(100, 100, NOTIFICATION_MODAL_WIDTH, NOTIFICATION_MODAL_HEIGHT)
        
        # Always on top [REQ-0005]
        if NOTIFICATION_MODAL_ALWAYS_ON_TOP:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout()
        
        # Contact name (title)
        name_label = QLabel(f"🎂 {self.contact.name}")
        name_font = QFont()
        name_font.setPointSize(16)
        name_font.setBold(True)
        name_label.setFont(name_font)
        layout.addWidget(name_label)
        
        # Recipient info
        recipient_label = QLabel(f"Recipient: {self.contact.recipient}")
        layout.addWidget(recipient_label)
        
        # Nameday date
        date_label = QLabel(f"Nameday: {self.notification.nameday_date}")
        layout.addWidget(date_label)
        
        # Comment if available
        if self.contact.comment:
            comment_label = QLabel(f"Note: {self.contact.comment}")
            layout.addWidget(comment_label)
        
        # Add spacer
        layout.addStretch()
        
        # Action buttons [REQ-0044]
        button_layout = QHBoxLayout()
        
        # Later button [REQ-0006]
        later_btn = QPushButton(BUTTON_LATER)
        later_btn.clicked.connect(self._on_later)
        button_layout.addWidget(later_btn)
        
        # Mail button [REQ-0007]
        mail_btn = QPushButton(BUTTON_MAIL)
        mail_btn.clicked.connect(self._on_mail)
        button_layout.addWidget(mail_btn)
        
        # Done button [REQ-0008]
        done_btn = QPushButton(BUTTON_DONE)
        done_btn.clicked.connect(self._on_done)
        button_layout.addWidget(done_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def _on_later(self):
        """Handle Later button click [REQ-0006]."""
        logger.info(f"Later button clicked for {self.contact.name}")
        self.later_clicked.emit(self.notification)
        self.accept()
    
    def _on_mail(self):
        """Handle Mail button click [REQ-0007]."""
        logger.info(f"Mail button clicked for {self.contact.name}")
        self.mail_clicked.emit(self.contact)
        self.accept()
    
    def _on_done(self):
        """Handle Done button click [REQ-0008]."""
        logger.info(f"Done button clicked for {self.contact.name}")
        self.done_clicked.emit(self.contact)
        self.accept()
