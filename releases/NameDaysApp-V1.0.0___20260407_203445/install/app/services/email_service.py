"""
Email service for Gmail integration [REQ-0007, REQ-0016, REQ-0019, REQ-0020, REQ-0052].

Sends emails via Gmail SMTP integration with template support.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional

from app.utils import get_logger
from app.exceptions import EmailException, AuthenticationException
from app.constants import GMAIL_SMTP_SERVER, GMAIL_SMTP_PORT, EMAIL_SEND_TIMEOUT

logger = get_logger(__name__)


class EmailService:
    """
    Send emails via Gmail SMTP integration [REQ-0007, REQ-0016, REQ-0052].
    
    Handles Gmail authentication and email sending with support for templates [REQ-0020].
    Only sends on explicit user action [REQ-0019].
    """
    
    def __init__(self, gmail_account: str = "", gmail_password: str = ""):
        """
        Initialize email service with Gmail credentials [REQ-0016].
        
        Args:
            gmail_account: Gmail account email address
            gmail_password: Gmail account password or app token
        """
        self.gmail_account = gmail_account
        self.gmail_password = gmail_password
        self._authenticated = False
    
    def authenticate(self, email: str, password: str) -> bool:
        """
        Authenticate with Gmail account [REQ-0016, REQ-0052].
        
        Verifies credentials by establishing SMTP connection.
        
        Args:
            email: Gmail account email
            password: Gmail password or app token
        
        Returns:
            True if authenticated successfully, False otherwise
        
        Raises:
            AuthenticationException: If authentication fails
        """
        try:
            self.gmail_account = email
            self.gmail_password = password
            
            # Test connection
            server = smtplib.SMTP(GMAIL_SMTP_SERVER, GMAIL_SMTP_PORT, timeout=EMAIL_SEND_TIMEOUT)
            server.starttls()
            server.login(email, password)
            server.quit()
            
            self._authenticated = True
            logger.info(f"Successfully authenticated with Gmail account: {email}")
            return True
        except smtplib.SMTPAuthenticationError as e:
            self._authenticated = False
            logger.error(f"Gmail authentication failed: {e}")
            raise AuthenticationException(f"Failed to authenticate with Gmail: {e}", "Gmail") from e
        except Exception as e:
            self._authenticated = False
            logger.error(f"Gmail connection failed: {e}")
            raise AuthenticationException(f"Failed to connect to Gmail SMTP: {e}", "Gmail") from e
    
    def send_email(
        self,
        to_addresses: List[str],
        subject: str,
        body: str,
        template: Optional[str] = None
    ) -> bool:
        """
        Send email to recipients [REQ-0007, REQ-0016, REQ-0019, REQ-0020, REQ-0052].
        
        Sends email via Gmail SMTP [REQ-0052].
        Only called on explicit Mail button click [REQ-0019].
        Applies prewritten template if provided [REQ-0020].
        Handles failures gracefully [REQ-0027].
        
        Args:
            to_addresses: List of recipient email addresses
            subject: Email subject line
            body: Email body text
            template: Optional prewritten email template to apply [REQ-0020]
        
        Returns:
            True if sent successfully, False otherwise
        
        Raises:
            EmailException: If email sending fails
        """
        try:
            # Validate credentials are available
            if not self.gmail_account or not self.gmail_password:
                raise EmailException("Gmail account credentials not configured", ", ".join(to_addresses))
            
            # Filter out invalid addresses
            valid_addresses = [addr for addr in to_addresses if addr and "@" in addr]
            if not valid_addresses:
                raise EmailException("No valid recipient email addresses provided")
            
            # Apply template if provided [REQ-0020]
            email_body = body
            if template:
                email_body = self._apply_template(template, body)
            
            # Create message
            message = MIMEMultipart()
            message["From"] = self.gmail_account
            message["To"] = ";".join(valid_addresses)
            message["Subject"] = subject
            message.attach(MIMEText(email_body, "plain", "utf-8"))
            
            # Send via SMTP [REQ-0052]
            return self._send_smtp(valid_addresses, subject, email_body)
        
        except EmailException:
            raise
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            raise EmailException(f"Failed to send email: {e}", ", ".join(to_addresses)) from e
    
    def send_to_contact(
        self,
        email_addresses: List[str],
        contact_name: str,
        prewritten_template: Optional[str] = None
    ) -> bool:
        """
        Send email to a contact [REQ-0007, REQ-0019, REQ-0020].
        
        Args:
            email_addresses: List of recipient addresses
            contact_name: Contact name for subject line
            prewritten_template: Contact's prewritten template [REQ-0020]
        
        Returns:
            True if sent successfully
        """
        subject = f"Nameday Greeting - {contact_name}"
        body = f"My best wishes on your nameday, {contact_name}!"
        
        return self.send_email(email_addresses, subject, body, prewritten_template)
    
    def validate_email_address(self, email: str) -> bool:
        """
        Validate email address format [REQ-0040].
        
        Args:
            email: Email address to validate
        
        Returns:
            True if valid format, False otherwise
        """
        from app.services.data_validator import DataValidator
        validator = DataValidator()
        return validator.validate_email(email)
    
    def is_authenticated(self) -> bool:
        """
        Check if service is authenticated with Gmail.
        
        Returns:
            True if authenticated, False otherwise
        """
        return self._authenticated
    
    def _apply_template(self, template: str, default_body: str) -> str:
        """
        Apply prewritten email template [REQ-0020].
        
        Substitutes template variables:
        - {body}: Default body text
        - {greeting}: Standard greeting
        
        Args:
            template: Template string
            default_body: Default body text
        
        Returns:
            Rendered email body
        """
        if not template:
            return default_body
        
        # Simple template substitution
        rendered = template.replace("{body}", default_body)
        rendered = rendered.replace("{greeting}", "Dear Friend,")
        
        return rendered
    
    def _send_smtp(
        self,
        to_addresses: List[str],
        subject: str,
        body: str
    ) -> bool:
        """
        Send email via SMTP [REQ-0052].
        
        Private method that handles low-level SMTP communication.
        
        Args:
            to_addresses: Recipient addresses
            subject: Email subject
            body: Email body
        
        Returns:
            True if successful
        
        Raises:
            EmailException: If SMTP operation fails
        """
        try:
            # Connect to Gmail SMTP
            server = smtplib.SMTP(GMAIL_SMTP_SERVER, GMAIL_SMTP_PORT, timeout=EMAIL_SEND_TIMEOUT)
            server.starttls()
            server.login(self.gmail_account, self.gmail_password)
            
            # Create message
            message = MIMEText(body, "plain", "utf-8")
            message["From"] = self.gmail_account
            message["To"] = ";".join(to_addresses)
            message["Subject"] = subject
            
            # Send
            server.send_message(message)
            server.quit()
            
            logger.info(f"Email sent to {len(to_addresses)} recipient(s): {subject}")
            return True
        
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error sending email: {e}")
            raise EmailException(f"SMTP error: {e}", ", ".join(to_addresses)) from e
        except Exception as e:
            logger.error(f"Error sending email via SMTP: {e}")
            raise EmailException(f"Failed to send email: {e}", ", ".join(to_addresses)) from e
