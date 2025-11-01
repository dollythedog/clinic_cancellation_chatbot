"""
Twilio Client - Wrapper for Twilio SMS API

This module provides a clean interface for sending SMS messages via Twilio.
Supports both real Twilio API and mock mode for testing.

Author: Jonathan Ives (@dollythedog)
"""

import logging
from typing import Optional
import requests

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from app.infra.settings import settings

logger = logging.getLogger(__name__)


class TwilioClient:
    """
    Wrapper for Twilio SMS API.
    
    Handles SMS sending with proper error handling and logging.
    Can be configured to use mock mode for testing.
    """
    
    def __init__(self, use_mock: bool = False):
        """
        Initialize Twilio client.
        
        Args:
            use_mock: Use mock client for testing (default: False)
        """
        self.use_mock = use_mock or settings.USE_MOCK_TWILIO
        
        if not self.use_mock:
            self.client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
            self.from_number = settings.TWILIO_PHONE_NUMBER
            self.messaging_service_sid = settings.TWILIO_MESSAGING_SERVICE_SID
        else:
            logger.info("Using mock Twilio client (no real SMS will be sent)")
            self.client = None
            self.from_number = "+15555551234"  # Mock number
            self.messaging_service_sid = None
    
    def send_sms(
        self,
        to: str,
        body: str,
        status_callback: Optional[str] = None
    ) -> Optional[str]:
        """
        Send an SMS message.
        
        Args:
            to: Recipient phone number (E.164 format: +12145551234)
            body: Message body text
            status_callback: Optional webhook URL for delivery status
            
        Returns:
            str: Twilio message SID, or None if failed
            
        Raises:
            TwilioRestException: If Twilio API call fails
            
        Example:
            >>> client = TwilioClient()
            >>> sid = client.send_sms(
            ...     to="+12145551234",
            ...     body="TPCCC: Your appointment is confirmed.",
            ...     status_callback="https://example.com/status"
            ... )
            >>> print(f"Message sent: {sid}")
        """
        if self.use_mock:
            # Mock mode - log and optionally send to ntfy.sh
            logger.info(f"[MOCK] SMS to {to}: {body}")
            
            # Send notification to webhook (e.g., ntfy.sh) if configured
            if hasattr(settings, 'SLACK_WEBHOOK_URL') and settings.SLACK_WEBHOOK_URL:
                self._send_mock_notification(to, body)
            
            return f"SM{to[-10:]}_mock"
        
        if not settings.ENABLE_SMS_SENDING:
            logger.warning(f"SMS sending disabled. Would send to {to}: {body}")
            return None
        
        try:
            # Build message parameters
            message_params = {
                "body": body,
                "to": to,
            }
            
            # Use Messaging Service SID if configured, otherwise use from_number
            if self.messaging_service_sid:
                message_params["messaging_service_sid"] = self.messaging_service_sid
            else:
                message_params["from_"] = self.from_number
            
            # Add status callback if provided
            if status_callback:
                message_params["status_callback"] = status_callback
            
            # Send message
            message = self.client.messages.create(**message_params)
            
            logger.info(
                f"SMS sent successfully. SID: {message.sid}, To: {to}, "
                f"Status: {message.status}"
            )
            
            return message.sid
            
        except TwilioRestException as e:
            logger.error(
                f"Twilio API error sending SMS to {to}. "
                f"Error code: {e.code}, Message: {e.msg}"
            )
            raise
        except Exception as e:
            logger.error(f"Unexpected error sending SMS to {to}: {e}")
            raise
    
    def get_message_status(self, message_sid: str) -> Optional[dict]:
        """
        Retrieve the status of a sent message.
        
        Args:
            message_sid: Twilio message SID
            
        Returns:
            dict: Message details (status, error_code, etc.) or None if not found
            
        Example:
            >>> client = TwilioClient()
            >>> status = client.get_message_status("SM1234567890")
            >>> print(status["status"])  # delivered, failed, etc.
        """
        if self.use_mock:
            logger.info(f"[MOCK] Get status for {message_sid}")
            return {
                "sid": message_sid,
                "status": "delivered",
                "error_code": None,
                "error_message": None,
            }
        
        try:
            message = self.client.messages(message_sid).fetch()
            
            return {
                "sid": message.sid,
                "status": message.status,
                "error_code": message.error_code,
                "error_message": message.error_message,
                "date_sent": message.date_sent,
                "date_updated": message.date_updated,
            }
            
        except TwilioRestException as e:
            logger.error(f"Error fetching message {message_sid}: {e.msg}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching message {message_sid}: {e}")
            return None
    
    def validate_phone_number(self, phone: str) -> bool:
        """
        Validate that a phone number is in E.164 format.
        
        Args:
            phone: Phone number string
            
        Returns:
            bool: True if valid E.164 format
            
        Example:
            >>> client = TwilioClient()
            >>> client.validate_phone_number("+12145551234")
            True
            >>> client.validate_phone_number("214-555-1234")
            False
        """
        import re
        
        # E.164 format: +[country code][number]
        # US: +1XXXXXXXXXX (11 digits total after +)
        pattern = r'^\+[1-9]\d{10,14}$'
        
        return bool(re.match(pattern, phone))
    
    def format_phone_to_e164(self, phone: str, country_code: str = "+1") -> str:
        """
        Convert a phone number to E.164 format.
        
        Args:
            phone: Phone number (various formats accepted)
            country_code: Country code (default: +1 for US)
            
        Returns:
            str: Phone number in E.164 format
            
        Example:
            >>> client = TwilioClient()
            >>> client.format_phone_to_e164("(214) 555-1234")
            '+12145551234'
            >>> client.format_phone_to_e164("214-555-1234")
            '+12145551234'
        """
        import re
        
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', phone)
        
        # If starts with country code (e.g., 1 for US), use as-is
        if digits.startswith('1') and len(digits) == 11:
            return f"+{digits}"
        
        # Otherwise prepend country code
        if len(digits) == 10:  # US number without country code
            return f"{country_code}{digits}"
        
        # If already has +, return as-is
        if phone.startswith('+'):
            return phone
        
        raise ValueError(f"Cannot format phone number to E.164: {phone}")
    
    def _send_mock_notification(self, to: str, body: str) -> None:
        """
        Send mock SMS notification to webhook (e.g., ntfy.sh).
        
        Args:
            to: Recipient phone number
            body: Message body
        """
        try:
            webhook_url = settings.SLACK_WEBHOOK_URL
            
            # Format notification message
            notification = f"📱 Mock SMS to {to}\n\n{body}"
            
            # Send to ntfy.sh (simple POST with message as body)
            response = requests.post(
                webhook_url,
                data=notification.encode('utf-8'),
                headers={
                    "Title": "TPCCC Mock SMS",
                    "Priority": "default",
                    "Tags": "speech_balloon"
                },
                timeout=5
            )
            
            if response.status_code == 200:
                logger.debug(f"Sent mock SMS notification to {webhook_url}")
            else:
                logger.warning(
                    f"Failed to send notification: {response.status_code} {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"Could not send mock notification: {e}")
        except Exception as e:
            logger.error(f"Unexpected error sending mock notification: {e}")


# Global Twilio client instance
twilio_client = TwilioClient()
