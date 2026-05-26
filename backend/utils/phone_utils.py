import re

def format_indian_phone_number(number):
    """
    Normalize Indian mobile numbers for Twilio calls (E.164 format).
    Accepts 10-digit numbers, numbers with a leading zero,
    or numbers already prefixed with country code +91 or 91.
    Returns format: +919876543210
    """
    digits = re.sub(r'\D', '', str(number))
    if digits.startswith('0'):
        digits = digits[1:]
    if digits.startswith('91') and len(digits) == 12:
        return f'+{digits}'
    if len(digits) == 10:
        return f'+91{digits}'
    raise ValueError("Invalid Indian mobile number. Provide a 10-digit Indian number.")

def format_indian_whatsapp_number(number):
    """
    Normalize Indian mobile numbers for WhatsApp messaging.
    Returns format: whatsapp:+919876543210
    """
    phone = format_indian_phone_number(number)
    return f'whatsapp:{phone}'