"""
Time Utilities - Timezone-aware datetime handling for Clinic Cancellation Chatbot

This module provides helpers for consistent UTC storage and Central Time display.
All database timestamps must be stored in UTC. Display conversions happen at the app layer.

Author: Jonathan Ives (@dollythedog)
"""

from datetime import datetime, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

# Constants
TZ_UTC = ZoneInfo("UTC")
TZ_LOCAL = ZoneInfo("America/Chicago")  # Central Time

def now_utc() -> datetime:
    """
    Get current time in UTC with timezone awareness.
    
    Returns:
        datetime: Current UTC time with timezone info
    
    Example:
        >>> now = now_utc()
        >>> print(now.tzinfo)
        UTC
    """
    return datetime.now(tz=TZ_UTC)


def now_local() -> datetime:
    """
    Get current time in America/Chicago (Central Time) with timezone awareness.
    
    Returns:
        datetime: Current Central time with timezone info
    """
    return datetime.now(tz=TZ_LOCAL)


def to_utc(dt: datetime) -> datetime:
    """
    Convert a datetime to UTC.
    
    Args:
        dt: Datetime to convert (naive or aware)
        
    Returns:
        datetime: UTC datetime with timezone info
        
    Raises:
        ValueError: If datetime is naive (no timezone info)
        
    Example:
        >>> local_time = datetime(2025, 11, 1, 14, 0, tzinfo=TZ_LOCAL)
        >>> utc_time = to_utc(local_time)
        >>> print(utc_time.hour)
        19  # 2pm CT = 7pm UTC
    """
    if dt.tzinfo is None:
        raise ValueError("Cannot convert naive datetime to UTC. Use make_aware() first.")
    return dt.astimezone(TZ_UTC)


def to_local(dt: datetime) -> datetime:
    """
    Convert a datetime to America/Chicago (Central Time).
    
    Args:
        dt: Datetime to convert (naive or aware)
        
    Returns:
        datetime: Central time datetime with timezone info
        
    Raises:
        ValueError: If datetime is naive (no timezone info)
        
    Example:
        >>> utc_time = datetime(2025, 11, 1, 19, 0, tzinfo=TZ_UTC)
        >>> local_time = to_local(utc_time)
        >>> print(local_time.hour)
        14  # 7pm UTC = 2pm CT
    """
    if dt.tzinfo is None:
        raise ValueError("Cannot convert naive datetime to local. Use make_aware() first.")
    return dt.astimezone(TZ_LOCAL)


def make_aware(dt: datetime, tz: Optional[ZoneInfo] = None) -> datetime:
    """
    Add timezone info to a naive datetime.
    
    Args:
        dt: Naive datetime (no timezone)
        tz: Timezone to apply (default: America/Chicago)
        
    Returns:
        datetime: Timezone-aware datetime
        
    Example:
        >>> naive = datetime(2025, 11, 1, 14, 0)
        >>> aware = make_aware(naive)
        >>> print(aware.tzinfo)
        America/Chicago
    """
    if dt.tzinfo is not None:
        return dt  # Already aware
    
    target_tz = tz or TZ_LOCAL
    return dt.replace(tzinfo=target_tz)


def format_for_sms(dt: datetime, include_date: bool = True) -> str:
    """
    Format datetime for SMS display in Central Time.
    
    Args:
        dt: Datetime to format (UTC or aware)
        include_date: Whether to include the date (default: True)
        
    Returns:
        str: Human-readable time string
        
    Example:
        >>> utc_time = datetime(2025, 11, 1, 19, 0, tzinfo=TZ_UTC)
        >>> format_for_sms(utc_time)
        'Nov 1 at 2:00 PM CT'
        >>> format_for_sms(utc_time, include_date=False)
        '2:00 PM CT'
    """
    local_time = to_local(dt) if dt.tzinfo else make_aware(dt)
    
    if include_date:
        return local_time.strftime("%b %d at %I:%M %p CT")
    else:
        return local_time.strftime("%I:%M %p CT")


def is_within_contact_hours(
    dt: Optional[datetime] = None,
    start_hour: int = 8,
    end_hour: int = 20
) -> bool:
    """
    Check if a time is within acceptable contact hours (Central Time).
    
    Args:
        dt: Datetime to check (default: now)
        start_hour: Start of contact window (0-23, default: 8am)
        end_hour: End of contact window (0-23, default: 8pm)
        
    Returns:
        bool: True if within contact hours
        
    Example:
        >>> morning = datetime(2025, 11, 1, 9, 0, tzinfo=TZ_LOCAL)
        >>> is_within_contact_hours(morning)
        True
        >>> night = datetime(2025, 11, 1, 22, 0, tzinfo=TZ_LOCAL)
        >>> is_within_contact_hours(night)
        False
    """
    check_time = dt or now_local()
    local_time = to_local(check_time) if check_time.tzinfo else make_aware(check_time)
    
    hour = local_time.hour
    return start_hour <= hour < end_hour


def add_minutes(dt: datetime, minutes: int) -> datetime:
    """
    Add minutes to a datetime while preserving timezone.
    
    Args:
        dt: Base datetime
        minutes: Minutes to add (can be negative)
        
    Returns:
        datetime: New datetime with same timezone
        
    Example:
        >>> start = now_utc()
        >>> later = add_minutes(start, 7)
        >>> (later - start).total_seconds()
        420.0  # 7 minutes
    """
    return dt + timedelta(minutes=minutes)


def time_until(target: datetime, from_time: Optional[datetime] = None) -> timedelta:
    """
    Calculate time remaining until a target datetime.
    
    Args:
        target: Target datetime
        from_time: Starting time (default: now)
        
    Returns:
        timedelta: Time remaining (negative if target is in past)
        
    Example:
        >>> future = now_utc() + timedelta(hours=1)
        >>> remaining = time_until(future)
        >>> remaining.total_seconds() > 3500  # ~1 hour
        True
    """
    start = from_time or now_utc()
    return target - start


def minutes_until(target: datetime, from_time: Optional[datetime] = None) -> float:
    """
    Calculate minutes remaining until a target datetime.
    
    Args:
        target: Target datetime
        from_time: Starting time (default: now)
        
    Returns:
        float: Minutes remaining (negative if target is in past)
        
    Example:
        >>> future = now_utc() + timedelta(minutes=30)
        >>> minutes_until(future)
        30.0
    """
    delta = time_until(target, from_time)
    return delta.total_seconds() / 60


def format_timedelta(td: timedelta, short: bool = False) -> str:
    """
    Format a timedelta for human display.
    
    Args:
        td: Timedelta to format
        short: Use short format (default: False)
        
    Returns:
        str: Human-readable string
        
    Example:
        >>> delta = timedelta(minutes=7, seconds=30)
        >>> format_timedelta(delta)
        '7 minutes'
        >>> format_timedelta(delta, short=True)
        '7m'
    """
    total_seconds = int(td.total_seconds())
    
    if total_seconds < 60:
        return f"{total_seconds}s" if short else f"{total_seconds} seconds"
    
    minutes = total_seconds // 60
    if minutes < 60:
        return f"{minutes}m" if short else f"{minutes} minute{'s' if minutes != 1 else ''}"
    
    hours = minutes // 60
    remaining_minutes = minutes % 60
    
    if short:
        return f"{hours}h{remaining_minutes}m" if remaining_minutes else f"{hours}h"
    
    hour_str = f"{hours} hour{'s' if hours != 1 else ''}"
    if remaining_minutes:
        min_str = f"{remaining_minutes} minute{'s' if remaining_minutes != 1 else ''}"
        return f"{hour_str}, {min_str}"
    return hour_str


def parse_time_string(time_str: str) -> datetime:
    """
    Parse a time string in various formats to Central Time datetime.
    
    Args:
        time_str: Time string (e.g., "2:00 PM", "14:00", "10:30am")
        
    Returns:
        datetime: Today's date at the specified time (Central Time)
        
    Raises:
        ValueError: If time string cannot be parsed
        
    Example:
        >>> dt = parse_time_string("2:00 PM")
        >>> dt.hour
        14
    """
    time_str = time_str.strip().upper()
    
    # Try common formats
    formats = [
        "%I:%M %p",  # 2:00 PM
        "%I:%M%p",   # 2:00PM
        "%H:%M",     # 14:00
    ]
    
    for fmt in formats:
        try:
            parsed = datetime.strptime(time_str, fmt)
            today = now_local().replace(
                hour=parsed.hour,
                minute=parsed.minute,
                second=0,
                microsecond=0
            )
            return today
        except ValueError:
            continue
    
    raise ValueError(f"Could not parse time string: {time_str}")


# Convenience aliases
utc_now = now_utc
local_now = now_local
