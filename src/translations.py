
TRANSLATIONS = {
    'en': {
        # Landing page
        'title': 'Find Sports Buddies!',
        'subtitle': 'Interested in connecting with others for sports activities?<br>We want to build an App for this!',
        'yes_button': 'Yes, I\'m interested! 🔥',
        'no_button': 'Probably not',
        'location_id': 'Location ID:',
        
        # Thank you page
        'thank_you_title': 'Thanks!',
        'thank_you_message': 'Your interest has been recorded. We\'ll use this to connect you with other sports enthusiasts in your area!',
        'email_placeholder': 'Enter your email to stay updated',
        'get_updates': 'Get updates'
    },
    'nl': {
        # Landing page
        'title': 'Vind Sportmaatjes!',
        'subtitle': 'Geïnteresseerd in contact met anderen voor sportactiviteiten?<br>We willen hier een App voor bouwen!',
        'yes_button': 'Ja, ik ben geïnteresseerd! 🔥',
        'no_button': 'Waarschijnlijk niet',
        'location_id': 'Locatie ID:',
        
        # Thank you page
        'thank_you_title': 'Bedankt!',
        'thank_you_message': 'Je interesse is geregistreerd. We gebruiken dit om je te verbinden met andere sportliefhebbers in jouw buurt!',
        'email_placeholder': 'Vul je e-mail in om updates te ontvangen',
        'get_updates': 'Ontvang updates'
    }
}

def get_text(lang, key):
    """Get translated text for a given language and key"""
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)

def is_valid_lang(lang):
    """Check if language code is supported."""
    return lang in TRANSLATIONS

def get_default_lang():
    """Return default language."""
    return 'en'
