TRANSLATIONS = {
    'en': {
        # Landing page
        'title': 'Find Sports Buddies!',
        'subtitle': 'Interested in connecting with others for sports activities?<br>We want to build an App for this!',
        'yes_button': 'Yes, I\'m interested! 🔥',
        'no_button': 'Probably not',
        'location_id': 'Location ID:',
        
        # Sports selection page
        'sports_title': 'Which sports are you interested in?',
        'sports_subtitle': 'Select all that apply - we\'ll help you find buddies for these activities!',
        'sports_other_label': 'Optional: Other sport(s):',
        'sports_other_placeholder': 'Enter any other sport you\'re interested in',
        'sports_continue_button': 'Continue',
        'sports_list': {
            'running': 'Running / Jogging',
            'cycling': 'Cycling',
            'basketball': 'Basketball',
            'volleyball': 'Volleyball',
            'calisthenics': 'Calisthenics',
            'table_tennis': 'Table Tennis',
            'chess': 'Chess',
            'inline_skating': 'Inline Skating',
        },
        
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
        
        # Sports selection page
        'sports_title': 'Welke sporten interesseren je?',
        'sports_subtitle': 'Selecteer alles wat van toepassing is - we helpen je maatjes te vinden voor deze activiteiten!',
        'sports_other_label': 'Optioneel: Andere sport(en):',
        'sports_other_placeholder': 'Je kunt een andere sport aangeven',
        'sports_continue_button': 'Doorgaan',
        'sports_list': {
            'running': 'Hardlopen / Joggen',
            'cycling': 'Fietsen',
            'basketball': 'Basketbal',
            'volleyball': 'Volleybal',
            'calisthenics': 'Calisthenics',
            'table_tennis': 'Tafeltennis',
            'chess': 'Schaken',
            'inline_skating': 'Inline skaten',


        },
        
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

def get_sports_list(lang):
    """Get the sports list for a given language"""
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get('sports_list', {})

def is_valid_lang(lang):
    """Check if language code is supported."""
    return lang in TRANSLATIONS

def get_default_lang():
    """Return default language."""
    return 'en'