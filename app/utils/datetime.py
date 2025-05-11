from datetime import datetime, timedelta, timezone
import re

def parse_datetime(dt_str: str) -> datetime:
    """
    Parse a datetime string in various formats
    
    Args:
        dt_str: Datetime string to parse
        
    Returns:
        Parsed datetime object
    """
    # Try various formats
    formats = [
        '%Y-%m-%dT%H:%M:%S%z',  # ISO 8601 with timezone
        '%Y-%m-%dT%H:%M:%S.%f%z',  # ISO 8601 with microseconds and timezone
        '%Y-%m-%dT%H:%M:%S',  # ISO 8601 without timezone
        '%Y-%m-%dT%H:%M:%S.%f',  # ISO 8601 with microseconds
        '%a, %d %b %Y %H:%M:%S %z',  # RFC 822/RFC 2822
        '%a, %d %b %Y %H:%M:%S',  # RFC 822/RFC 2822 without timezone
        '%Y-%m-%d %H:%M:%S',  # MySQL datetime format
        '%Y-%m-%d',  # Just date
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(dt_str, fmt)
            if dt.tzinfo is None:
                # Assume UTC if no timezone is specified
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue
    
    # Handle relative times like "2 hours ago"
    if 'ago' in dt_str:
        return parse_relative_time(dt_str)
    
    raise ValueError(f"Could not parse datetime string: {dt_str}")

def parse_relative_time(time_str: str) -> datetime:
    """
    Parse a relative time string like "2 hours ago"
    
    Args:
        time_str: Relative time string to parse
        
    Returns:
        Datetime object
    """
    now = datetime.now(timezone.utc)
    
    # Extract number and unit
    match = re.match(r'(\d+)\s+(\w+)(?:\s+ago)?', time_str)
    if not match:
        raise ValueError(f"Could not parse relative time: {time_str}")
    
    amount, unit = match.groups()
    amount = int(amount)
    
    # Handle different units
    if unit.startswith('second'):
        return now - timedelta(seconds=amount)
    elif unit.startswith('minute'):
        return now - timedelta(minutes=amount)
    elif unit.startswith('hour'):
        return now - timedelta(hours=amount)
    elif unit.startswith('day'):
        return now - timedelta(days=amount)
    elif unit.startswith('week'):
        return now - timedelta(days=amount * 7)
    elif unit.startswith('month'):
        return now - timedelta(days=amount * 30)  # Approximation
    elif unit.startswith('year'):
        return now - timedelta(days=amount * 365)  # Approximation
    
    raise ValueError(f"Unknown time unit: {unit}")

def format_datetime(dt: datetime, fmt: str = '%Y-%m-%d %H:%M:%S') -> str:
    """
    Format a datetime object as a string
    
    Args:
        dt: Datetime object to format
        fmt: Format string
        
    Returns:
        Formatted datetime string
    """
    return dt.strftime(fmt)

def get_relative_time(dt: datetime) -> str:
    """
    Get a relative time string like "2 hours ago" from a datetime object
    
    Args:
        dt: Datetime object
        
    Returns:
        Relative time string
    """
    now = datetime.now(timezone.utc)
    
    # Ensure dt has timezone info
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    diff = now - dt
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return f"{int(seconds)} seconds ago"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days > 1 else ''} ago"
    elif seconds < 2592000:
        weeks = int(seconds / 604800)
        return f"{weeks} week{'s' if weeks > 1 else ''} ago"
    elif seconds < 31536000:
        months = int(seconds / 2592000)
        return f"{months} month{'s' if months > 1 else ''} ago"
    else:
        years = int(seconds / 31536000)
        return f"{years} year{'s' if years > 1 else ''} ago" 