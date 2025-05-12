"""
Constants for the WhatsApp Chat Analyzer application.
"""
import os

# File paths
ARTIFACTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'artifacts')
STOPWORDS_PATH = os.path.join(ARTIFACTS_DIR, 'stop_hinglish.txt')

# Patterns for identifying media messages in WhatsApp chat
MEDIA_PATTERNS = [
    '<Media omitted>',
    'image omitted',
    'video omitted',
    'audio omitted',
    'GIF omitted',
    'sticker omitted',
    'document omitted',
    'Contact card omitted',
    'Poll omitted',
    'omitido>',  # Spanish
    'omitida>',  # Spanish
    'weggelaten>',  # Dutch
    'omesso>',  # Italian
    'omitido',  # Portuguese
    'ausgelassen',  # German
    'omis>',  # French
    '省略されました',  # Japanese
    '已省略',  # Chinese
    '생략됨'  # Korean
]

# Date format patterns for different WhatsApp versions and regions
DATE_FORMATS = [
    # Standard formats (12h)
    r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s[APap][Mm]\s-\s',  # MM/DD/YY, h:mm AM/PM -
    r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}:\d{2}\s[APap][Mm]\s-\s',  # MM/DD/YY, h:mm:ss AM/PM -
    # Standard formats (24h)
    r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s',  # MM/DD/YY, HH:mm -
    r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}:\d{2}\s-\s',  # MM/DD/YY, HH:mm:ss -
    # European formats
    r'\d{1,2}\.\d{1,2}\.\d{2,4},\s\d{1,2}:\d{2}\s-\s',  # DD.MM.YY, HH:mm -
    r'\d{1,2}\.\d{1,2}\.\d{2,4},\s\d{1,2}:\d{2}:\d{2}\s-\s',  # DD.MM.YY, HH:mm:ss -
    r'\d{1,2}-\d{1,2}-\d{2,4}\s\d{1,2}:\d{2}\s-\s',  # DD-MM-YY HH:mm -
    r'\d{1,2}-\d{1,2}-\d{2,4}\s\d{1,2}:\d{2}:\d{2}\s-\s',  # DD-MM-YY HH:mm:ss -
    # ISO-like formats
    r'\d{4}-\d{1,2}-\d{1,2},\s\d{1,2}:\d{2}\s-\s',  # YYYY-MM-DD, HH:mm -
    r'\d{4}-\d{1,2}-\d{1,2},\s\d{1,2}:\d{2}:\d{2}\s-\s',  # YYYY-MM-DD, HH:mm:ss -
    # With brackets around timestamp
    r'\[\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}:\d{2}\]\s',  # [MM/DD/YY, HH:mm:ss]
    r'\[\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\]\s',  # [MM/DD/YY, HH:mm]
]

# Group notification patterns
GROUP_NOTIFICATION_PATTERNS = [
    'added',
    'removed',
    'left',
    'joined',
    'created group',
    'changed the subject',
    'changed this group\'s icon',
    'changed the group description',
    'changed the group settings',
    'now an admin',
    'no longer an admin',
    'Messages and calls are end-to-end encrypted',
    'changed their phone number',
    'turned on disappearing messages',
    'turned off disappearing messages',
    'changed the message timer',
    'was added',
    'added you',
    'removed you',
    'You were added',
    'You added',
    'You removed',
    'You left',
    'This message was deleted',
    'You deleted this message',
    'The message was deleted',
    'changed the subject',
    'added to this group',
    'set the encryption',
    'invited you',
    'You joined via invite link'
]

# UI Configuration
THEME_COLORS = {
    'primary': '#1E88E5',  # Primary blue color
    'secondary': '#FF5722',  # Accent orange color
    'background': '#f0f2f6',  # Light background
    'text': '#424242',  # Dark text color
    'light_text': '#757575'  # Light text color
}

# Chart configuration
CHART_CONFIG = {
    'height': 500,
    'width': 800,
    'colorscale': 'Blues',
    'bar_colors': ['#1E88E5', '#42A5F5', '#90CAF9', '#BBDEFB'],
    'line_color': '#1E88E5',
    'sentiment_colors': {
        'positive': '#4CAF50',
        'neutral': '#FFC107',
        'negative': '#F44336'
    }
}

# Time periods for labeling
DAY_PERIODS = {
    0: 'Late Night',
    1: 'Late Night',
    2: 'Late Night',
    3: 'Late Night',
    4: 'Early Morning',
    5: 'Early Morning',
    6: 'Early Morning',
    7: 'Morning',
    8: 'Morning',
    9: 'Morning',
    10: 'Late Morning',
    11: 'Late Morning',
    12: 'Noon',
    13: 'Afternoon',
    14: 'Afternoon',
    15: 'Afternoon',
    16: 'Evening',
    17: 'Evening',
    18: 'Evening',
    19: 'Night',
    20: 'Night',
    21: 'Night',
    22: 'Late Night',
    23: 'Late Night'
}

# Day names (for sorting)
WEEKDAYS = [
    'Monday',
    'Tuesday',
    'Wednesday',
    'Thursday',
    'Friday',
    'Saturday',
    'Sunday'
]

# Month names (for sorting)
MONTHS = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December'
]

# Default text for no data available
NO_DATA_TEXT = "No data available for this selection."