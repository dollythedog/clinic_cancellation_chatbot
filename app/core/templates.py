"""
SMS Templates - Message templates for patient communication

This module provides templated SMS messages that comply with HIPAA.
No PHI (Protected Health Information) is included in SMS bodies.

All times are displayed in Central Time (America/Chicago).

Author: Jonathan Ives (@dollythedog)
"""

from datetime import datetime
from typing import Optional

from utils.time_utils import format_for_sms


def format_initial_offer(
    slot_time: datetime,
    location: str,
    hold_minutes: int = 7
) -> str:
    """
    Format an initial offer message for a cancellation slot.
    
    Args:
        slot_time: Appointment slot start time (UTC aware)
        location: Clinic location name
        hold_minutes: Minutes until offer expires
        
    Returns:
        str: Formatted SMS message
        
    Example:
        >>> from datetime import datetime, timezone
        >>> slot = datetime(2025, 11, 1, 19, 0, tzinfo=timezone.utc)  # 2pm CT
        >>> msg = format_initial_offer(slot, "Main Clinic", 7)
        >>> print(msg)
        TPCCC: An earlier appointment opened Nov 1 at 2:00 PM CT at Main Clinic. Reply YES to claim or NO to skip. This offer expires in 7 min.
    """
    time_str = format_for_sms(slot_time, include_date=True)
    
    return (
        f"TPCCC: An earlier appointment opened {time_str} at {location}. "
        f"Reply YES to claim or NO to skip. This offer expires in {hold_minutes} min."
    )


def format_acceptance_winner(
    slot_time: datetime,
    location: str
) -> str:
    """
    Format confirmation message for patient who successfully claimed slot.
    
    Args:
        slot_time: Appointment slot start time (UTC aware)
        location: Clinic location name
        
    Returns:
        str: Formatted SMS message
        
    Example:
        >>> slot = datetime(2025, 11, 1, 19, 0, tzinfo=timezone.utc)
        >>> msg = format_acceptance_winner(slot, "Main Clinic")
        >>> print(msg)
        TPCCC: Confirmed. You're scheduled Nov 1 at 2:00 PM CT at Main Clinic. Reply STOP to opt out of future messages.
    """
    time_str = format_for_sms(slot_time, include_date=True)
    
    return (
        f"TPCCC: Confirmed. You're scheduled {time_str} at {location}. "
        f"Reply STOP to opt out of future messages."
    )


def format_acceptance_too_late() -> str:
    """
    Format message for patient who accepted after slot was already claimed.
    
    Returns:
        str: Formatted SMS message
        
    Example:
        >>> msg = format_acceptance_too_late()
        >>> print(msg)
        TPCCC: Thanks—this slot has been taken. We'll keep you on the list for the next opening.
    """
    return (
        "TPCCC: Thanks—this slot has been taken. "
        "We'll keep you on the list for the next opening."
    )


def format_decline_response() -> str:
    """
    Format message acknowledging patient declined the offer.
    
    Returns:
        str: Formatted SMS message
        
    Example:
        >>> msg = format_decline_response()
        >>> print(msg)
        TPCCC: No problem—we'll keep you on the list for future openings.
    """
    return "TPCCC: No problem—we'll keep you on the list for future openings."


def format_help_response() -> str:
    """
    Format automatic response to HELP keyword.
    
    Returns:
        str: Formatted SMS message
        
    Example:
        >>> msg = format_help_response()
        >>> print(msg)
        HELP: TPCCC scheduling. Reply YES to claim slots; NO to skip.
    """
    return "HELP: TPCCC scheduling. Reply YES to claim slots; NO to skip."


def format_stop_response() -> str:
    """
    Format automatic response to STOP keyword (opt-out).
    
    Returns:
        str: Formatted SMS message
        
    Example:
        >>> msg = format_stop_response()
        >>> print(msg)
        You'll no longer receive earlier-slot messages from TPCCC.
    """
    return "You'll no longer receive earlier-slot messages from TPCCC."


def format_cancellation_notification(offer_id: int) -> str:
    """
    Format message notifying patient their pending offer was canceled (slot filled by another).
    
    Args:
        offer_id: ID of the canceled offer
        
    Returns:
        str: Formatted SMS message
        
    Example:
        >>> msg = format_cancellation_notification(123)
        >>> print(msg)
        TPCCC: The slot you were offered has been filled. We'll notify you of the next opening.
    """
    return (
        "TPCCC: The slot you were offered has been filled. "
        "We'll notify you of the next opening."
    )


def format_error_response() -> str:
    """
    Format generic error response for unrecognized messages.
    
    Returns:
        str: Formatted SMS message
        
    Example:
        >>> msg = format_error_response()
        >>> print(msg)
        TPCCC: Please reply YES or NO to appointment offers. Reply HELP for info or STOP to opt out.
    """
    return (
        "TPCCC: Please reply YES or NO to appointment offers. "
        "Reply HELP for info or STOP to opt out."
    )


def parse_patient_response(message_body: str) -> Optional[str]:
    """
    Parse patient SMS response into a normalized action.
    
    Args:
        message_body: Raw SMS body text
        
    Returns:
        str: Normalized action ("YES", "NO", "STOP", "HELP", or None)
        
    Example:
        >>> parse_patient_response("yes!")
        'YES'
        >>> parse_patient_response("No thanks")
        'NO'
        >>> parse_patient_response("Random text")
        None
        >>> parse_patient_response("STOP")
        'STOP'
    """
    body = message_body.strip().upper()
    
    # YES variations
    if any(keyword in body for keyword in ["YES", "Y", "YEAH", "YEP", "OK", "OKAY", "SURE", "ACCEPT"]):
        return "YES"
    
    # NO variations
    if any(keyword in body for keyword in ["NO", "N", "NOPE", "NAH", "DECLINE", "SKIP", "PASS"]):
        return "NO"
    
    # STOP variations (TCPA compliance)
    if any(keyword in body for keyword in ["STOP", "UNSUBSCRIBE", "CANCEL", "END", "QUIT", "REMOVE"]):
        return "STOP"
    
    # HELP variations
    if any(keyword in body for keyword in ["HELP", "INFO", "?"]):
        return "HELP"
    
    return None


# Character count helper for Twilio pricing
def get_sms_segment_count(message: str) -> int:
    """
    Calculate the number of SMS segments required for a message.
    
    SMS segments:
    - GSM-7 encoding: 160 chars per segment (or 153 for multi-part)
    - Unicode: 70 chars per segment (or 67 for multi-part)
    
    Args:
        message: SMS message body
        
    Returns:
        int: Number of SMS segments
        
    Example:
        >>> msg = "Short message"
        >>> get_sms_segment_count(msg)
        1
        >>> long_msg = "x" * 200
        >>> get_sms_segment_count(long_msg)
        2
    """
    length = len(message)
    
    # Check if message contains non-GSM characters
    contains_unicode = not all(ord(c) < 128 for c in message)
    
    if contains_unicode:
        # Unicode (UCS-2) encoding
        if length <= 70:
            return 1
        return (length + 66) // 67
    else:
        # GSM-7 encoding
        if length <= 160:
            return 1
        return (length + 152) // 153
